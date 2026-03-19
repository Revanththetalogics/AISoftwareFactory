'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

const METADATA_KEY = 'metadata';

export function useAvailablePhases() {
  return useQuery({
    queryKey: [METADATA_KEY, 'phases'],
    queryFn: () => api.getAvailablePhases(),
    staleTime: 10 * 60 * 1000, // 10 minutes - phases rarely change
  });
}

export function useAvailableRoles() {
  return useQuery({
    queryKey: [METADATA_KEY, 'roles'],
    queryFn: () => api.getAvailableRoles(),
    staleTime: 10 * 60 * 1000, // 10 minutes - roles rarely change
  });
}

export function useAvailableEnvironments() {
  return useQuery({
    queryKey: [METADATA_KEY, 'environments'],
    queryFn: () => api.getAvailableEnvironments(),
    staleTime: 10 * 60 * 1000, // 10 minutes - environments rarely change
  });
}
