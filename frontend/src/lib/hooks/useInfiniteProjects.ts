'use client';

import { useInfiniteQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

export function useInfiniteProjects() {
  return useInfiniteQuery({
    queryKey: ['projects', 'infinite'],
    queryFn: ({ pageParam = 0 }) => 
      api.getProjects().then(projects => ({
        projects: projects.slice(pageParam * 20, (pageParam + 1) * 20),
        nextPage: (pageParam + 1) * 20 < projects.length ? pageParam + 1 : undefined,
      })),
    getNextPageParam: (lastPage) => lastPage.nextPage,
    initialPageParam: 0,
  });
}
