import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock the api client
vi.mock('@/lib/api/client', () => ({
  api: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
    setToken: vi.fn(),
  },
}));

// Mock the AuthContext
const mockLogin = vi.fn();
const mockLogout = vi.fn();
const mockGetToken = vi.fn();
let mockIsAuthenticated = false;
let mockUser: { user_id: string; username: string; email: string } | null = null;
let mockIsLoading = false;

vi.mock('@/lib/auth', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: mockIsAuthenticated,
    isLoading: mockIsLoading,
    login: mockLogin,
    logout: mockLogout,
    getToken: mockGetToken,
  }),
}));

import { api } from '@/lib/api/client';
import { useLogin, useRegister, useCurrentUser, useLogout } from '@/lib/hooks/useAuth';
import type { User, LoginResponse } from '@/lib/types';

const mockUserData: User = {
  user_id: 'user-1',
  username: 'testuser',
  email: 'test@example.com',
  permissions: ['read', 'write'],
  is_active: true,
};

const mockLoginResponse: LoginResponse = {
  access_token: 'test-token-123',
  refresh_token: 'test-refresh-token',
  token_type: 'bearer',
  expires_in: 3600,
  user_id: mockUserData.user_id,
  username: mockUserData.username,
  email: mockUserData.email,
  permissions: mockUserData.permissions,
};

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

describe('useAuth hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockIsAuthenticated = false;
    mockUser = null;
    mockIsLoading = false;
  });

  describe('useLogin hook', () => {
    it('calls api.login with credentials', async () => {
      vi.mocked(api.login).mockResolvedValue(mockLoginResponse);

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({
          username: 'testuser',
          password: 'password123',
        });
      });

      expect(api.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });

    it('calls context login on successful login', async () => {
      vi.mocked(api.login).mockResolvedValue(mockLoginResponse);

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({
          username: 'testuser',
          password: 'password123',
        });
      });

      expect(mockLogin).toHaveBeenCalledWith(mockLoginResponse);
    });

    it('updates query cache with user data on success', async () => {
      vi.mocked(api.login).mockResolvedValue(mockLoginResponse);

      const queryClient = createTestQueryClient();
      const setQueryDataSpy = vi.spyOn(queryClient, 'setQueryData');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useLogin(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync({
          username: 'testuser',
          password: 'password123',
        });
      });

      expect(setQueryDataSpy).toHaveBeenCalledWith(['auth'], mockUserData);
    });

    it('handles login error', async () => {
      const error = new Error('Invalid credentials');
      vi.mocked(api.login).mockRejectedValue(error);

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        try {
          await result.current.mutateAsync({
            username: 'wronguser',
            password: 'wrongpass',
          });
        } catch (e) {
          expect(e).toBe(error);
        }
      });

      expect(result.current.isError).toBe(true);
      expect(mockLogin).not.toHaveBeenCalled();
    });

    it('returns isLoading during login', async () => {
      let resolvePromise: (value: typeof mockLoginResponse) => void;
      vi.mocked(api.login).mockImplementation(
        () => new Promise((resolve) => { resolvePromise = resolve; })
      );

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.mutate({
          username: 'testuser',
          password: 'password123',
        });
      });

      await waitFor(() => {
        expect(result.current.isPending).toBe(true);
      });

      await act(async () => {
        resolvePromise!(mockLoginResponse);
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });
  });

  describe('useRegister hook', () => {
    it('calls api.register with user data', async () => {
      vi.mocked(api.register).mockResolvedValue(mockUserData);

      const { result } = renderHook(() => useRegister(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({
          username: 'newuser',
          email: 'new@example.com',
          password: 'newpass123',
        });
      });

      expect(api.register).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'new@example.com',
        password: 'newpass123',
      });
    });

    it('returns registered user on success', async () => {
      vi.mocked(api.register).mockResolvedValue(mockUserData);

      const { result } = renderHook(() => useRegister(), {
        wrapper: createWrapper(),
      });

      let registeredUser;
      await act(async () => {
        registeredUser = await result.current.mutateAsync({
          username: 'newuser',
          email: 'new@example.com',
          password: 'newpass123',
        });
      });

      expect(registeredUser).toEqual(mockUserData);
    });

    it('handles registration error', async () => {
      const error = new Error('Username already exists');
      vi.mocked(api.register).mockRejectedValue(error);

      const { result } = renderHook(() => useRegister(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        try {
          await result.current.mutateAsync({
            username: 'existinguser',
            email: 'existing@example.com',
            password: 'pass123',
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

  describe('useCurrentUser hook', () => {
    it('fetches current user when authenticated', async () => {
      mockIsAuthenticated = true;
      vi.mocked(api.getCurrentUser).mockResolvedValue(mockUserData);

      const { result } = renderHook(() => useCurrentUser(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockUserData);
      expect(api.getCurrentUser).toHaveBeenCalled();
    });

    it('does not fetch when not authenticated', () => {
      mockIsAuthenticated = false;

      const { result } = renderHook(() => useCurrentUser(), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.getCurrentUser).not.toHaveBeenCalled();
    });

    it('handles fetch error', async () => {
      mockIsAuthenticated = true;
      const error = new Error('Token expired');
      vi.mocked(api.getCurrentUser).mockRejectedValue(error);

      const { result } = renderHook(() => useCurrentUser(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBe(error);
    });
  });

  describe('useLogout hook', () => {
    it('calls context logout on mutation', async () => {
      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(mockLogout).toHaveBeenCalled();
    });

    it('clears API token on logout', async () => {
      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(api.setToken).toHaveBeenCalledWith(null);
    });

    it('clears query cache on success', async () => {
      const queryClient = createTestQueryClient();
      queryClient.setQueryData(['auth'], mockUserData);
      queryClient.setQueryData(['projects'], [{ id: 'project-1' }]);
      
      const clearSpy = vi.spyOn(queryClient, 'clear');

      const wrapper = ({ children }: { children: React.ReactNode }) =>
        React.createElement(QueryClientProvider, { client: queryClient }, children);

      const { result } = renderHook(() => useLogout(), { wrapper });

      await act(async () => {
        await result.current.mutateAsync();
      });

      expect(clearSpy).toHaveBeenCalled();
    });

    it('completes mutation successfully', async () => {
      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync();
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });
  });

  describe('authenticated state management', () => {
    it('returns authenticated user from context', async () => {
      mockIsAuthenticated = true;
      mockUser = {
        user_id: 'user-1',
        username: 'testuser',
        email: 'test@example.com',
      };
      vi.mocked(api.getCurrentUser).mockResolvedValue(mockUserData);

      const { result } = renderHook(() => useCurrentUser(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data?.username).toBe('testuser');
    });

    it('handles loading state from context', () => {
      mockIsLoading = true;
      mockIsAuthenticated = false;

      const { result } = renderHook(() => useCurrentUser(), {
        wrapper: createWrapper(),
      });

      // Should not fetch while context is loading
      expect(result.current.fetchStatus).toBe('idle');
    });
  });
});
