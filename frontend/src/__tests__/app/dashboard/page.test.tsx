import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import DashboardPage from '@/app/(dashboard)/dashboard/page';

// Mock WebSocket hook to prevent connection attempts during tests
vi.mock('@/hooks/useFactoryWebSocket', () => ({
  useFactoryWebSocket: () => ({
    isConnected: () => false,
    sendPipelineUpdate: vi.fn(),
    sendAgentStatus: vi.fn(),
    sendWorkflowStep: vi.fn(),
    sendSystemMetric: vi.fn(),
    sendLogEntry: vi.fn(),
    sendFactoryReset: vi.fn(),
  }),
}));

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

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, className, ...props }: React.PropsWithChildren<{ className?: string }>) => (
      <div className={className} {...props}>{children}</div>
    ),
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}));

// Mock UI components
vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, className }: React.PropsWithChildren<{ className?: string }>) => (
    <span data-testid="badge" className={className}>{children}</span>
  ),
}));

vi.mock('@/components/ui/button', () => ({
  Button: ({ children, className, variant }: React.PropsWithChildren<{ className?: string; variant?: string }>) => (
    <button data-testid="button" data-variant={variant} className={className}>{children}</button>
  ),
}));

vi.mock('@/components/ui/scroll-area', () => ({
  ScrollArea: ({ children }: React.PropsWithChildren) => <div data-testid="scroll-area">{children}</div>,
}));

vi.mock('@/components/ui/card', () => ({
  Card: ({ children, className }: React.PropsWithChildren<{ className?: string }>) => (
    <div data-testid="card" className={className}>{children}</div>
  ),
  CardContent: ({ children }: React.PropsWithChildren) => <div data-testid="card-content">{children}</div>,
  CardHeader: ({ children, className }: React.PropsWithChildren<{ className?: string }>) => (
    <div data-testid="card-header" className={className}>{children}</div>
  ),
}));

vi.mock('@/components/ui/progress', () => ({
  Progress: ({ value, className, children }: { value?: number; className?: string; children?: React.ReactNode }) => (
    <div data-testid="progress" data-value={value} className={className}>{children}</div>
  ),
  ProgressTrack: ({ children }: React.PropsWithChildren) => <div data-testid="progress-track">{children}</div>,
  ProgressIndicator: ({ className }: { className?: string }) => <div data-testid="progress-indicator" className={className}></div>,
}));

describe('SuperEnhancedDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('layout structure', () => {
    it('renders 3-column layout with sidebar, main content, and right panel', () => {
      render(<DashboardPage />);
      
      // Check for layout containers
      expect(document.querySelector('.layout-container')).toBeInTheDocument();
      expect(document.querySelector('.sidebar-panel')).toBeInTheDocument();
      expect(document.querySelector('.main-content')).toBeInTheDocument();
      expect(document.querySelector('.right-panel')).toBeInTheDocument();
    });

    it('renders connection status bar in main content', () => {
      render(<DashboardPage />);
      
      // Should show either connected or disconnected status
      const statusText = screen.getByText(/Connected to factory backend|Disconnected from factory backend/);
      expect(statusText).toBeInTheDocument();
    });
  });

  describe('pipeline section', () => {
    it('renders AI Pipeline Execution section', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('AI Pipeline Execution')).toBeInTheDocument();
    });

    it('renders pipeline stepper component', () => {
      render(<DashboardPage />);
      
      // Check for pipeline phases (the actual stepper component)
      expect(screen.getByText('IDEA')).toBeInTheDocument();
      expect(screen.getByText('REQUIREMENTS')).toBeInTheDocument();
      expect(screen.getByText('ARCHITECTURE')).toBeInTheDocument();
    });

    it('renders progress bar', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Overall Progress')).toBeInTheDocument();
      expect(document.querySelector('[data-testid="progress"]')).toBeInTheDocument();
    });
  });

  describe('agent visualization section', () => {
    it('renders Agent Collaboration section', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Agent Collaboration')).toBeInTheDocument();
    });

    it('renders agent view toggle buttons', () => {
      render(<DashboardPage />);
      
      // Check that we have buttons with Grid3X3 and GitGraph icons
      const buttons = screen.getAllByTestId('button');
      const gridButtonExists = buttons.some(button => 
        button.querySelector('svg')?.classList.contains('lucide-grid-3x3')
      );
      const graphButtonExists = buttons.some(button => 
        button.querySelector('svg')?.classList.contains('lucide-git-graph')
      );
      
      expect(gridButtonExists).toBe(true);
      expect(graphButtonExists).toBe(true);
    });
  });

  describe('workflow execution section', () => {
    it('renders Workflow Execution section', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Workflow Execution')).toBeInTheDocument();
    });

    it('shows workflow step completion status', () => {
      render(<DashboardPage />);
      
      // Should show completed/pending status
      expect(screen.getByText(/\d+\/\d+ completed/)).toBeInTheDocument();
    });
  });

  describe('control panel', () => {
    it('renders factory controls section', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Factory Controls')).toBeInTheDocument();
    });

    it('renders control buttons', () => {
      render(<DashboardPage />);
      
      // Look for buttons specifically in the control panel section
      const controlPanel = screen.getByText('Factory Controls').closest('section');
      const pauseButton = controlPanel?.querySelector('button');
      
      expect(pauseButton).toBeInTheDocument();
      expect(screen.getByText('Reset')).toBeInTheDocument();
      
      // Check for either Running or Resume text (there might be multiple)
      const runningElements = screen.queryAllByText(/Running|Resume/);
      expect(runningElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('right panel tabs', () => {
    it('renders Live Logs and Health tabs', () => {
      render(<DashboardPage />);
      
      // Check that we have the tab elements
      const liveLogsTabs = screen.queryAllByText('Live Logs');
      const healthTabs = screen.queryAllByText('Health');
      
      expect(liveLogsTabs.length).toBeGreaterThanOrEqual(1);
      expect(healthTabs.length).toBeGreaterThanOrEqual(1);
    });

    it('renders live log console elements', () => {
      render(<DashboardPage />);
      
      // Check that we have at least one instance of Live Logs text
      const liveLogsElements = screen.queryAllByText('Live Logs');
      expect(liveLogsElements.length).toBeGreaterThanOrEqual(1);
      
      // Check for entries badge
      const entriesElements = screen.queryAllByText(/entries/);
      expect(entriesElements.length).toBeGreaterThanOrEqual(1);
    });

    it('renders system health monitor elements', () => {
      render(<DashboardPage />);
      
      // Check for basic health monitoring elements
      expect(screen.getByText('Health')).toBeInTheDocument();
      
      // Check for any system/resource related text - be flexible about exact wording
      const healthRelatedElements = screen.queryAllByText(/System|Health|CPU|Memory|Storage|Resource/i);
      expect(healthRelatedElements.length).toBeGreaterThanOrEqual(1);
    });
  });
});