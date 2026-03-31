// WebSocket service for real-time factory updates
// Handles connection management, reconnection logic, and message routing

export type WebSocketMessageType = 
  | 'PIPELINE_UPDATE'
  | 'AGENT_STATUS'
  | 'WORKFLOW_STEP'
  | 'SYSTEM_METRIC'
  | 'LOG_ENTRY'
  | 'FACTORY_RESET'
  | 'CONNECTION_STATUS';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  payload: unknown;
  timestamp: Date;
}

export interface PipelineUpdatePayload {
  phaseId: string;
  phaseIndex: number;
  progress: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface AgentStatusPayload {
  agentId: string;
  status: 'idle' | 'busy' | 'offline' | 'error';
  taskId?: string;
  progress?: number;
}

export interface WorkflowStepPayload {
  stepId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  progress?: number;
  output?: Record<string, unknown>;
}

export interface SystemMetricPayload {
  metric: 'cpu' | 'memory' | 'storage';
  value: number;
}

export interface LogEntryPayload {
  level: 'debug' | 'info' | 'warn' | 'error' | 'success';
  source: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ConnectionStatusPayload {
  connected: boolean;
  latency?: number;
  reconnectAttempts?: number;
}

export type WebSocketPayload = 
  | PipelineUpdatePayload
  | AgentStatusPayload
  | WorkflowStepPayload
  | SystemMetricPayload
  | LogEntryPayload
  | ConnectionStatusPayload;

// Backend sends these raw message types over /ws/global
type BackendMessageType = 'connected' | 'pong' | 'subscribed' | 'status' | 'logs' | 'error';

interface BackendMessage {
  type: BackendMessageType | string;
  payload?: unknown;
}

class FactoryWebSocketService {
  private ws: WebSocket | null = null;
  private baseUrl: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private listeners: Map<WebSocketMessageType, Set<(payload: unknown) => void>> = new Map();
  private connectionListeners: Set<(connected: boolean) => void> = new Set();

  constructor(url?: string) {
    // /ws/global is the actual backend endpoint; NEXT_PUBLIC_WEBSOCKET_URL can override
    this.baseUrl = url || process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws/global';
  }

  private buildUrl(): string {
    // Append JWT token as query param — backend requires ?token= for WebSocket auth
    if (typeof window === 'undefined') return this.baseUrl;
    const token = localStorage.getItem('aifactory_token');
    return token ? `${this.baseUrl}?token=${encodeURIComponent(token)}` : this.baseUrl;
  }

  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.warn('WebSocket already connected');
      return;
    }

    try {
      const url = this.buildUrl();
      console.log(`Connecting to WebSocket: ${this.baseUrl}`);
      this.ws = new WebSocket(url);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.reconnectAttempts = 0;
  }

  public subscribe<T extends WebSocketPayload>(
    messageType: WebSocketMessageType,
    callback: (payload: T) => void
  ): () => void {
    if (!this.listeners.has(messageType)) {
      this.listeners.set(messageType, new Set());
    }

    const listeners = this.listeners.get(messageType)!;
    listeners.add(callback as (payload: unknown) => void);

    // Return unsubscribe function
    return () => {
      listeners.delete(callback as (payload: unknown) => void);
      if (listeners.size === 0) {
        this.listeners.delete(messageType);
      }
    };
  }

  public subscribeConnection(callback: (connected: boolean) => void): () => void {
    this.connectionListeners.add(callback);
    return () => {
      this.connectionListeners.delete(callback);
    };
  }

  public sendMessage(type: WebSocketMessageType, payload: unknown): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, message not sent:', type);
      return;
    }

    const message: WebSocketMessage = {
      type,
      payload,
      timestamp: new Date()
    };

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
    }
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private handleOpen(): void {
    console.log('WebSocket connected successfully');
    this.reconnectAttempts = 0;

    // Start heartbeat to keep connection alive
    this.startHeartbeat();

    // Notify connection listeners
    this.connectionListeners.forEach(listener => listener(true));

    // Subscribe to all relevant topics on the global channel
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        payload: { topics: ['pipeline', 'agents', 'workflows', 'deployments', 'logs'] },
      }));
    }
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const raw: BackendMessage = JSON.parse(event.data);

      // Map backend message types to frontend WebSocketMessageType equivalents
      let frontendType: WebSocketMessageType | null = null;
      let payload = raw.payload ?? raw;

      switch (raw.type) {
        case 'connected':
          // Backend confirmed connection; notify connection listeners
          this.connectionListeners.forEach(l => l(true));
          frontendType = 'CONNECTION_STATUS';
          payload = { connected: true, latency: 0 } as ConnectionStatusPayload;
          break;
        case 'status':
          // Project/workflow status update → treat as pipeline update
          frontendType = 'PIPELINE_UPDATE';
          break;
        case 'logs':
          // Workflow log batch → treat as log entry
          frontendType = 'LOG_ENTRY';
          break;
        case 'pong':
          // Keep-alive response; no dispatch needed
          return;
        case 'subscribed':
          // Subscription confirmed; no dispatch needed
          return;
        case 'error':
          console.error('WebSocket server error:', (raw.payload as Record<string, unknown>)?.message ?? raw.payload);
          return;
        case 'CONNECTION_STATUS':
          // Legacy/self-originated message — handle normally
          frontendType = 'CONNECTION_STATUS';
          break;
        default:
          // Forward any other types that happen to match frontend types directly
          if (['PIPELINE_UPDATE','AGENT_STATUS','WORKFLOW_STEP','SYSTEM_METRIC','LOG_ENTRY','FACTORY_RESET'].includes(raw.type)) {
            frontendType = raw.type as WebSocketMessageType;
          } else {
            return;
          }
      }

      // Dispatch to registered listeners
      const listeners = this.listeners.get(frontendType);
      if (listeners) {
        listeners.forEach(listener => {
          try {
            listener(payload);
          } catch (error) {
            console.error(`Error in WebSocket listener for ${frontendType}:`, error);
          }
        });
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    
    // Stop heartbeat
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    // Notify connection listeners
    this.connectionListeners.forEach(listener => listener(false));
    
    // Schedule reconnection if not intentionally closed
    if (event.code !== 1000) { // 1000 = Normal closure
      this.scheduleReconnect();
    }
  }

  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    
    // Notify connection listeners of disconnection
    this.connectionListeners.forEach(listener => listener(false));
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        // Backend expects a "ping" text frame to keep the connection alive
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // 30 seconds
  }

  // Factory-specific helper methods
  public sendPipelineUpdate(update: PipelineUpdatePayload): void {
    this.sendMessage('PIPELINE_UPDATE', update);
  }

  public sendAgentStatus(status: AgentStatusPayload): void {
    this.sendMessage('AGENT_STATUS', status);
  }

  public sendWorkflowStep(step: WorkflowStepPayload): void {
    this.sendMessage('WORKFLOW_STEP', step);
  }

  public sendSystemMetric(metric: SystemMetricPayload): void {
    this.sendMessage('SYSTEM_METRIC', metric);
  }

  public sendLogEntry(log: LogEntryPayload): void {
    this.sendMessage('LOG_ENTRY', log);
  }

  public sendFactoryReset(): void {
    this.sendMessage('FACTORY_RESET', {});
  }
}

// Singleton instance
export const factoryWebSocket = new FactoryWebSocketService();