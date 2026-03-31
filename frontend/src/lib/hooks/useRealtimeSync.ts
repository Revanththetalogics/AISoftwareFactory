'use client';

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useFactoryWebSocket } from '@/hooks/useFactoryWebSocket';

export function useRealtimeSync() {
  const queryClient = useQueryClient();
  const { subscribe } = useFactoryWebSocket();

  useEffect(() => {
    const unsubscribers = [
      subscribe('PIPELINE_UPDATE', () => {
        queryClient.invalidateQueries({ queryKey: ['projects'] });
        queryClient.invalidateQueries({ queryKey: ['workflows'] });
      }),
      
      subscribe('AGENT_STATUS', () => {
        queryClient.invalidateQueries({ queryKey: ['agents'] });
      }),
      
      subscribe('WORKFLOW_STEP', () => {
        queryClient.invalidateQueries({ queryKey: ['workflows'] });
      }),
      
      subscribe('DEPLOYMENT_UPDATE', () => {
        queryClient.invalidateQueries({ queryKey: ['deployments'] });
      }),
      
      subscribe('TEST_COMPLETE', () => {
        queryClient.invalidateQueries({ queryKey: ['testing'] });
      }),
    ];

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe, queryClient]);
}
