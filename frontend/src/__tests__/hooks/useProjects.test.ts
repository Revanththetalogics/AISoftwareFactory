import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock the api client
vi.mock('@/lib/api/client', () => ({
  api: {
    getProjects: vi.fn(),
    getProject: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
    activateProject: vi.fn(),
  },
}));

import { api } from '@/lib/api/client';
import {
  useProjects,
  useProject,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  useActivateProject,
} from '@/lib/hooks/useProjects';
import type { Project } from '@/lib/types';

const mockProjects: Project[] = [
  {
    id: 'project-1',
    name: 'Test Project 1',
    description: 'Description 1',
    status: 'active',
    progress_percent: 50,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'project-2',
    name: 'Test Project 2',
    description: 'Description 2',
    status: 'draft',
    progress_percent: 0,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
];

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

function createWrapper() {
  const queryClient = createTestQueryClient();
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(
      QueryClientProvider,
      { client: queryClient },
      children
    );
  };
}

describe('useProjects', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useProjects hook', () => {
    it('returns loading state initially', () => {
      vi.mocked(api.getProjects).mockReturnValue(new Promise(() => {}));

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();
    });

    it('fetches projects successfully', async () => {
      vi.mocked(api.getProjects).mockResolvedValue(mockProjects);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockProjects);
      expect(api.getProjects).toHaveBeenCalledTimes(1);
    });

    it('handles error state', async () => {
      const error = new Error('Failed to fetch projects');
      vi.mocked(api.getProjects).mockRejectedValue(error);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBe(error);
    });
  });

  describe('useProject hook', () => {
    it('fetches single project by id', async () => {
      const singleProject = mockProjects[0];
      vi.mocked(api.getProject).mockResolvedValue(singleProject);

      const { result } = renderHook(() => useProject('project-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(singleProject);
      expect(api.getProject).toHaveBeenCalledWith('project-1');
    });

    it('does not fetch when id is empty', () => {
      const { result } = renderHook(() => useProject(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.getProject).not.toHaveBeenCalled();
    });
  });

  describe('useCreateProject hook', () => {
    it('creates a project successfully', async () => {
      const newProject: Project = {
        id: 'project-3',
        name: 'New Project',
        description: 'New Description',
        status: 'draft',
        progress_percent: 0,
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      };
      vi.mocked(api.createProject).mockResolvedValue(newProject);

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useCreateProject(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({
          name: 'New Project',
          description: 'New Description',
        });
      });

      expect(api.createProject).toHaveBeenCalledWith({
        name: 'New Project',
        description: 'New Description',
      });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['projects'] });
    });

    it('handles creation error', async () => {
      const error = new Error('Creation failed');
      vi.mocked(api.createProject).mockRejectedValue(error);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        try {
          await result.current.mutateAsync({
            name: 'Failing Project',
            description: 'Will fail',
          });
        } catch (e) {
          expect(e).toBe(error);
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useUpdateProject hook', () => {
    it('updates a project successfully', async () => {
      const updatedProject: Project = { ...mockProjects[0], name: 'Updated Name' };
      vi.mocked(api.updateProject).mockResolvedValue(updatedProject);

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useUpdateProject(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({
          id: 'project-1',
          data: { name: 'Updated Name' },
        });
      });

      expect(api.updateProject).toHaveBeenCalledWith('project-1', { name: 'Updated Name' });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['projects'] });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['projects', 'project-1'] });
    });
  });

  describe('useDeleteProject hook', () => {
    it('deletes a project successfully', async () => {
      vi.mocked(api.deleteProject).mockResolvedValue(undefined);

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useDeleteProject(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync('project-1');
      });

      expect(api.deleteProject).toHaveBeenCalledWith('project-1');
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['projects'] });
    });
  });

  describe('useActivateProject hook', () => {
    it('activates a project successfully', async () => {
      const activatedProject: Project = { ...mockProjects[0], status: 'active' };
      vi.mocked(api.activateProject).mockResolvedValue(activatedProject);

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useActivateProject(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync('project-1');
      });

      expect(api.activateProject).toHaveBeenCalledWith('project-1');
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['projects'] });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['projects', 'project-1'] });
    });
  });
});
