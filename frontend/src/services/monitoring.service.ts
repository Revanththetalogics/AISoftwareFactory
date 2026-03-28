// Real-time monitoring service for system metrics and infrastructure status
// Connects to backend WebSocket for live metrics streaming

export type MonitorEventType = 
  | 'metric_update'
  | 'alert_triggered'
  | 'service_status_change'
  | 'cluster_topology_change'
  | 'performance_degradation';

export interface MonitorEvent {
  event_type: MonitorEventType;
  timestamp: string;
  data: Record<string, unknown>;
  severity: 'info' | 'warning' | 'error' | 'critical';
}

export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_bytes_sent: number;
  network_bytes_recv: number;
  timestamp: string;
}

export interface ApplicationMetrics {
  requests_per_second: number;
  average_response_time_ms: number;
  error_rate: number;
  active_connections: number;
  queue_depth: number;
  timestamp: string;
}

export interface BusinessMetrics {
  projects_count: number;
  code_generations_today: number;
  simulations_run_today: number;
  deployments_successful: number;
  timestamp: string;
}

export interface ClusterStatus {
  nodes_active: number;
  nodes_total: number;
  leader_node: string;
  cluster_health: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
}

export interface AlertInfo {
  name: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  triggered_at: string;
  resolved: boolean;
  resolved_at?: string;
}

class MonitoringService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private listeners: Map<MonitorEventType, Set<(event: MonitorEvent) => void>> = new Map();
  private connectionListeners: Set<(connected: boolean) => void> = new Set();
  private clientId: string;

  // Current metrics state
  public systemMetrics: SystemMetrics | null = null;
  public applicationMetrics: ApplicationMetrics | null = null;
  public businessMetrics: BusinessMetrics | null = null;
  public clusterStatus: ClusterStatus | null = null;
  public activeAlerts: AlertInfo[] = [];

  constructor(url?: string) {
    // Generate unique client ID
    this.clientId = `frontend-${Math.random().toString(36).substr(2, 9)}`;
    
    // Use environment variable or default to localhost
    this.url = url || process.env.NEXT_PUBLIC_MONITORING_WS_URL || 'ws://localhost:8000/api/v1/realtime/monitor';
  }

  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.warn('Monitoring WebSocket already connected');
      return;
    }

    try {
      console.log(`Connecting to monitoring WebSocket: ${this.url}`);
      this.ws = new WebSocket(`${this.url}?client_id=${this.clientId}`);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('Failed to create monitoring WebSocket connection:', error);
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

  public subscribe(
    eventType: MonitorEventType,
    callback: (event: MonitorEvent) => void
  ): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }

    const listeners = this.listeners.get(eventType)!;
    listeners.add(callback);

    // Return unsubscribe function
    return () => {
      listeners.delete(callback);
      if (listeners.size === 0) {
        this.listeners.delete(eventType);
      }
    };
  }

  public subscribeConnection(callback: (connected: boolean) => void): () => void {
    this.connectionListeners.add(callback);
    return () => {
      this.connectionListeners.delete(callback);
    };
  }

  public sendMessage(type: string, payload: unknown): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('Monitoring WebSocket not connected, message not sent:', type);
      return;
    }

    try {
      this.ws.send(JSON.stringify({ type, payload }));
    } catch (error) {
      console.error('Failed to send monitoring WebSocket message:', error);
    }
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public subscribeToMetrics(
    callback: (metrics: {
      system?: SystemMetrics | null;
      application?: ApplicationMetrics | null;
      business?: BusinessMetrics | null;
      cluster?: ClusterStatus | null;
    }) => void
  ): () => void {
    return this.subscribe('metric_update', (event) => {
      const data = event.data;
      
      if (data.system) {
        this.systemMetrics = data.system as SystemMetrics;
      }
      if (data.application) {
        this.applicationMetrics = data.application as ApplicationMetrics;
      }
      if (data.business) {
        this.businessMetrics = data.business as BusinessMetrics;
      }
      if (data.cluster) {
        this.clusterStatus = data.cluster as ClusterStatus;
      }

      callback({
        system: this.systemMetrics,
        application: this.applicationMetrics,
        business: this.businessMetrics,
        cluster: this.clusterStatus
      });
    });
  }

  public subscribeToAlerts(callback: (alerts: AlertInfo[]) => void): () => void {
    return this.subscribe('alert_triggered', (event) => {
      const alert = event.data as Partial<AlertInfo>;
      
      // Validate required fields exist
      if (!alert.name || !alert.message || !alert.triggered_at) {
        console.warn('Invalid alert data received:', alert);
        return;
      }
      
      const fullAlert: AlertInfo = {
        name: alert.name,
        severity: (alert.severity as AlertInfo['severity']) || 'info',
        message: alert.message,
        triggered_at: alert.triggered_at,
        resolved: Boolean(alert.resolved),
        resolved_at: alert.resolved_at as string | undefined
      };
      
      // Add to active alerts
      this.activeAlerts.push(fullAlert);
      
      // Keep only recent alerts (last 50)
      if (this.activeAlerts.length > 50) {
        this.activeAlerts = this.activeAlerts.slice(-50);
      }
      
      callback(this.activeAlerts);
    });
  }

  public acknowledgeAlert(alertName: string): void {
    this.sendMessage('acknowledge_alert', { alert_name: alertName });
  }

  public getHistoricalMetrics(minutes: number = 60): Promise<any> {
    // This would call a REST endpoint to get historical data
    return fetch(`/api/v1/monitoring/metrics/history?minutes=${minutes}`)
      .then(res => res.json())
      .catch(error => {
        console.error('Failed to fetch historical metrics:', error);
        throw error;
      });
  }

  private handleOpen(): void {
    console.log('Monitoring WebSocket connected successfully');
    this.reconnectAttempts = 0;
    
    // Start heartbeat to keep connection alive
    this.startHeartbeat();
    
    // Notify connection listeners
    this.connectionListeners.forEach(listener => listener(true));
    
    // Send subscription request
    this.sendMessage('subscribe', {
      topics: ['metrics', 'alerts', 'system_status'],
      client_id: this.clientId
    });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      
      // Handle different message types
      if (data.event_type) {
        const event: MonitorEvent = {
          event_type: data.event_type,
          timestamp: data.timestamp,
          data: data.data,
          severity: data.severity || 'info'
        };
        
        // Route to appropriate listeners
        const listeners = this.listeners.get(event.event_type);
        if (listeners) {
          listeners.forEach(listener => {
            try {
              listener(event);
            } catch (error) {
              console.error(`Error in monitoring listener for ${event.event_type}:`, error);
            }
          });
        }
      }
    } catch (error) {
      console.error('Failed to parse monitoring WebSocket message:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('Monitoring WebSocket closed:', event.code, event.reason);
    
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
    console.error('Monitoring WebSocket error:', event);
    
    // Notify connection listeners of disconnection
    this.connectionListeners.forEach(listener => listener(false));
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max monitoring reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Attempting to reconnect monitoring in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
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
        this.sendMessage('ping', { timestamp: new Date().toISOString() });
      }
    }, 30000); // 30 seconds
  }
}

// Singleton instance
export const monitoringService = new MonitoringService();