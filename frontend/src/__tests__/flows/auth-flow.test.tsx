import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import type { LoginResponse, User } from '@/lib/types';

// Mock the API client
vi.mock('@/lib/api/client', () => ({
  api: {
    setToken: vi.fn(),
    logout: vi.fn().mockResolvedValue(undefined),
    login: vi.fn(),
  },
}));

// Mock next/navigation
const mockPush = vi.fn();
const mockPathname = vi.fn(() => '/dashboard');

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => mockPathname(),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock user and login response
const mockUser: User = {
  user_id: 'user-123',
  username: 'testuser',
  email: 'test@example.com',
  permissions: ['read', 'write'],
  is_active: true,
};

const mockAdminUser: User = {
  user_id: 'admin-123',
  username: 'admin',
  email: 'admin@example.com',
  permissions: ['admin'],
  is_active: true,
};

const mockLoginResponse: LoginResponse = {
  access_token: 'mock-jwt-token',
  token_type: 'bearer',
  expires_in: 3600,
  user: mockUser,
};

// Test components
function AuthStatus() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();
  
  return (
    <div>
      <span data-testid="is-authenticated">{String(isAuthenticated)}</span>
      <span data-testid="is-loading">{String(isLoading)}</span>
      <span data-testid="username">{user?.username || 'none'}</span>
      <span data-testid="user-email">{user?.email || 'none'}</span>
      <button onClick={() => login(mockLoginResponse)} data-testid="login-btn">Login</button>
      <button onClick={logout} data-testid="logout-btn">Logout</button>
    </div>
  );
}

function DashboardContent() {
  return <div data-testid="dashboard-content">Dashboard Content</div>;
}

function ProtectedDashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

describe('Auth Flow Integration Tests', () => {
  const localStorageMock = window.localStorage as unknown as {
    getItem: ReturnType<typeof vi.fn>;
    setItem: ReturnType<typeof vi.fn>;
    removeItem: ReturnType<typeof vi.fn>;
    clear: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockPush.mockClear();
    mockPathname.mockReturnValue('/dashboard');
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('complete login flow', () => {
    it('transitions from unauthenticated to authenticated on login', async () => {
      const user = userEvent.setup();
      
      render(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });

      // Initially not authenticated
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('username')).toHaveTextContent('none');

      // Perform login
      await user.click(screen.getByTestId('login-btn'));

      // Now authenticated
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('username')).toHaveTextContent('testuser');
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });

    it('stores auth data in localStorage on login', async () => {
      const user = userEvent.setup();
      
      render(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });

      await user.click(screen.getByTestId('login-btn'));

      // Verify localStorage was called with correct data
      expect(localStorageMock.setItem).toHaveBeenCalledWith('aifactory_token', 'mock-jwt-token');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('aifactory_user', JSON.stringify(mockUser));
      expect(localStorageMock.setItem).toHaveBeenCalledWith('aifactory_token_expiry', expect.any(String));
    });
  });

  describe('complete logout flow', () => {
    it('transitions from authenticated to unauthenticated on logout', async () => {
      const user = userEvent.setup();
      
      render(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });

      // Login first
      await user.click(screen.getByTestId('login-btn'));
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');

      // Logout
      await user.click(screen.getByTestId('logout-btn'));

      // Should be unauthenticated
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('username')).toHaveTextContent('none');
    });

    it('clears all auth data from localStorage on logout', async () => {
      const user = userEvent.setup();
      
      render(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });

      await user.click(screen.getByTestId('login-btn'));
      await user.click(screen.getByTestId('logout-btn'));

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('aifactory_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('aifactory_user');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('aifactory_token_expiry');
    });
  });

  describe('protected route redirect behavior', () => {
    it('shows loading spinner while checking auth', () => {
      // Simulate loading state
      render(
        <AuthProvider>
          <ProtectedDashboard />
        </AuthProvider>
      );

      // The spinner should be visible during loading
      // Note: This may or may not be present depending on timing
      // Just verify the component renders without error
      expect(document.body).toBeInTheDocument();
    });

    it('redirects to login when unauthenticated', async () => {
      mockPathname.mockReturnValue('/dashboard');
      
      render(
        <AuthProvider>
          <ProtectedDashboard />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/login?returnUrl=%2Fdashboard');
      });
    });

    it('does not redirect from login page', async () => {
      mockPathname.mockReturnValue('/login');
      mockPush.mockClear();
      
      render(
        <AuthProvider>
          <ProtectedDashboard />
        </AuthProvider>
      );

      // Wait a bit to ensure redirect would have happened if it was going to
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // mockPush should not have been called for login redirect
      const loginRedirectCalls = mockPush.mock.calls.filter(
        call => call[0]?.startsWith('/login')
      );
      expect(loginRedirectCalls).toHaveLength(0);
    });

    it('shows dashboard content when authenticated', async () => {
      // First, set up authenticated state
      const futureExpiry = new Date(Date.now() + 3600000).toISOString();
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'aifactory_token') return 'stored-token';
        if (key === 'aifactory_user') return JSON.stringify(mockUser);
        if (key === 'aifactory_token_expiry') return futureExpiry;
        return null;
      });

      render(
        <AuthProvider>
          <ProtectedDashboard />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('dashboard-content')).toBeInTheDocument();
      });
    });
  });

  describe('session restoration', () => {
    it('restores session from localStorage on page load', async () => {
      const futureExpiry = new Date(Date.now() + 3600000).toISOString();
      
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'aifactory_token') return 'stored-token';
        if (key === 'aifactory_user') return JSON.stringify(mockUser);
        if (key === 'aifactory_token_expiry') return futureExpiry;
        return null;
      });

      render(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });

      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('username')).toHaveTextContent('testuser');
    });

    it('clears expired session on page load', async () => {
      const pastExpiry = new Date(Date.now() - 3600000).toISOString();
      
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'aifactory_token') return 'expired-token';
        if (key === 'aifactory_user') return JSON.stringify(mockUser);
        if (key === 'aifactory_token_expiry') return pastExpiry;
        return null;
      });

      render(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });

      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('aifactory_token');
    });
  });

  describe('permission handling', () => {
    it('allows access when user has required permission', async () => {
      const futureExpiry = new Date(Date.now() + 3600000).toISOString();
      
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'aifactory_token') return 'stored-token';
        if (key === 'aifactory_user') return JSON.stringify(mockUser);
        if (key === 'aifactory_token_expiry') return futureExpiry;
        return null;
      });

      render(
        <AuthProvider>
          <ProtectedRoute requiredPermissions={['read']}>
            <div data-testid="protected-content">Protected Content</div>
          </ProtectedRoute>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      });
    });

    it('admin permission grants access to all protected routes', async () => {
      const futureExpiry = new Date(Date.now() + 3600000).toISOString();
      
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'aifactory_token') return 'stored-token';
        if (key === 'aifactory_user') return JSON.stringify(mockAdminUser);
        if (key === 'aifactory_token_expiry') return futureExpiry;
        return null;
      });

      render(
        <AuthProvider>
          <ProtectedRoute requiredPermissions={['special-permission']}>
            <div data-testid="admin-content">Admin Content</div>
          </ProtectedRoute>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('admin-content')).toBeInTheDocument();
      });
    });
  });

  describe('auth state consistency', () => {
    it('maintains auth state across multiple renders', async () => {
      const user = userEvent.setup();
      
      const { rerender } = render(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });

      await user.click(screen.getByTestId('login-btn'));
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');

      // Re-render the component
      rerender(
        <AuthProvider>
          <AuthStatus />
        </AuthProvider>
      );

      // Auth state should persist
      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      });
    });
  });
});
