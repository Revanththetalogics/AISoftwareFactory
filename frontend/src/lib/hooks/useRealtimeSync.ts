'use client';

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { factoryWebSocket } from '@/services/websocket.service';

/**
 * Subscribes to factory WebSocket events and invalidates React Query caches.
 * Uses the shared {@link factoryWebSocket} client (same as useFactoryWebSocket).
 */
export function useRealtimeSync() {
  const queryClient = useQueryClient();

  useEffect(() => {
    factoryWebSocket.connect();

    const unsubscribers = [
      factoryWebSocket.subscribe('PIPELINE_UPDATE', () => {
        queryClient.invalidateQueries({ queryKey: ['projects'] });
        queryClient.invalidateQueries({ queryKey: ['workflows'] });
      }),

      factoryWebSocket.subscribe('AGENT_STATUS', () => {
        queryClient.invalidateQueries({ queryKey: ['agents'] });
      }),

      factoryWebSocket.subscribe('WORKFLOW_STEP', () => {
        queryClient.invalidateQueries({ queryKey: ['workflows'] });
        queryClient.invalidateQueries({ queryKey: ['deployments'] });
      }),

      factoryWebSocket.subscribe('LOG_ENTRY', () => {
        queryClient.invalidateQueries({ queryKey: ['testing'] });
      }),
    ];

    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, [queryClient]);
}
