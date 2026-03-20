'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

const AGENTS_KEY = 'agents';

export function useAgents() {
  return useQuery({
    queryKey: [AGENTS_KEY],
    queryFn: () => api.getAgents(),
    staleTime: 5000, // 5 seconds - optimized for real-time dashboard
    gcTime: 30000, // 30 seconds
    refetchOnWindowFocus: true,
    refetchInterval: 10000, // Poll every 10s for agent status updates
  });
}

export function useAgent(id: string) {
  return useQuery({
    queryKey: [AGENTS_KEY, id],
    queryFn: () => api.getAgent(id),
    enabled: !!id,
    staleTime: 5000,
    gcTime: 30000,
  });
}

export function useAssignTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      agentId,
      data,
    }: {
      agentId: string;
      data: { task_type: string; description: string };
    }) => api.assignTask(agentId, data),
    onSuccess: (_, variables) => {
      // Invalidate specific queries
      queryClient.invalidateQueries({ queryKey: [AGENTS_KEY] });
      queryClient.invalidateQueries({ queryKey: [AGENTS_KEY, variables.agentId] });
    },
  });
}
