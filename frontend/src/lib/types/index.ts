export interface Project {
  id: string;
  name: string;
  description: string;
  requirements?: string;
  status: 'draft' | 'active' | 'paused' | 'completed' | 'failed';
  tech_stack?: Record<string, unknown>;
  current_phase?: string;
  progress_percent: number;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

export interface Agent {
  agent_id: string;
  name: string;
  role: string;
  capabilities: string[];
  status: 'idle' | 'running' | 'busy' | 'error';
  current_task?: string;
  last_active?: string;
  metadata?: Record<string, unknown>;
}

export interface Workflow {
  workflow_id: string;
  project_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_phase?: string;
  progress_percent: number;
  steps_completed: number;
  steps_total: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  logs: string[];
}

export interface Deployment {
  deployment_id: string;
  project_id: string;
  environment: 'dev' | 'staging' | 'production';
  version: string;
  status: 'pending' | 'running' | 'success' | 'failed' | 'rolled_back';
  steps: DeploymentStep[];
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  url?: string;
}

export interface DeploymentStep {
  name: string;
  status: string;
  message?: string;
  started_at?: string;
  completed_at?: string;
}

export interface Simulation {
  id: string;
  name: string;
  type: 'ux' | 'architecture' | 'api' | 'infrastructure';
  status: 'pending' | 'running' | 'passed' | 'failed';
  issues: number;
  warnings: number;
  approved: boolean;
  report?: string;
  completed_at?: string;
}

export interface SystemStatus {
  active_agents: number;
  running_projects: number;
  system_health: 'healthy' | 'degraded' | 'unhealthy';
  llm_status: 'connected' | 'disconnected' | 'error';
}

export interface AgentActivity {
  id: string;
  agent_name: string;
  agent_role: string;
  action: string;
  target: string;
  timestamp: string;
  status: 'in_progress' | 'completed' | 'failed';
}

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export type Theme = 'dark' | 'light' | 'system';
