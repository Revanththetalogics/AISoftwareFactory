import type { Project, Agent, Workflow, Deployment } from '@/lib/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

class ApiClient {
  private baseUrl: string;
  private wsUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.wsUrl = WS_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Projects
  async getProjects() {
    return this.request<Project[]>('/projects');
  }

  async getProject(id: string) {
    return this.request<Project>(`/projects/${id}`);
  }

  async createProject(data: { name: string; description: string; requirements?: string }) {
    return this.request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProject(id: string, data: Partial<Project>) {
    return this.request<Project>(`/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteProject(id: string) {
    return this.request<void>(`/projects/${id}`, {
      method: 'DELETE',
    });
  }

  async activateProject(id: string) {
    return this.request<Project>(`/projects/${id}/activate`, {
      method: 'POST',
    });
  }

  // Workflows
  async executeWorkflow(data: { project_id: string; phase?: string }) {
    return this.request<Workflow>('/workflows/execute', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getWorkflows() {
    return this.request<Workflow[]>('/workflows');
  }

  async getWorkflow(id: string) {
    return this.request<Workflow>(`/workflows/${id}`);
  }

  async cancelWorkflow(id: string) {
    return this.request<Workflow>(`/workflows/${id}/cancel`, {
      method: 'POST',
    });
  }

  // Agents
  async getAgents() {
    return this.request<Agent[]>('/agents');
  }

  async getAgent(id: string) {
    return this.request<Agent>(`/agents/${id}`);
  }

  async assignTask(agentId: string, data: { task_type: string; description: string }) {
    return this.request<Agent>(`/agents/${agentId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Deployments
  async getDeployments() {
    return this.request<Deployment[]>('/deployments');
  }

  async createDeployment(data: { project_id: string; environment: string; version: string }) {
    return this.request<Deployment>('/deployments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDeployment(id: string) {
    return this.request<Deployment>(`/deployments/${id}`);
  }

  // Health
  async getHealth() {
    return this.request<{ status: string; version: string }>('/health');
  }

  // WebSocket
  connectWebSocket(channel: string, id?: string): WebSocket {
    const url = id ? `${this.wsUrl}/${channel}/${id}` : `${this.wsUrl}/${channel}`;
    return new WebSocket(url);
  }
}

export const api = new ApiClient();
