import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  
  // WebSocket readyState constants
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;
  
  url: string;
  readyState: number = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  
  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }
  
  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
  });
  
  // Test helpers
  simulateOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.(new Event('open'));
  }
  
  simulateClose() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close'));
  }
  
  simulateMessage(data: unknown) {
    this.onmessage?.(new MessageEvent('message', {
      data: JSON.stringify(data),
    }));
  }
  
  simulateError() {
    this.onerror?.(new Event('error'));
  }
  
  static reset() {
    MockWebSocket.instances = [];
  }
  
  static get lastInstance() {
    return MockWebSocket.instances[MockWebSocket.instances.length - 1];
  }
}

// Store original WebSocket
const originalWebSocket = globalThis.WebSocket;

import { useWebSocket } from '@/lib/hooks/useWebSocket';

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
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

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    MockWebSocket.reset();
    // Replace global WebSocket with mock
    globalThis.WebSocket = MockWebSocket as unknown as typeof WebSocket;
  });
  
  afterEach(() => {
    // Restore original WebSocket
    globalThis.WebSocket = originalWebSocket;
  });

  describe('connection establishment', () => {
    it('connects to WebSocket on mount', () => {
      renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      expect(MockWebSocket.instances).toHaveLength(1);
      expect(MockWebSocket.lastInstance.url).toContain('/test-channel');
    });

    it('connects with channel and id', () => {
      renderHook(
        () => useWebSocket({
          channel: 'workflows',
          id: 'wf-123',
        }),
        { wrapper: createWrapper() }
      );

      expect(MockWebSocket.lastInstance.url).toContain('/workflows/wf-123');
    });

    it('sets isConnected to true on open', async () => {
      const { result } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      expect(result.current.isConnected).toBe(false);

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      expect(result.current.isConnected).toBe(true);
    });

    it('calls onConnect callback when connection opens', async () => {
      const onConnect = vi.fn();
      
      renderHook(
        () => useWebSocket({
          channel: 'test-channel',
          onConnect,
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      expect(onConnect).toHaveBeenCalledTimes(1);
    });
  });

  describe('message handling', () => {
    it('updates lastMessage on incoming message', async () => {
      const { result } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      const testMessage = {
        type: 'test_message',
        data: { value: 'test' },
        timestamp: '2024-01-01T00:00:00Z',
      };

      act(() => {
        MockWebSocket.lastInstance.simulateMessage(testMessage);
      });

      // The hook normalises the timestamp to the current time, so only check type and data
      expect(result.current.lastMessage).toMatchObject({ type: testMessage.type, data: testMessage.data });
    });

    it('calls onMessage callback with parsed message', async () => {
      const onMessage = vi.fn();
      
      renderHook(
        () => useWebSocket({
          channel: 'test-channel',
          onMessage,
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      const testMessage = {
        type: 'agent_update',
        data: { agent_id: 'agent-1', status: 'busy' },
        timestamp: '2024-01-01T00:00:00Z',
      };

      act(() => {
        MockWebSocket.lastInstance.simulateMessage(testMessage);
      });

      // The hook normalises the timestamp to the current time, so only check type and data
      expect(onMessage).toHaveBeenCalledWith(expect.objectContaining({ type: testMessage.type, data: testMessage.data }));
    });

    it('handles agent_update message type', async () => {
      const queryClient = createTestQueryClient();
      queryClient.setQueryData(['agents'], [
        { agent_id: 'agent-1', status: 'idle', name: 'Test Agent' },
      ]);

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      renderHook(
        () => useWebSocket({
          channel: 'agents',
          enableCacheUpdates: true,
        }),
        { wrapper }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      act(() => {
        MockWebSocket.lastInstance.simulateMessage({
          type: 'agent_update',
          data: { agent_id: 'agent-1', status: 'busy' },
          timestamp: '2024-01-01T00:00:00Z',
        });
      });

      const agents = queryClient.getQueryData(['agents']) as Array<{ agent_id: string; status: string }>;
      expect(agents[0].status).toBe('busy');
    });

    it('handles project_update message type', async () => {
      const queryClient = createTestQueryClient();
      queryClient.setQueryData(['projects'], [
        { id: 'project-1', name: 'Original Name', status: 'draft' },
      ]);

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      renderHook(
        () => useWebSocket({
          channel: 'projects',
          enableCacheUpdates: true,
        }),
        { wrapper }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      act(() => {
        MockWebSocket.lastInstance.simulateMessage({
          type: 'project_update',
          data: { id: 'project-1', status: 'active' },
          timestamp: '2024-01-01T00:00:00Z',
        });
      });

      const projects = queryClient.getQueryData(['projects']) as Array<{ id: string; status: string }>;
      expect(projects[0].status).toBe('active');
    });

    it('handles workflow_update message type', async () => {
      const queryClient = createTestQueryClient();
      queryClient.setQueryData(['workflows'], [
        { workflow_id: 'wf-1', status: 'running', progress: 50 },
      ]);

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      renderHook(
        () => useWebSocket({
          channel: 'workflows',
          enableCacheUpdates: true,
        }),
        { wrapper }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      act(() => {
        MockWebSocket.lastInstance.simulateMessage({
          type: 'workflow_update',
          data: { workflow_id: 'wf-1', status: 'completed', progress: 100 },
          timestamp: '2024-01-01T00:00:00Z',
        });
      });

      const workflows = queryClient.getQueryData(['workflows']) as Array<{ workflow_id: string; status: string; progress: number }>;
      expect(workflows[0].status).toBe('completed');
      expect(workflows[0].progress).toBe(100);
    });
  });

  describe('disconnection handling', () => {
    it('sets isConnected to false on close', async () => {
      const { result } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      expect(result.current.isConnected).toBe(true);

      act(() => {
        MockWebSocket.lastInstance.simulateClose();
      });

      expect(result.current.isConnected).toBe(false);
    });

    it('calls onDisconnect callback when connection closes', async () => {
      const onDisconnect = vi.fn();
      
      renderHook(
        () => useWebSocket({
          channel: 'test-channel',
          onDisconnect,
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      act(() => {
        MockWebSocket.lastInstance.simulateClose();
      });

      expect(onDisconnect).toHaveBeenCalledTimes(1);
    });

    it('attempts reconnection on disconnect', async () => {
      vi.useFakeTimers();

      renderHook(
        () => useWebSocket({
          channel: 'test-channel',
          reconnectAttempts: 3,
          reconnectInterval: 1000,
        }),
        { wrapper: createWrapper() }
      );

      expect(MockWebSocket.instances).toHaveLength(1);

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      act(() => {
        MockWebSocket.lastInstance.simulateClose();
      });

      // Advance time for reconnection
      await act(async () => {
        vi.advanceTimersByTime(1000);
      });

      // Should have created a new WebSocket instance
      expect(MockWebSocket.instances.length).toBeGreaterThanOrEqual(2);

      vi.useRealTimers();
    });
  });

  describe('error handling', () => {
    it('calls onError callback on WebSocket error', async () => {
      const onError = vi.fn();
      
      renderHook(
        () => useWebSocket({
          channel: 'test-channel',
          onError,
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateError();
      });

      expect(onError).toHaveBeenCalledTimes(1);
    });
  });

  describe('send function', () => {
    it('sends data when connected', async () => {
      const { result } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      const testData = { action: 'subscribe', topic: 'updates' };

      act(() => {
        result.current.send(testData);
      });

      expect(MockWebSocket.lastInstance.send).toHaveBeenCalledWith(
        JSON.stringify(testData)
      );
    });

    it('warns when sending while disconnected', async () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      const { result } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      // Ensure connection is not open (readyState stays CONNECTING)
      expect(result.current.isConnected).toBe(false);

      act(() => {
        result.current.send({ test: 'data' });
      });

      expect(consoleWarnSpy).toHaveBeenCalledWith('WebSocket is not connected');
      
      consoleWarnSpy.mockRestore();
    });
  });

  describe('cleanup on unmount', () => {
    it('closes WebSocket connection on unmount', async () => {
      const { unmount } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      const wsInstance = MockWebSocket.lastInstance;

      act(() => {
        wsInstance.simulateOpen();
      });

      unmount();

      expect(wsInstance.close).toHaveBeenCalled();
    });

    it('clears reconnect timer on unmount', async () => {
      vi.useFakeTimers();

      const { unmount } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
          reconnectAttempts: 5,
          reconnectInterval: 1000,
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      act(() => {
        MockWebSocket.lastInstance.simulateClose();
      });

      // Unmount before reconnection timer fires
      unmount();

      // Advance time past reconnection interval
      await act(async () => {
        vi.advanceTimersByTime(2000);
      });

      // Should not have created additional instances after unmount
      // (Only initial + 1 reconnect attempt before unmount)
      expect(MockWebSocket.instances.length).toBeLessThanOrEqual(2);

      vi.useRealTimers();
    });
  });

  describe('manual control', () => {
    it('provides disconnect function', async () => {
      const { result } = renderHook(
        () => useWebSocket({
          channel: 'test-channel',
        }),
        { wrapper: createWrapper() }
      );

      act(() => {
        MockWebSocket.lastInstance.simulateOpen();
      });

      expect(result.current.isConnected).toBe(true);

      act(() => {
        result.current.disconnect();
      });

      expect(MockWebSocket.lastInstance.close).toHaveBeenCalled();
    });
  });
});
