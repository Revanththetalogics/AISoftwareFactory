'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, useEffect, type ReactNode } from 'react';
import { api } from '@/lib/api/client';
import { useAuth } from '@/lib/auth';

interface QueryProviderProps {
  children: ReactNode;
}

function AuthTokenSync() {
  const { getToken, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      const token = getToken();
      api.setToken(token);
    } else {
      api.setToken(null);
    }
  }, [isAuthenticated, getToken]);

  return null;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Optimized for real-time dashboard
            staleTime: 5 * 1000, // 5 seconds - data is fresh for 5s
            gcTime: 30 * 1000, // 30 seconds - cache persists for 30s after unmount
            refetchOnWindowFocus: true, // Refetch when user returns to tab
            retry: 3, // Retry failed requests up to 3 times
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000), // Exponential backoff
            refetchOnReconnect: true, // Refetch on network reconnect
            throwOnError: false, // Don't throw errors by default
          },
          mutations: {
            retry: 1, // Retry mutations once
            throwOnError: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthTokenSync />
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
