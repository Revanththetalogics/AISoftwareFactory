'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import type { Agent } from '@/lib/types';

const AGENTS_KEY = 'agents';

export function useAgents() {
  return useQuery({
    queryKey: [AGENTS_KEY],
    queryFn: () => api.getAgents(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useAgent(id: string) {
  return useQuery({
    queryKey: [AGENTS_KEY, id],
    queryFn: () => api.getAgent(id),
    enabled: !!id,
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
      queryClient.invalidateQueries({ queryKey: [AGENTS_KEY] });
      queryClient.invalidateQueries({ queryKey: [AGENTS_KEY, variables.agentId] });
    },
  });
}
