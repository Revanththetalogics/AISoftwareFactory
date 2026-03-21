import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Track router.push calls
const mockRouterPush = vi.fn();
const mockUsePathname = vi.fn();

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockRouterPush,
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => mockUsePathname(),
}));

// Mock useAuth hook
const mockUseAuth = vi.fn();
vi.mock('@/lib/auth', () => ({
  useAuth: () => mockUseAuth(),
}));

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUsePathname.mockReturnValue('/dashboard');
  });

  describe('loading state', () => {
    it('shows loading spinner when isLoading is true', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        isLoading: true,
        user: null,
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      // Should show spinner (the animate-spin class indicates spinner)
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
      
      // Should not show children
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });

  describe('authenticated users', () => {
    it('renders children when user is authenticated', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
        user: { 
          user_id: 'user-123',
          username: 'testuser',
          permissions: ['read', 'write'],
        },
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('does not redirect authenticated users', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
        user: { 
          user_id: 'user-123',
          username: 'testuser',
          permissions: ['admin'],
        },
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(mockRouterPush).not.toHaveBeenCalled();
    });
  });

  describe('unauthenticated users', () => {
    it('redirects to /login when not authenticated', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        isLoading: false,
        user: null,
      });
      mockUsePathname.mockReturnValue('/dashboard');

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      await waitFor(() => {
        expect(mockRouterPush).toHaveBeenCalledWith(
          '/login?returnUrl=%2Fdashboard'
        );
      });
    });

    it('includes return URL in redirect', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        isLoading: false,
        user: null,
      });
      mockUsePathname.mockReturnValue('/projects/123');

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      await waitFor(() => {
        expect(mockRouterPush).toHaveBeenCalledWith(
          '/login?returnUrl=%2Fprojects%2F123'
        );
      });
    });

    it('renders null while redirecting', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        isLoading: false,
        user: null,
      });

      const { container } = render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
      expect(container.innerHTML).toBe('');
    });
  });

  describe('login page behavior', () => {
    it('skips auth check on login page', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        isLoading: false,
        user: null,
      });
      mockUsePathname.mockReturnValue('/login');

      render(
        <ProtectedRoute>
          <div>Login Form</div>
        </ProtectedRoute>
      );

      // Give time for useEffect to run
      await new Promise(resolve => setTimeout(resolve, 50));

      // Should not redirect on login page
      expect(mockRouterPush).not.toHaveBeenCalled();
    });
  });

  describe('permission-based access', () => {
    it('renders children when user has required permissions', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
        user: {
          user_id: 'user-123',
          username: 'testuser',
          permissions: ['read', 'write', 'delete'],
        },
      });

      render(
        <ProtectedRoute requiredPermissions={['read', 'write']}>
          <div>Admin Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Admin Content')).toBeInTheDocument();
    });

    it('redirects to /unauthorized when user lacks permissions', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
        user: {
          user_id: 'user-123',
          username: 'testuser',
          permissions: ['read'],
        },
      });

      render(
        <ProtectedRoute requiredPermissions={['admin']}>
          <div>Admin Content</div>
        </ProtectedRoute>
      );

      await waitFor(() => {
        expect(mockRouterPush).toHaveBeenCalledWith('/unauthorized');
      });
    });

    it('allows admin users to access any protected route', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
        user: {
          user_id: 'admin-123',
          username: 'admin',
          permissions: ['admin'],
        },
      });

      render(
        <ProtectedRoute requiredPermissions={['special-permission']}>
          <div>Special Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Special Content')).toBeInTheDocument();
      expect(mockRouterPush).not.toHaveBeenCalledWith('/unauthorized');
    });

    it('renders children when no permissions are required', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        isLoading: false,
        user: {
          user_id: 'user-123',
          username: 'testuser',
          permissions: [],
        },
      });

      render(
        <ProtectedRoute>
          <div>Public Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Public Protected Content')).toBeInTheDocument();
    });
  });
});
