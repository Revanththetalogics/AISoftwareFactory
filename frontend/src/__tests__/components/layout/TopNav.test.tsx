import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TopNav } from '@/components/layout/top-nav';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/dashboard',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock next-themes
vi.mock('next-themes', () => ({
  useTheme: () => ({
    theme: 'dark',
    setTheme: vi.fn(),
  }),
}));

// Mock auth
const mockLogout = vi.fn();
vi.mock('@/lib/auth', () => ({
  useAuth: () => ({
    user: {
      user_id: 'user-123',
      username: 'TestUser',
      email: 'test@example.com',
      permissions: ['read', 'write'],
      is_active: true,
    },
    isAuthenticated: true,
    logout: mockLogout,
  }),
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}));

// Mock sub-components with simpler implementations
vi.mock('@/components/layout/user-profile', () => ({
  ThemeToggle: () => (
    <button data-testid="theme-toggle">Toggle Theme</button>
  ),
  UserProfile: () => (
    <div data-testid="user-profile">
      <button data-testid="user-menu-trigger">TU</button>
      <span>TestUser</span>
      <span>test@example.com</span>
    </div>
  ),
}));

vi.mock('@/components/layout/notification-center', () => ({
  NotificationCenter: () => (
    <button data-testid="notification-center">Notifications</button>
  ),
}));

describe('TopNav', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders the top navigation component', () => {
      render(<TopNav />);
      
      // Should render as a header element
      const header = document.querySelector('header');
      expect(header).toBeInTheDocument();
    });

    it('renders search input', () => {
      render(<TopNav />);
      
      const searchInput = screen.getByPlaceholderText(/search projects, agents, or tasks/i);
      expect(searchInput).toBeInTheDocument();
    });

    it('renders theme toggle', () => {
      render(<TopNav />);
      
      expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
    });

    it('renders notification center', () => {
      render(<TopNav />);
      
      expect(screen.getByTestId('notification-center')).toBeInTheDocument();
    });

    it('renders user profile', () => {
      render(<TopNav />);
      
      expect(screen.getByTestId('user-profile')).toBeInTheDocument();
    });
  });

  describe('search functionality', () => {
    it('allows typing in search input', async () => {
      const user = userEvent.setup();
      render(<TopNav />);
      
      const searchInput = screen.getByPlaceholderText(/search projects, agents, or tasks/i);
      await user.type(searchInput, 'test query');
      
      expect(searchInput).toHaveValue('test query');
    });

    it('clears search on change', async () => {
      const user = userEvent.setup();
      render(<TopNav />);
      
      const searchInput = screen.getByPlaceholderText(/search projects, agents, or tasks/i);
      await user.type(searchInput, 'initial');
      await user.clear(searchInput);
      
      expect(searchInput).toHaveValue('');
    });

    it('search input has correct type attribute', () => {
      render(<TopNav />);
      
      const searchInput = screen.getByPlaceholderText(/search projects, agents, or tasks/i);
      expect(searchInput).toHaveAttribute('type', 'search');
    });
  });

  describe('user profile display', () => {
    it('shows user information when authenticated', () => {
      render(<TopNav />);
      
      expect(screen.getByText('TestUser')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });

    it('displays user avatar/initials', () => {
      render(<TopNav />);
      
      // User initials should be shown
      expect(screen.getByText('TU')).toBeInTheDocument();
    });
  });

  describe('layout and positioning', () => {
    it('has top-navbar class', () => {
      render(<TopNav />);
      
      const header = document.querySelector('header');
      expect(header?.className).toContain('top-navbar');
    });

    it('positions content with flex justify-between', () => {
      render(<TopNav />);
      
      const header = document.querySelector('header');
      const flexContainer = header?.querySelector('.flex.items-center.justify-between');
      expect(flexContainer).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('renders as a header element for semantic navigation', () => {
      render(<TopNav />);
      
      const header = document.querySelector('header');
      expect(header).toBeInTheDocument();
    });

    it('search input is focusable', () => {
      render(<TopNav />);
      
      const searchInput = screen.getByPlaceholderText(/search projects, agents, or tasks/i);
      searchInput.focus();
      expect(document.activeElement).toBe(searchInput);
    });
  });
});
