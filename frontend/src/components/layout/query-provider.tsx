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
            staleTime: 30000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthTokenSync />
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
