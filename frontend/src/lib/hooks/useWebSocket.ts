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
          const message = JSON.parse(event.data) as WebSocketMessage;
          setLastMessage(message);
          
          // Automatic cache updates for known message types
          if (enableCacheUpdates) {
            const msgData = message.data as Record<string, unknown>;
            
            switch (message.type) {
              case 'agent_update':
                queryClient.setQueryData(['agents'], (old: unknown) => {
                  if (!old || !Array.isArray(old)) return old;
                  return old.map((agent: Record<string, unknown>) =>
                    agent.agent_id === msgData.agent_id
                      ? { ...agent, ...msgData }
                      : agent,
                  );
                });
                break;
              
              case 'project_update':
                queryClient.setQueryData(['projects'], (old: unknown) => {
                  if (!old || !Array.isArray(old)) return old;
                  return old.map((project: Record<string, unknown>) =>
                    project.id === msgData.id
                      ? { ...project, ...msgData }
                      : project,
                  );
                });
                break;
              
              case 'workflow_update':
                queryClient.setQueryData(['workflows'], (old: unknown) => {
                  if (!old || !Array.isArray(old)) return old;
                  return old.map((wf: Record<string, unknown>) =>
                    wf.workflow_id === msgData.workflow_id
                      ? { ...wf, ...msgData }
                      : wf,
                  );
                });
                break;
            }
          }
          
          onMessage?.(message);
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
    // Store connect function in ref for use in callbacks
    connectRef.current = connect;
  });

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    send,
    connect,
    disconnect,
  };
}
