'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
}

export function ProtectedRoute({ children, requiredPermissions }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Skip auth check for login page
    if (pathname === '/login') return;

    console.log('ProtectedRoute Check:', { 
      isAuthenticated, 
      isLoading, 
      pathname,
      hasUser: !!user 
    });

    if (!isLoading && !isAuthenticated) {
      console.log('Redirecting to login, returnUrl:', pathname);
      // Redirect to login with return URL
      const returnUrl = encodeURIComponent(pathname);
      router.push(`/login?returnUrl=${returnUrl}`);
    }
  }, [isAuthenticated, isLoading, router, pathname]);

  // Check permissions if required
  const hasPermission = !requiredPermissions ||
    requiredPermissions.every(permission =>
      user?.permissions?.includes(permission) || user?.permissions?.includes('admin')
    );

  useEffect(() => {
    if (!isLoading && isAuthenticated && !hasPermission) {
      router.push('/unauthorized');
    }
  }, [isAuthenticated, isLoading, hasPermission, router]);

  if (isLoading) {
    console.log('ProtectedRoute: Loading...');
    return (
      <div className="flex items-center justify-center min-h-screen bg-bg-base">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-state-running"></div>
      </div>
    );
  }

  if (!isAuthenticated || !hasPermission) {
    console.log('ProtectedRoute: Not authenticated or no permission, rendering null');
    return null;
  }

  console.log('ProtectedRoute: Authenticated, rendering children');
  return <>{children}</>;
}
