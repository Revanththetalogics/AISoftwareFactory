import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Sidebar } from '@/components/layout/sidebar';

// Mock next/navigation with different pathnames
const mockPathname = vi.fn(() => '/dashboard');

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => mockPathname(),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock the sidebar sub-components
vi.mock('@/components/layout/sidebar-section', () => ({
  SidebarSection: ({ title, items, pathname }: { title: string; items: { label: string; href: string }[]; pathname: string }) => (
    <div data-testid={`section-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <h3>{title}</h3>
      {items.map((item) => (
        <a 
          key={item.href} 
          href={item.href} 
          data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
          data-active={pathname === item.href || pathname.startsWith(`${item.href}/`)}
        >
          {item.label}
        </a>
      ))}
    </div>
  ),
}));

vi.mock('@/components/layout/sidebar-stats', () => ({
  SidebarStats: () => <div data-testid="sidebar-stats">Stats</div>,
}));

describe('Sidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPathname.mockReturnValue('/dashboard');
  });

  describe('rendering', () => {
    it('renders the sidebar component', () => {
      render(<Sidebar />);
      
      // Check for logo/brand
      expect(screen.getByText('AI Factory')).toBeInTheDocument();
      expect(screen.getByText('Software Engineering')).toBeInTheDocument();
    });

    it('renders main navigation items', () => {
      render(<Sidebar />);
      
      // Check main nav items are present
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Projects')).toBeInTheDocument();
    });

    it('renders sidebar sections', () => {
      render(<Sidebar />);
      
      // Check section titles
      expect(screen.getByTestId('section-ai-agents')).toBeInTheDocument();
      expect(screen.getByTestId('section-code-generation')).toBeInTheDocument();
      expect(screen.getByTestId('section-testing-&-qa')).toBeInTheDocument();
      expect(screen.getByTestId('section-infrastructure')).toBeInTheDocument();
      expect(screen.getByTestId('section-observability')).toBeInTheDocument();
    });

    it('renders settings in bottom navigation', () => {
      render(<Sidebar />);
      
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('renders sidebar stats component', () => {
      render(<Sidebar />);
      
      expect(screen.getByTestId('sidebar-stats')).toBeInTheDocument();
    });
  });

  describe('navigation links', () => {
    it('contains correct href for Dashboard link', () => {
      render(<Sidebar />);
      
      const dashboardLinks = screen.getAllByText('Dashboard');
      const dashboardLink = dashboardLinks[0].closest('a');
      expect(dashboardLink).toHaveAttribute('href', '/dashboard');
    });

    it('contains correct href for Projects link', () => {
      render(<Sidebar />);
      
      const projectsLink = screen.getByText('Projects').closest('a');
      expect(projectsLink).toHaveAttribute('href', '/projects');
    });

    it('contains correct href for Settings link', () => {
      render(<Sidebar />);
      
      const settingsLink = screen.getByText('Settings').closest('a');
      expect(settingsLink).toHaveAttribute('href', '/settings');
    });
  });

  describe('active state highlighting', () => {
    it('highlights Dashboard when on /dashboard path', () => {
      mockPathname.mockReturnValue('/dashboard');
      render(<Sidebar />);
      
      const dashboardButtons = screen.getAllByText('Dashboard');
      // Find the button within the main nav (not in sections)
      const dashboardButton = dashboardButtons[0].closest('button');
      expect(dashboardButton?.className).toContain('bg-state-running-dim');
    });

    it('highlights Projects when on /projects path', () => {
      mockPathname.mockReturnValue('/projects');
      render(<Sidebar />);
      
      const projectsButton = screen.getByText('Projects').closest('button');
      expect(projectsButton?.className).toContain('bg-state-running-dim');
    });

    it('highlights nested paths correctly', () => {
      mockPathname.mockReturnValue('/projects/123');
      render(<Sidebar />);
      
      const projectsButton = screen.getByText('Projects').closest('button');
      // Should still be active for child routes
      expect(projectsButton?.className).toContain('bg-state-running-dim');
    });

    it('does not highlight inactive items', () => {
      mockPathname.mockReturnValue('/dashboard');
      render(<Sidebar />);
      
      const projectsButton = screen.getByText('Projects').closest('button');
      expect(projectsButton?.className).not.toContain('bg-state-running-dim');
      expect(projectsButton?.className).toContain('text-text-secondary');
    });
  });

  describe('section navigation items', () => {
    it('renders AI Agents section items', () => {
      render(<Sidebar />);
      
      expect(screen.getByTestId('nav-agent-crews')).toBeInTheDocument();
      expect(screen.getByTestId('nav-workflows')).toBeInTheDocument();
      expect(screen.getByTestId('nav-knowledge-base')).toBeInTheDocument();
    });

    it('renders Code Generation section items', () => {
      render(<Sidebar />);
      
      expect(screen.getByTestId('nav-code-generator')).toBeInTheDocument();
      expect(screen.getByTestId('nav-architecture')).toBeInTheDocument();
      expect(screen.getByTestId('nav-file-manager')).toBeInTheDocument();
    });

    it('renders Testing & QA section items', () => {
      render(<Sidebar />);
      
      expect(screen.getByTestId('nav-testing')).toBeInTheDocument();
      expect(screen.getByTestId('nav-simulations')).toBeInTheDocument();
      expect(screen.getByTestId('nav-visual-regression')).toBeInTheDocument();
    });

    it('renders Infrastructure section items', () => {
      render(<Sidebar />);
      
      expect(screen.getByTestId('nav-deployment')).toBeInTheDocument();
      expect(screen.getByTestId('nav-infrastructure')).toBeInTheDocument();
      expect(screen.getByTestId('nav-database')).toBeInTheDocument();
    });

    it('renders Observability section items', () => {
      render(<Sidebar />);
      
      expect(screen.getByTestId('nav-monitoring')).toBeInTheDocument();
      expect(screen.getByTestId('nav-security')).toBeInTheDocument();
      expect(screen.getByTestId('nav-performance')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('renders as an aside element for semantic navigation', () => {
      render(<Sidebar />);
      
      const sidebar = document.querySelector('aside');
      expect(sidebar).toBeInTheDocument();
    });

    it('renders navigation items as links', () => {
      render(<Sidebar />);
      
      const links = screen.getAllByRole('link');
      expect(links.length).toBeGreaterThan(0);
    });
  });
});
