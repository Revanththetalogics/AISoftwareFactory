import type {
  Project, Agent, Workflow, Deployment,
  User, LoginRequest, LoginResponse, RegisterRequest,
} from '@/lib/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

// Request configuration
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second initial delay

// CSRF configuration — matches backend csrf_middleware.py
const CSRF_COOKIE_NAME = 'csrf_token';
const CSRF_HEADER_NAME = 'X-CSRF-Token';
const CSRF_PROTECTED_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

/**
 * Read the CSRF token from the browser cookie set by the backend on any GET response.
 * The cookie is NOT httpOnly so JavaScript can read it (Double Submit Cookie pattern).
 */
function getCsrfTokenFromCookie(): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie
    .split(';')
    .map(c => c.trim())
    .find(c => c.startsWith(`${CSRF_COOKIE_NAME}=`));
  return match ? match.split('=')[1] : null;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private baseUrl: string;
  private wsUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.wsUrl = WS_BASE_URL;
    // Initialize token from localStorage on construction
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('aifactory_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('aifactory_token', token);
      } else {
        localStorage.removeItem('aifactory_token');
      }
    }
  }

  private async requestWithTimeout(
    url: string,
    options: RequestInit,
    timeout: number = DEFAULT_TIMEOUT
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408, 'TIMEOUT');
      }
      throw error;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount: number = 0
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    };

    // Add authorization header if token exists
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    // Add CSRF token for state-changing requests (Double Submit Cookie pattern).
    // The backend bypasses CSRF when a Bearer token is present, but we send it
    // regardless so cookie-auth sessions also work correctly.
    if (CSRF_PROTECTED_METHODS.has(options.method?.toUpperCase() ?? '')) {
      const csrfToken = getCsrfTokenFromCookie();
      if (csrfToken) {
        headers[CSRF_HEADER_NAME] = csrfToken;
      }
    }

    try {
      const response = await this.requestWithTimeout(url, {
        ...options,
        headers,
        credentials: 'include', // Include httpOnly cookies in requests
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));

        // Handle authentication errors
        if (response.status === 401) {
          this.token = null;
          if (typeof window !== 'undefined') {
            localStorage.removeItem('aifactory_token');
            window.dispatchEvent(new CustomEvent('auth:unauthorized'));
            window.location.href = '/login';
          }
          throw new ApiError('Authentication required', 401, 'UNAUTHORIZED');
        }

        throw new ApiError(
          errorData.detail || `HTTP ${response.status}`,
          response.status,
          errorData.code
        );
      }

      return response.json();
    } catch (error) {
      // Retry logic for network errors or 5xx server errors
      if (retryCount < MAX_RETRIES) {
        const shouldRetry = error instanceof ApiError
          ? error.status >= 500 || error.code === 'TIMEOUT'
          : true;

        if (shouldRetry) {
          const delay = RETRY_DELAY * Math.pow(2, retryCount);
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.request<T>(endpoint, options, retryCount + 1);
        }
      }

      throw error;
    }
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

  async quickstartProject(data: { idea: string; template?: string; tech_stack?: Record<string, unknown> }) {
    return this.request<{ project_id: string; workflow_id: string; message: string; status: string }>('/projects/quickstart', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Workflows
  async executeWorkflow(data: { project_id: string; phase?: string; async_execution?: boolean }) {
    return this.request<Workflow>('/workflows/execute', {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        async_execution: data.async_execution ?? true,
      }),
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

  // Authentication
  async login(data: LoginRequest) {
    const response = await this.request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(response.access_token);
    return response;
  }

  async logout() {
    // Call backend to clear httpOnly cookies
    await this.request<{ message: string }>('/auth/logout', {
      method: 'POST',
    });
    this.setToken(null);
  }

  async register(data: RegisterRequest) {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCurrentUser() {
    return this.request<User>('/auth/me');
  }

  // Workflow Phases
  async getAvailablePhases() {
    return this.request<string[]>('/workflows/phases/available');
  }

  // Agent Roles
  async getAvailableRoles() {
    return this.request<string[]>('/agents/roles/available');
  }

  // Dynamic Agent/Crew Management
  async createAgent(data: {
    name: string;
    role: string;
    goal: string;
    backstory: string;
    llm_task_type?: string;
    allow_delegation?: boolean;
  }) {
    return this.request<{
      agent_id: string;
      name: string;
      role: string;
      llm_model: string;
      message: string;
    }>('/agent-management/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCustomAgents() {
    return this.request<Array<{
      agent_id: string;
      name: string;
      role: string;
      llm_model: string;
      message: string;
    }>>('/agent-management/agents');
  }

  async deleteAgent(agentId: string) {
    return this.request<void>(`/agent-management/agents/${agentId}`, {
      method: 'DELETE',
    });
  }

  async createCrew(data: {
    name: string;
    description: string;
    agent_ids: string[];
    process?: 'sequential' | 'hierarchical' | 'parallel';
  }) {
    return this.request<{
      crew_id: string;
      name: string;
      agent_count: number;
      message: string;
    }>('/agent-management/crews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCustomCrews() {
    return this.request<Array<{
      crew_id: string;
      name: string;
      agent_count: number;
      message: string;
    }>>('/agent-management/crews');
  }

  async deleteCrew(crewId: string) {
    return this.request<void>(`/agent-management/crews/${crewId}`, {
      method: 'DELETE',
    });
  }

  async getLLMModels() {
    return this.request<{
      models: Array<{
        id: string;
        name: string;
        task_types: string[];
        description: string;
        context_window: number;
      }>;
    }>('/agent-management/llm-models');
  }

  // Deployment Environments
  async getAvailableEnvironments() {
    return this.request<string[]>('/deployments/environments/available');
  }

  // Cancel Deployment
  async cancelDeployment(id: string) {
    return this.request<Deployment>(`/deployments/${id}/cancel`, {
      method: 'POST',
    });
  }

  // WebSocket
  connectWebSocket(channel: string, id?: string): WebSocket {
    const url = id ? `${this.wsUrl}/${channel}/${id}` : `${this.wsUrl}/${channel}`;
    // Add token to WebSocket URL if available
    if (this.token) {
      const separator = url.includes('?') ? '&' : '?';
      return new WebSocket(`${url}${separator}token=${this.token}`);
    }
    return new WebSocket(url);
  }
}

export const api = new ApiClient();
