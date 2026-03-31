'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp: string;
}

interface UseWebSocketOptions {
  channel: string;
  id?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  enableCacheUpdates?: boolean; // Enable automatic TanStack Query cache updates
}

export function useWebSocket({
  channel,
  id,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  reconnectAttempts = 5,
  reconnectInterval = 3000,
  enableCacheUpdates = true,
}: UseWebSocketOptions) {
  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);

  const connectRef = useRef<(() => void) | null>(null);

  const connect = useCallback(() => {
    const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
    const url = id ? `${WS_BASE_URL}/${channel}/${id}` : `${WS_BASE_URL}/${channel}`;

    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setIsConnected(true);
        reconnectCount.current = 0;
        onConnect?.();
      };

      ws.current.onmessage = (event) => {
        try {
          // Backend sends { type, payload } — normalise to the hook's { type, data } shape
          const raw = JSON.parse(event.data) as { type: string; payload?: unknown; data?: unknown };
          const normalised: WebSocketMessage = {
            type: raw.type,
            data: raw.payload ?? raw.data ?? raw,
            timestamp: new Date().toISOString(),
          };
          setLastMessage(normalised);

          if (enableCacheUpdates) {
            const payload = normalised.data as Record<string, unknown>;

            switch (raw.type) {
              // ── Backend native types ─────────────────────────────────────
              case 'status':
                // Project/workflow status changed — invalidate both caches
                queryClient.invalidateQueries({ queryKey: ['projects'] });
                queryClient.invalidateQueries({ queryKey: ['workflows'] });
                if (payload?.project_id) {
                  queryClient.invalidateQueries({ queryKey: ['projects', payload.project_id] });
                }
                if (payload?.workflow_id) {
                  queryClient.invalidateQueries({ queryKey: ['workflows', payload.workflow_id] });
                }
                break;

              case 'logs':
                // Workflow logs arrived — refresh the specific workflow
                if (payload?.workflow_id) {
                  queryClient.invalidateQueries({ queryKey: ['workflows', payload.workflow_id] });
                }
                break;

              case 'connected':
              case 'pong':
              case 'subscribed':
                // Keep-alive / handshake frames — no cache action needed
                break;

              // ── Legacy / direct-match types ──────────────────────────────
              case 'agent_update':
                queryClient.setQueryData(['agents'], (old: unknown) => {
                  if (!Array.isArray(old)) return old;
                  return old.map((a: Record<string, unknown>) =>
                    a.agent_id === payload?.agent_id ? { ...a, ...payload } : a,
                  );
                });
                break;

              case 'project_update':
                queryClient.setQueryData(['projects'], (old: unknown) => {
                  if (!Array.isArray(old)) return old;
                  return old.map((p: Record<string, unknown>) =>
                    p.id === payload?.id ? { ...p, ...payload } : p,
                  );
                });
                break;

              case 'workflow_update':
                queryClient.setQueryData(['workflows'], (old: unknown) => {
                  if (!Array.isArray(old)) return old;
                  return old.map((w: Record<string, unknown>) =>
                    w.workflow_id === payload?.workflow_id ? { ...w, ...payload } : w,
                  );
                });
                break;

              default:
                break;
            }
          }

          onMessage?.(normalised);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        onDisconnect?.();

        // Attempt reconnection
        if (reconnectCount.current < reconnectAttempts) {
          reconnectCount.current += 1;
          reconnectTimer.current = setTimeout(() => {
            console.log(`Reconnecting... Attempt ${reconnectCount.current}`);
            connectRef.current?.();
          }, reconnectInterval);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [channel, id, onMessage, onConnect, onDisconnect, onError, reconnectAttempts, reconnectInterval, enableCacheUpdates, queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    ws.current?.close();
  }, []);

  const send = useCallback((data: unknown) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    // Store connect function in ref so reconnect callbacks always use the latest version
    connectRef.current = connect;
  });

  useEffect(() => {
    // Connect once on mount using the ref to avoid stale closure issues
    // and prevent reconnection loops caused by changing callback deps
    connectRef.current?.();

    return () => {
      // Cancel any pending reconnect timer and close socket on unmount
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      ws.current?.close();
    };
  }, []); // mount-only: connectRef always has the latest connect fn

  return {
    isConnected,
    lastMessage,
    send,
    connect,
    disconnect,
  };
}
