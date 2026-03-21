import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AgentCard, AgentGrid, type AgentRole, type AgentStatus } from '@/components/system/agent-card';

// Mock framer-motion - filter out framer-motion specific props from DOM
vi.mock('framer-motion', () => ({
  motion: {
    div: (props: React.PropsWithChildren<{ onClick?: () => void; className?: string }>) => {
      const { children, onClick, className } = props;
      return <div onClick={onClick} className={className}>{children}</div>;
    },
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}));

// Mock tooltip
vi.mock('@/components/ui/tooltip', () => ({
  TooltipProvider: ({ children }: React.PropsWithChildren) => <>{children}</>,
  Tooltip: ({ children }: React.PropsWithChildren) => <>{children}</>,
  TooltipTrigger: ({ children }: React.PropsWithChildren) => <>{children}</>,
  TooltipContent: ({ children }: React.PropsWithChildren) => <div data-testid="tooltip">{children}</div>,
}));

// Mock progress
vi.mock('@/components/ui/progress', () => ({
  Progress: ({ value }: { value: number }) => (
    <div role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
      {value}%
    </div>
  ),
}));

const defaultProps = {
  agentId: 'agent-123',
  role: 'executor' as AgentRole,
  status: 'idle' as AgentStatus,
};

describe('AgentCard', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<AgentCard {...defaultProps} />);
      expect(screen.getByText('agent-123')).toBeInTheDocument();
    });

    it('renders agent name when provided', () => {
      render(<AgentCard {...defaultProps} name="Backend Engineer" />);
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    });

    it('shows agent ID as fallback when no name', () => {
      render(<AgentCard {...defaultProps} />);
      expect(screen.getByText('agent-123')).toBeInTheDocument();
    });

    it('displays role label', () => {
      render(<AgentCard {...defaultProps} role="orchestrator" />);
      expect(screen.getByText('orchestrator')).toBeInTheDocument();
    });

    it('displays truncated agent ID', () => {
      render(<AgentCard {...defaultProps} agentId="agent-12345678" />);
      expect(screen.getByText('agent-12')).toBeInTheDocument();
    });
  });

  describe('roles', () => {
    const roles: AgentRole[] = ['orchestrator', 'executor', 'validator', 'deployer'];
    
    roles.forEach(role => {
      it(`renders ${role} role correctly`, () => {
        render(<AgentCard {...defaultProps} role={role} />);
        expect(screen.getByText(role)).toBeInTheDocument();
      });
    });
  });

  describe('statuses', () => {
    const statuses: AgentStatus[] = ['idle', 'running', 'success', 'error', 'queued'];
    
    statuses.forEach(status => {
      it(`renders ${status} status correctly`, () => {
        render(<AgentCard {...defaultProps} status={status} />);
        const statusDot = screen.getByTitle(`Status: ${status}`);
        expect(statusDot).toBeInTheDocument();
      });
    });

    it('shows error message for error status', () => {
      render(<AgentCard {...defaultProps} status="error" />);
      expect(screen.getByText('Agent encountered an error')).toBeInTheDocument();
    });
  });

  describe('current task', () => {
    it('displays current task when provided', () => {
      render(<AgentCard {...defaultProps} currentTask="Processing API requests" />);
      expect(screen.getByText('Processing API requests')).toBeInTheDocument();
    });

    it('shows Current Task label', () => {
      render(<AgentCard {...defaultProps} currentTask="Any task" />);
      expect(screen.getByText('Current Task')).toBeInTheDocument();
    });

    it('does not show task section when no task', () => {
      render(<AgentCard {...defaultProps} />);
      expect(screen.queryByText('Current Task')).not.toBeInTheDocument();
    });
  });

  describe('progress', () => {
    it('shows progress bar when running with progress', () => {
      render(<AgentCard {...defaultProps} status="running" progress={50} />);
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('displays correct progress value', () => {
      render(<AgentCard {...defaultProps} status="running" progress={75} />);
      // Progress value appears in both the display and the mocked progress bar
      expect(screen.getAllByText('75%').length).toBeGreaterThan(0);
    });

    it('does not show progress for idle status', () => {
      render(<AgentCard {...defaultProps} status="idle" progress={50} />);
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    it('does not show progress when progress is 0', () => {
      render(<AgentCard {...defaultProps} status="running" progress={0} />);
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  describe('metrics', () => {
    const metrics = {
      tasksCompleted: 25,
      avgExecutionTime: '1.5s',
      successRate: 92.5,
      totalTokens: 15000,
      activeDuration: '2h 30m',
    };

    it('displays metrics when provided', () => {
      render(<AgentCard {...defaultProps} metrics={metrics} />);
      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText('1.5s')).toBeInTheDocument();
      expect(screen.getByText('93%')).toBeInTheDocument(); // successRate.toFixed(0)
    });

    it('hides metrics in compact mode', () => {
      render(<AgentCard {...defaultProps} metrics={metrics} compact />);
      expect(screen.queryByText('Completed')).not.toBeInTheDocument();
    });

    it('shows metric labels', () => {
      render(<AgentCard {...defaultProps} metrics={metrics} />);
      expect(screen.getByText('Completed')).toBeInTheDocument();
      expect(screen.getByText('Avg Time')).toBeInTheDocument();
      expect(screen.getByText('Success Rate')).toBeInTheDocument();
    });
  });

  describe('interactions', () => {
    it('calls onClick when clicked', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();
      render(<AgentCard {...defaultProps} onClick={handleClick} />);
      
      await user.click(screen.getByText('agent-123'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('toggles details when no onClick provided', async () => {
      const user = userEvent.setup();
      const metrics = {
        tasksCompleted: 25,
        avgExecutionTime: '1.5s',
        successRate: 92.5,
        totalTokens: 15000,
        activeDuration: '2h 30m',
      };
      
      render(<AgentCard {...defaultProps} metrics={metrics} />);
      
      // Click to expand
      await user.click(screen.getByText('agent-123'));
      
      // Should show expanded details
      expect(screen.getByText('Total Tokens')).toBeInTheDocument();
    });
  });

  describe('compact mode', () => {
    it('applies compact padding', () => {
      const { container } = render(<AgentCard {...defaultProps} compact />);
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain('p-3');
    });

    it('applies normal padding when not compact', () => {
      const { container } = render(<AgentCard {...defaultProps} />);
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain('p-4');
    });
  });

  describe('custom className', () => {
    it('applies custom className', () => {
      const { container } = render(<AgentCard {...defaultProps} className="custom-class" />);
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain('custom-class');
    });
  });
});

describe('AgentGrid', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(
        <AgentGrid>
          <div>Child 1</div>
          <div>Child 2</div>
        </AgentGrid>
      );
      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
    });

    it('renders children in grid', () => {
      const { container } = render(
        <AgentGrid>
          <div>Item</div>
        </AgentGrid>
      );
      const grid = container.firstChild as HTMLElement;
      expect(grid.className).toContain('grid');
    });
  });

  describe('columns', () => {
    it('uses auto columns by default', () => {
      const { container } = render(
        <AgentGrid>
          <div>Item</div>
        </AgentGrid>
      );
      const grid = container.firstChild as HTMLElement;
      expect(grid.className).toContain('grid-cols-1');
    });

    it('applies custom column count', () => {
      const { container } = render(
        <AgentGrid columns={2}>
          <div>Item</div>
        </AgentGrid>
      );
      const grid = container.firstChild as HTMLElement;
      expect(grid.className).toContain('grid-cols-2');
    });
  });

  describe('styling', () => {
    it('has gap between items', () => {
      const { container } = render(
        <AgentGrid>
          <div>Item</div>
        </AgentGrid>
      );
      const grid = container.firstChild as HTMLElement;
      expect(grid.className).toContain('gap-4');
    });

    it('applies custom className', () => {
      const { container } = render(
        <AgentGrid className="custom-grid">
          <div>Item</div>
        </AgentGrid>
      );
      const grid = container.firstChild as HTMLElement;
      expect(grid.className).toContain('custom-grid');
    });
  });
});

describe('AgentCard with AgentGrid', () => {
  it('renders multiple cards in grid', () => {
    render(
      <AgentGrid>
        <AgentCard agentId="agent-1" role="orchestrator" status="idle" />
        <AgentCard agentId="agent-2" role="executor" status="running" />
        <AgentCard agentId="agent-3" role="validator" status="success" />
      </AgentGrid>
    );
    
    // Use getAllByText since each agent ID appears twice (in title and truncated form)
    expect(screen.getAllByText('agent-1').length).toBeGreaterThan(0);
    expect(screen.getAllByText('agent-2').length).toBeGreaterThan(0);
    expect(screen.getAllByText('agent-3').length).toBeGreaterThan(0);
  });
});
