'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

const DEPLOYMENTS_KEY = 'deployments';

export function useDeployments() {
  return useQuery({
    queryKey: [DEPLOYMENTS_KEY],
    queryFn: () => api.getDeployments(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useDeployment(id: string) {
  return useQuery({
    queryKey: [DEPLOYMENTS_KEY, id],
    queryFn: () => api.getDeployment(id),
    enabled: !!id,
    staleTime: 5000,
  });
}

export function useCreateDeployment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { project_id: string; environment: string; version: string }) =>
      api.createDeployment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DEPLOYMENTS_KEY] });
    },
  });
}
