'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

const WORKFLOWS_KEY = 'workflows';

export function useWorkflows() {
  return useQuery({
    queryKey: [WORKFLOWS_KEY],
    queryFn: () => api.getWorkflows(),
    staleTime: 5000, // 5 seconds
    refetchInterval: 10000, // Refetch every 10 seconds for active workflows
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
