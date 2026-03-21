import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock the api client
vi.mock('@/lib/api/client', () => ({
  api: {
    getWorkflows: vi.fn(),
    getWorkflow: vi.fn(),
    executeWorkflow: vi.fn(),
    cancelWorkflow: vi.fn(),
    getAvailablePhases: vi.fn(),
  },
}));

import { api } from '@/lib/api/client';
import {
  useWorkflows,
  useWorkflow,
  useExecuteWorkflow,
  useCancelWorkflow,
} from '@/lib/hooks/useWorkflows';
import type { Workflow } from '@/lib/types';

const mockWorkflows: Workflow[] = [
  {
    workflow_id: 'wf-1',
    project_id: 'project-1',
    status: 'running',
    current_phase: 'design',
    progress_percent: 50,
    steps_completed: 2,
    steps_total: 4,
    logs: [],
  },
  {
    workflow_id: 'wf-2',
    project_id: 'project-2',
    status: 'completed',
    current_phase: 'deployment',
    progress_percent: 100,
    steps_completed: 4,
    steps_total: 4,
    logs: [],
  },
];

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        refetchInterval: false,
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

describe('useWorkflows', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useWorkflows hook', () => {
    it('returns loading state initially', () => {
      vi.mocked(api.getWorkflows).mockReturnValue(new Promise(() => {}));

      const { result } = renderHook(() => useWorkflows(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();
    });

    it('fetches workflows successfully', async () => {
      vi.mocked(api.getWorkflows).mockResolvedValue(mockWorkflows);

      const { result } = renderHook(() => useWorkflows(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockWorkflows);
      expect(api.getWorkflows).toHaveBeenCalledTimes(1);
    });

    it('handles error state', async () => {
      const error = new Error('Failed to fetch workflows');
      vi.mocked(api.getWorkflows).mockRejectedValue(error);

      const { result } = renderHook(() => useWorkflows(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBe(error);
    });
  });

  describe('useWorkflow hook', () => {
    it('fetches single workflow by id', async () => {
      const singleWorkflow = mockWorkflows[0];
      vi.mocked(api.getWorkflow).mockResolvedValue(singleWorkflow);

      const { result } = renderHook(() => useWorkflow('wf-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(singleWorkflow);
      expect(api.getWorkflow).toHaveBeenCalledWith('wf-1');
    });

    it('does not fetch when id is empty', () => {
      const { result } = renderHook(() => useWorkflow(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.getWorkflow).not.toHaveBeenCalled();
    });

    it('handles running workflow status', async () => {
      const runningWorkflow: Workflow = {
        ...mockWorkflows[0],
        status: 'running',
        progress_percent: 75,
      };
      vi.mocked(api.getWorkflow).mockResolvedValue(runningWorkflow);

      const { result } = renderHook(() => useWorkflow('wf-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.status).toBe('running');
      expect(result.current.data?.progress_percent).toBe(75);
    });
  });

  describe('useExecuteWorkflow hook', () => {
    it('executes a workflow successfully', async () => {
      const newWorkflow: Workflow = {
        workflow_id: 'wf-3',
        project_id: 'project-1',
        status: 'pending',
        current_phase: 'initialization',
        progress_percent: 0,
        steps_completed: 0,
        steps_total: 4,
        logs: [],
      };
      vi.mocked(api.executeWorkflow).mockResolvedValue(newWorkflow);

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useExecuteWorkflow(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({
          project_id: 'project-1',
          phase: 'design',
        });
      });

      expect(api.executeWorkflow).toHaveBeenCalledWith({
        project_id: 'project-1',
        phase: 'design',
      });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['workflows'] });
    });

    it('executes workflow without phase', async () => {
      const newWorkflow: Workflow = {
        workflow_id: 'wf-4',
        project_id: 'project-2',
        status: 'pending',
        current_phase: 'all',
        progress_percent: 0,
        steps_completed: 0,
        steps_total: 4,
        logs: [],
      };
      vi.mocked(api.executeWorkflow).mockResolvedValue(newWorkflow);

      const { result } = renderHook(() => useExecuteWorkflow(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({ project_id: 'project-2' });
      });

      expect(api.executeWorkflow).toHaveBeenCalledWith({ project_id: 'project-2' });
    });

    it('handles execution error', async () => {
      const error = new Error('Workflow execution failed');
      vi.mocked(api.executeWorkflow).mockRejectedValue(error);

      const { result } = renderHook(() => useExecuteWorkflow(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        try {
          await result.current.mutateAsync({ project_id: 'project-1' });
        } catch (e) {
          expect(e).toBe(error);
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useCancelWorkflow hook', () => {
    it('cancels a workflow successfully', async () => {
      const cancelledWorkflow: Workflow = {
        ...mockWorkflows[0],
        status: 'cancelled',
      };
      vi.mocked(api.cancelWorkflow).mockResolvedValue(cancelledWorkflow);

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useCancelWorkflow(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync('wf-1');
      });

      expect(api.cancelWorkflow).toHaveBeenCalledWith('wf-1');
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['workflows'] });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['workflows', 'wf-1'] });
    });

    it('handles cancel error', async () => {
      const error = new Error('Cannot cancel workflow');
      vi.mocked(api.cancelWorkflow).mockRejectedValue(error);

      const { result } = renderHook(() => useCancelWorkflow(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        try {
          await result.current.mutateAsync('wf-1');
        } catch (e) {
          expect(e).toBe(error);
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });
});
