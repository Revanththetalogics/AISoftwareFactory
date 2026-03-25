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

class FactoryWebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private listeners: Map<WebSocketMessageType, Set<(payload: unknown) => void>> = new Map();
  private connectionListeners: Set<(connected: boolean) => void> = new Set();

  constructor(url?: string) {
    // Use environment variable or default to localhost
    this.url = url || process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws/factory';
  }

  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.warn('WebSocket already connected');
      return;
    }

    try {
      console.log(`Connecting to WebSocket: ${this.url}`);
      this.ws = new WebSocket(this.url);
      
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
    
    // Send connection established message
    this.sendMessage('CONNECTION_STATUS', {
      connected: true,
      latency: 0
    } as ConnectionStatusPayload);
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Handle special system messages
      if (message.type === 'CONNECTION_STATUS') {
        const payload = message.payload as ConnectionStatusPayload;
        this.connectionListeners.forEach(listener => listener(payload.connected));
      }
      
      // Route to appropriate listeners
      const listeners = this.listeners.get(message.type);
      if (listeners) {
        listeners.forEach(listener => {
          try {
            listener(message.payload);
          } catch (error) {
            console.error(`Error in WebSocket listener for ${message.type}:`, error);
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
        // Send ping message to keep connection alive
        this.sendMessage('CONNECTION_STATUS', {
          connected: true
        } as ConnectionStatusPayload);
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