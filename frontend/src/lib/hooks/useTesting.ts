'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

const TESTING_KEY = 'testing';

export function useTestStatistics(projectId?: string) {
  return useQuery({
    queryKey: [TESTING_KEY, 'statistics', projectId],
    queryFn: () => api.getTestStatistics(projectId),
    staleTime: 10000, // 10 seconds
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useTestRuns(projectId?: string) {
  return useQuery({
    queryKey: [TESTING_KEY, 'runs', projectId],
    queryFn: () => api.getTestRuns(projectId),
    staleTime: 10000,
    refetchInterval: 30000,
  });
}

export function useBugs(filters?: { projectId?: string; status?: string; severity?: string }) {
  return useQuery({
    queryKey: [TESTING_KEY, 'bugs', filters],
    queryFn: () => api.getBugs(filters),
    staleTime: 10000,
    refetchInterval: 30000,
  });
}

export function useTestFiles(projectId: string) {
  return useQuery({
    queryKey: [TESTING_KEY, 'files', projectId],
    queryFn: () => api.getTestFiles(projectId),
    enabled: !!projectId,
    staleTime: 10000,
  });
}

export function useCoverageData(projectId: string) {
  return useQuery({
    queryKey: [TESTING_KEY, 'coverage', projectId],
    queryFn: () => api.getCoverageData(projectId),
    enabled: !!projectId,
    staleTime: 10000,
  });
}

export function useCreateBug() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      projectId: string;
      title: string;
      description: string;
      severity: string;
      filePath?: string;
      lineNumber?: number;
    }) => api.createBug(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TESTING_KEY, 'bugs'] });
    },
  });
}
