import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Store original fetch
const originalFetch = globalThis.fetch;

// Mock fetch globally
const mockFetch = vi.fn();

describe('API Client', () => {
  type ApiClientType = {
    setToken: (token: string | null) => void;
    getProjects: () => Promise<unknown>;
    login: (data: { username: string; password: string }) => Promise<unknown>;
    getHealth: () => Promise<unknown>;
  };
  let api: ApiClientType;

  beforeEach(async () => {
    vi.resetModules();
    
    // Reset fetch mock
    mockFetch.mockReset();
    globalThis.fetch = mockFetch;
    
    // Reset localStorage mock
    const localStorageMock = window.localStorage as unknown as {
      getItem: ReturnType<typeof vi.fn>;
      setItem: ReturnType<typeof vi.fn>;
      removeItem: ReturnType<typeof vi.fn>;
    };
    localStorageMock.getItem.mockReturnValue(null);
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();

    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true,
    });

    // Dynamically import to get fresh instance
    const clientModule = await import('@/lib/api/client');
    api = clientModule.api;
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  describe('Authorization header', () => {
    it('adds Authorization header when token is set', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      });

      api.setToken('test-token-123');
      await api.getProjects();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token-123',
          }),
        })
      );
    });

    it('does not add Authorization header when token is null', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      });

      api.setToken(null);
      await api.getProjects();

      const callArgs = mockFetch.mock.calls[0][1] as { headers: Record<string, string> };
      expect(callArgs.headers['Authorization']).toBeUndefined();
    });

    it('updates Authorization header when token changes', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([]),
      });

      api.setToken('token-1');
      await api.getProjects();
      
      let callArgs = mockFetch.mock.calls[0][1] as { headers: Record<string, string> };
      expect(callArgs.headers['Authorization']).toBe('Bearer token-1');

      api.setToken('token-2');
      await api.getProjects();
      
      callArgs = mockFetch.mock.calls[1][1] as { headers: Record<string, string> };
      expect(callArgs.headers['Authorization']).toBe('Bearer token-2');
    });
  });

  describe('401 handling', () => {
    it('redirects to /login on 401 response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Unauthorized' }),
      });

      api.setToken('expired-token');
      
      await expect(api.getProjects()).rejects.toThrow('Authentication required');
      
      expect(window.location.href).toBe('/login');
    });

    it('clears token from localStorage on 401', async () => {
      const localStorageMock = window.localStorage as unknown as {
        removeItem: ReturnType<typeof vi.fn>;
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Unauthorized' }),
      });

      api.setToken('expired-token');
      
      try {
        await api.getProjects();
      } catch {
        // Expected to throw
      }

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('aifactory_token');
    });
  });

  describe('retry logic', () => {
    it('retries on 500 server error', async () => {
      // First call fails with 500
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server Error' }),
      });
      
      // Second call succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([{ id: 'project-1' }]),
      });

      const result = await api.getProjects();

      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(result).toEqual([{ id: 'project-1' }]);
    });

    it('retries up to MAX_RETRIES times', async () => {
      // All calls fail with 500
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server Error' }),
      });

      await expect(api.getProjects()).rejects.toThrow();

      // Should retry 3 times (MAX_RETRIES) plus initial request = 4 total
      expect(mockFetch).toHaveBeenCalledTimes(4);
    }, 15000); // Extended timeout for retry delays

    it('does not retry on 400 client error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ detail: 'Bad Request' }),
      });

      await expect(api.getProjects()).rejects.toThrow();

      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('does not retry on 404 not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'Not Found' }),
      });

      await expect(api.getProjects()).rejects.toThrow();

      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('request configuration', () => {
    it('sends JSON content type header', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'healthy' }),
      });

      await api.getHealth();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('uses correct API base URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      });

      await api.getProjects();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/projects'),
        expect.any(Object)
      );
    });
  });

  describe('setToken', () => {
    it('stores token in localStorage when token is provided', () => {
      const localStorageMock = window.localStorage as unknown as {
        setItem: ReturnType<typeof vi.fn>;
      };

      api.setToken('new-token');

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'aifactory_token',
        'new-token'
      );
    });

    it('removes token from localStorage when token is null', () => {
      const localStorageMock = window.localStorage as unknown as {
        removeItem: ReturnType<typeof vi.fn>;
      };

      api.setToken(null);

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('aifactory_token');
    });
  });

  describe('login', () => {
    it('stores token after successful login', async () => {
      const localStorageMock = window.localStorage as unknown as {
        setItem: ReturnType<typeof vi.fn>;
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          access_token: 'new-login-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: { user_id: 'user-1', username: 'testuser' },
        }),
      });

      await api.login({ username: 'testuser', password: 'password123' });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'aifactory_token',
        'new-login-token'
      );
    });

    it('returns login response on success', async () => {
      const loginResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
        expires_in: 3600,
        user: { user_id: 'user-1', username: 'testuser' },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(loginResponse),
      });

      const result = await api.login({ username: 'testuser', password: 'password123' });

      expect(result).toEqual(loginResponse);
    });
  });

  describe('error handling', () => {
    it('throws ApiError with status and message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: () => Promise.resolve({ detail: 'Forbidden access' }),
      });

      await expect(api.getProjects()).rejects.toMatchObject({
        message: 'Forbidden access',
        status: 403,
      });
    });

    it('handles json parse failure gracefully', async () => {
      // Use 403 to avoid retry logic (only 5xx errors retry)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: () => Promise.reject(new Error('JSON parse error')),
      });

      // When json parsing fails, client falls back to 'Unknown error' message
      await expect(api.getProjects()).rejects.toThrow('Unknown error');
    });
  });
});
