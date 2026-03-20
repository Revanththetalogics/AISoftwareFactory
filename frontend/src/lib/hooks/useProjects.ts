'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import type { Project } from '@/lib/types';

const PROJECTS_KEY = 'projects';

export function useProjects() {
  return useQuery({
    queryKey: [PROJECTS_KEY],
    queryFn: () => api.getProjects(),
    staleTime: 5000, // 5 seconds
    gcTime: 30000, // 30 seconds
    refetchOnWindowFocus: true,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: [PROJECTS_KEY, id],
    queryFn: () => api.getProject(id),
    enabled: !!id,
    staleTime: 5000,
    gcTime: 30000,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; description: string; requirements?: string }) =>
      api.createProject(data),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY] });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) =>
      api.updateProject(id, data),
    onSuccess: (_, variables) => {
      // Invalidate specific queries
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY] });
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY, variables.id] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.deleteProject(id),
    onSuccess: () => {
      // Invalidate all project queries
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY] });
    },
  });
}

export function useActivateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.activateProject(id),
    onSuccess: (_, id) => {
      // Invalidate specific queries
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY] });
      queryClient.invalidateQueries({ queryKey: [PROJECTS_KEY, id] });
    },
  });
}
