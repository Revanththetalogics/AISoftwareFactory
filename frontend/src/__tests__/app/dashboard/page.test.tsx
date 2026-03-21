import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import DashboardPage from '@/app/(dashboard)/dashboard/page';

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
  CardTitle: ({ children, className }: React.PropsWithChildren<{ className?: string }>) => (
    <h3 data-testid="card-title" className={className}>{children}</h3>
  ),
}));

// Mock system components
vi.mock('@/components/system/agent-card', () => ({
  AgentCard: ({ name, role, status }: { name: string; role: string; status: string }) => (
    <div data-testid="agent-card" data-name={name} data-role={role} data-status={status}>
      {name} - {role}
    </div>
  ),
  AgentGrid: ({ children }: React.PropsWithChildren) => <div data-testid="agent-grid">{children}</div>,
}));

vi.mock('@/components/system/metric-panel', () => ({
  MetricPanel: () => <div data-testid="metric-panel">Metric Panel</div>,
  SystemMetrics: ({ cpu, memory }: { cpu: number; memory: number }) => (
    <div data-testid="system-metrics" data-cpu={cpu} data-memory={memory}>
      System Metrics - CPU: {cpu}% Memory: {memory}%
    </div>
  ),
}));

vi.mock('@/components/system/execution-timeline', () => ({
  ExecutionTimeline: ({ phases }: { phases: unknown[] }) => (
    <div data-testid="execution-timeline" data-phases={phases.length}>
      Execution Timeline ({phases.length} phases)
    </div>
  ),
}));

vi.mock('@/components/system/log-stream', () => ({
  LogStream: () => <div data-testid="log-stream">Log Stream</div>,
  MiniLogViewer: ({ logs, limit }: { logs: unknown[]; limit: number }) => (
    <div data-testid="mini-log-viewer" data-logs={logs.length} data-limit={limit}>
      Log Viewer ({logs.length} logs)
    </div>
  ),
}));

vi.mock('@/lib/motion-variants', () => ({
  containerVariants: {},
  slideVariants: {},
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('page header', () => {
    it('renders the dashboard title', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    it('renders the dashboard subtitle', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText(/Monitor your AI Software Factory operations in real-time/i)).toBeInTheDocument();
    });

    it('renders the New Project button', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('New Project')).toBeInTheDocument();
    });

    it('New Project button has AI action variant', () => {
      render(<DashboardPage />);
      
      const buttons = screen.getAllByTestId('button');
      const newProjectButton = buttons.find(btn => btn.textContent?.includes('New Project'));
      expect(newProjectButton).toHaveAttribute('data-variant', 'ai-action');
    });
  });

  describe('system metrics section', () => {
    it('renders system metrics component', () => {
      render(<DashboardPage />);
      
      expect(screen.getByTestId('system-metrics')).toBeInTheDocument();
    });

    it('passes CPU and memory values to SystemMetrics', () => {
      render(<DashboardPage />);
      
      const metrics = screen.getByTestId('system-metrics');
      expect(metrics).toHaveAttribute('data-cpu', '45');
      expect(metrics).toHaveAttribute('data-memory', '62');
    });
  });

  describe('active agents section', () => {
    it('renders Active Agents card title', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Active Agents')).toBeInTheDocument();
    });

    it('renders agent grid', () => {
      render(<DashboardPage />);
      
      expect(screen.getByTestId('agent-grid')).toBeInTheDocument();
    });

    it('renders all agent cards', () => {
      render(<DashboardPage />);
      
      const agentCards = screen.getAllByTestId('agent-card');
      expect(agentCards).toHaveLength(4);
    });

    it('displays Backend Engineer agent', () => {
      render(<DashboardPage />);
      
      const backendAgent = screen.getByText(/Backend Engineer/);
      expect(backendAgent).toBeInTheDocument();
    });

    it('displays UX Designer agent', () => {
      render(<DashboardPage />);
      
      const uxAgent = screen.getByText(/UX Designer/);
      expect(uxAgent).toBeInTheDocument();
    });

    it('displays QA Engineer agent', () => {
      render(<DashboardPage />);
      
      const qaAgent = screen.getByText(/QA Engineer/);
      expect(qaAgent).toBeInTheDocument();
    });

    it('displays DevOps Engineer agent', () => {
      render(<DashboardPage />);
      
      const devopsAgent = screen.getByText(/DevOps Engineer/);
      expect(devopsAgent).toBeInTheDocument();
    });

    it('shows Live badge for active agents', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Live')).toBeInTheDocument();
    });
  });

  describe('project pipeline section', () => {
    it('renders Project Pipeline card', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Project Pipeline')).toBeInTheDocument();
    });

    it('renders execution timeline', () => {
      render(<DashboardPage />);
      
      expect(screen.getByTestId('execution-timeline')).toBeInTheDocument();
    });

    it('passes phases to execution timeline', () => {
      render(<DashboardPage />);
      
      const timeline = screen.getByTestId('execution-timeline');
      expect(timeline).toHaveAttribute('data-phases', '4');
    });
  });

  describe('activity logs section', () => {
    it('renders Activity Logs card title', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Activity Logs')).toBeInTheDocument();
    });

    it('renders mini log viewer', () => {
      render(<DashboardPage />);
      
      expect(screen.getByTestId('mini-log-viewer')).toBeInTheDocument();
    });

    it('displays View All button for logs', () => {
      render(<DashboardPage />);
      
      const viewAllButtons = screen.getAllByText('View All');
      expect(viewAllButtons.length).toBeGreaterThan(0);
    });
  });

  describe('recent projects section', () => {
    it('renders Recent Projects card title', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('Recent Projects')).toBeInTheDocument();
    });

    it('displays SaaS Dashboard project', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('SaaS Dashboard')).toBeInTheDocument();
    });

    it('displays E-commerce API project', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('E-commerce API')).toBeInTheDocument();
    });

    it('shows Active badge for projects', () => {
      render(<DashboardPage />);
      
      const activeBadges = screen.getAllByText('Active');
      expect(activeBadges.length).toBe(2);
    });

    it('shows project progress percentages', () => {
      render(<DashboardPage />);
      
      expect(screen.getByText('45%')).toBeInTheDocument();
      expect(screen.getByText('25%')).toBeInTheDocument();
    });
  });

  describe('layout structure', () => {
    it('renders multiple cards for different sections', () => {
      render(<DashboardPage />);
      
      const cards = screen.getAllByTestId('card');
      expect(cards.length).toBeGreaterThanOrEqual(4);
    });

    it('renders card headers for each section', () => {
      render(<DashboardPage />);
      
      const headers = screen.getAllByTestId('card-header');
      expect(headers.length).toBeGreaterThanOrEqual(4);
    });
  });
});
