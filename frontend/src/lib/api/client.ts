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
    return this.request<any[]>('/projects');
  }

  async getProject(id: string) {
    return this.request<any>(`/projects/${id}`);
  }

  async createProject(data: { name: string; description: string; requirements?: string }) {
    return this.request<any>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProject(id: string, data: Partial<any>) {
    return this.request<any>(`/projects/${id}`, {
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
    return this.request<any>(`/projects/${id}/activate`, {
      method: 'POST',
    });
  }

  // Workflows
  async executeWorkflow(data: { project_id: string; phase?: string }) {
    return this.request<any>('/workflows/execute', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getWorkflows() {
    return this.request<any[]>('/workflows');
  }

  async getWorkflow(id: string) {
    return this.request<any>(`/workflows/${id}`);
  }

  async cancelWorkflow(id: string) {
    return this.request<any>(`/workflows/${id}/cancel`, {
      method: 'POST',
    });
  }

  // Agents
  async getAgents() {
    return this.request<any[]>('/agents');
  }

  async getAgent(id: string) {
    return this.request<any>(`/agents/${id}`);
  }

  async assignTask(agentId: string, data: { task_type: string; description: string }) {
    return this.request<any>(`/agents/${agentId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Deployments
  async getDeployments() {
    return this.request<any[]>('/deployments');
  }

  async createDeployment(data: { project_id: string; environment: string; version: string }) {
    return this.request<any>('/deployments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDeployment(id: string) {
    return this.request<any>(`/deployments/${id}`);
  }

  // Health
  async getHealth() {
    return this.request<any>('/health');
  }

  // WebSocket
  connectWebSocket(channel: string, id?: string): WebSocket {
    const url = id ? `${this.wsUrl}/${channel}/${id}` : `${this.wsUrl}/${channel}`;
    return new WebSocket(url);
  }
}

export const api = new ApiClient();
