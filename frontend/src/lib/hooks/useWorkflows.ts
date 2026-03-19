'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

const WORKFLOWS_KEY = 'workflows';

export function useWorkflows() {
  return useQuery({
    queryKey: [WORKFLOWS_KEY],
    queryFn: () => api.getWorkflows(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 30000, // Refetch every 30 seconds (reduced from 10s)
  });
}

export function useWorkflow(id: string) {
  return useQuery({
    queryKey: [WORKFLOWS_KEY, id],
    queryFn: () => api.getWorkflow(id),
    enabled: !!id,
    refetchInterval: 5000, // Refetch every 5 seconds for active workflow
  });
}

export function useExecuteWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { project_id: string; phase?: string }) =>
      api.executeWorkflow(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [WORKFLOWS_KEY] });
    },
  });
}

export function useCancelWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.cancelWorkflow(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [WORKFLOWS_KEY] });
      queryClient.invalidateQueries({ queryKey: [WORKFLOWS_KEY, id] });
    },
  });
}

// Re-export for convenience
export { useAvailablePhases } from './useMetadata';
