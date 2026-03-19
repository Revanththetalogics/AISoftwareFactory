'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

const AGENTS_KEY = 'agents';

export function useAgents() {
  return useQuery({
    queryKey: [AGENTS_KEY],
    queryFn: () => api.getAgents(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every 60 seconds (reduced from 30s)
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
