import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock the api client
vi.mock('@/lib/api/client', () => ({
  api: {
    getAgents: vi.fn(),
    getAgent: vi.fn(),
    assignTask: vi.fn(),
  },
}));

import { api } from '@/lib/api/client';
import { useAgents, useAgent, useAssignTask } from '@/lib/hooks/useAgents';
import type { Agent } from '@/lib/types';

const mockAgents: Agent[] = [
  {
    agent_id: 'agent-1',
    name: 'Architect Agent',
    role: 'architect',
    status: 'idle',
    current_task: undefined,
    capabilities: ['system_design', 'api_design'],
  },
  {
    agent_id: 'agent-2',
    name: 'Developer Agent',
    role: 'developer',
    status: 'busy',
    current_task: 'Implementing feature X',
    capabilities: ['coding', 'testing'],
  },
  {
    agent_id: 'agent-3',
    name: 'Tester Agent',
    role: 'tester',
    status: 'idle',
    current_task: undefined,
    capabilities: ['unit_testing', 'integration_testing'],
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

describe('useAgents', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useAgents hook', () => {
    it('returns loading state initially', () => {
      vi.mocked(api.getAgents).mockReturnValue(new Promise(() => {}));

      const { result } = renderHook(() => useAgents(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();
    });

    it('fetches agents successfully', async () => {
      vi.mocked(api.getAgents).mockResolvedValue(mockAgents);

      const { result } = renderHook(() => useAgents(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockAgents);
      expect(api.getAgents).toHaveBeenCalledTimes(1);
    });

    it('handles error state', async () => {
      const error = new Error('Failed to fetch agents');
      vi.mocked(api.getAgents).mockRejectedValue(error);

      const { result } = renderHook(() => useAgents(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBe(error);
    });

    it('returns agents with different statuses', async () => {
      vi.mocked(api.getAgents).mockResolvedValue(mockAgents);

      const { result } = renderHook(() => useAgents(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      const idleAgents = result.current.data?.filter(a => a.status === 'idle');
      const busyAgents = result.current.data?.filter(a => a.status === 'busy');

      expect(idleAgents).toHaveLength(2);
      expect(busyAgents).toHaveLength(1);
    });

    it('returns agents with different roles', async () => {
      vi.mocked(api.getAgents).mockResolvedValue(mockAgents);

      const { result } = renderHook(() => useAgents(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      const roles = result.current.data?.map(a => a.role);
      expect(roles).toContain('architect');
      expect(roles).toContain('developer');
      expect(roles).toContain('tester');
    });
  });

  describe('useAgent hook', () => {
    it('fetches single agent by id', async () => {
      const singleAgent = mockAgents[0];
      vi.mocked(api.getAgent).mockResolvedValue(singleAgent);

      const { result } = renderHook(() => useAgent('agent-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(singleAgent);
      expect(api.getAgent).toHaveBeenCalledWith('agent-1');
    });

    it('does not fetch when id is empty', () => {
      const { result } = renderHook(() => useAgent(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.getAgent).not.toHaveBeenCalled();
    });

    it('handles agent not found', async () => {
      const error = new Error('Agent not found');
      vi.mocked(api.getAgent).mockRejectedValue(error);

      const { result } = renderHook(() => useAgent('non-existent'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBe(error);
    });

    it('fetches agent with current task', async () => {
      const busyAgent = mockAgents[1];
      vi.mocked(api.getAgent).mockResolvedValue(busyAgent);

      const { result } = renderHook(() => useAgent('agent-2'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.status).toBe('busy');
      expect(result.current.data?.current_task).toBe('Implementing feature X');
    });
  });

  describe('useAssignTask hook', () => {
    it('assigns task to agent successfully', async () => {
      const updatedAgent: Agent = {
        ...mockAgents[0],
        status: 'busy',
        current_task: 'Design API endpoints',
      };
      vi.mocked(api.assignTask).mockResolvedValue(updatedAgent);

      const queryClient = createTestQueryClient();
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useAssignTask(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({
          agentId: 'agent-1',
          data: {
            task_type: 'design',
            description: 'Design API endpoints',
          },
        });
      });

      expect(api.assignTask).toHaveBeenCalledWith('agent-1', {
        task_type: 'design',
        description: 'Design API endpoints',
      });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['agents'] });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['agents', 'agent-1'] });
    });

    it('handles task assignment error', async () => {
      const error = new Error('Agent is currently busy');
      vi.mocked(api.assignTask).mockRejectedValue(error);

      const { result } = renderHook(() => useAssignTask(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        try {
          await result.current.mutateAsync({
            agentId: 'agent-2',
            data: {
              task_type: 'coding',
              description: 'Implement feature Y',
            },
          });
        } catch (e) {
          expect(e).toBe(error);
        }
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });

    it('assigns task with different task types', async () => {
      const updatedAgent: Agent = {
        ...mockAgents[2],
        status: 'busy',
        current_task: 'Run integration tests',
      };
      vi.mocked(api.assignTask).mockResolvedValue(updatedAgent);

      const { result } = renderHook(() => useAssignTask(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({
          agentId: 'agent-3',
          data: {
            task_type: 'testing',
            description: 'Run integration tests',
          },
        });
      });

      expect(api.assignTask).toHaveBeenCalledWith('agent-3', {
        task_type: 'testing',
        description: 'Run integration tests',
      });
    });
  });
});
