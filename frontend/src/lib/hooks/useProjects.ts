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
    onMutate: async (newProject) => {
      await queryClient.cancelQueries({ queryKey: [PROJECTS_KEY] });
      const previousProjects = queryClient.getQueryData([PROJECTS_KEY]);
      
      queryClient.setQueryData([PROJECTS_KEY], (old: any) => [
        ...(old || []),
        { ...newProject, id: `temp-${Date.now()}`, status: 'draft', created_at: new Date().toISOString() }
      ]);
      
      return { previousProjects };
    },
    onError: (err, newProject, context: any) => {
      queryClient.setQueryData([PROJECTS_KEY], context?.previousProjects);
    },
    onSuccess: () => {
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
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: [PROJECTS_KEY] });
      const previousProjects = queryClient.getQueryData([PROJECTS_KEY]);
      
      queryClient.setQueryData([PROJECTS_KEY], (old: any) => 
        (old || []).filter((p: any) => p.id !== id)
      );
      
      return { previousProjects };
    },
    onError: (err, id, context: any) => {
      queryClient.setQueryData([PROJECTS_KEY], context?.previousProjects);
    },
    onSuccess: () => {
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
