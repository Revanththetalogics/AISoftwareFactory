'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { useAuth as useAuthContext } from '@/lib/auth';
import type { LoginRequest, RegisterRequest, User } from '@/lib/types';

const AUTH_KEY = 'auth';

export function useLogin() {
  const { login } = useAuthContext();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginRequest) => api.login(data),
    onSuccess: (response) => {
      login(response);
      // Build User from flat login response fields for the query cache
      const cachedUser: User = {
        user_id: response.user_id,
        username: response.username,
        email: response.email,
        permissions: response.permissions,
        is_active: true,
      };
      queryClient.setQueryData([AUTH_KEY], cachedUser);
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: RegisterRequest) => api.register(data),
  });
}

export function useCurrentUser() {
  const { isAuthenticated } = useAuthContext();

  return useQuery({
    queryKey: [AUTH_KEY, 'me'],
    queryFn: () => api.getCurrentUser(),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useLogout() {
  const { logout } = useAuthContext();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      // AuthContext.logout awaits api.logout(), clears localStorage and api token
      await logout();
    },
    onSuccess: () => {
      queryClient.clear();
    },
  });
}
