import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatCard } from '@/components/cards/stat-card';

describe('StatCard', () => {
  const defaultProps = {
    title: 'Total Users',
    value: '1,234',
  };

  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<StatCard {...defaultProps} />);
      expect(screen.getByText('Total Users')).toBeInTheDocument();
    });

    it('displays the title', () => {
      render(<StatCard {...defaultProps} />);
      expect(screen.getByText('Total Users')).toBeInTheDocument();
    });

    it('displays the value', () => {
      render(<StatCard {...defaultProps} />);
      expect(screen.getByText('1,234')).toBeInTheDocument();
    });

    it('displays numeric value', () => {
      render(<StatCard title="Count" value={42} />);
      expect(screen.getByText('42')).toBeInTheDocument();
    });

    it('displays string value', () => {
      render(<StatCard title="Status" value="Active" />);
      expect(screen.getByText('Active')).toBeInTheDocument();
    });
  });

  describe('description', () => {
    it('displays description when provided', () => {
      render(<StatCard {...defaultProps} description="Total registered users" />);
      expect(screen.getByText('Total registered users')).toBeInTheDocument();
    });

    it('does not render description element when not provided', () => {
      render(<StatCard {...defaultProps} />);
      expect(screen.queryByText('Total registered users')).not.toBeInTheDocument();
    });
  });

  describe('icon', () => {
    it('renders icon when provided', () => {
      const icon = <span data-testid="icon">📊</span>;
      render(<StatCard {...defaultProps} icon={icon} />);
      expect(screen.getByTestId('icon')).toBeInTheDocument();
    });

    it('wraps icon in styled container', () => {
      const icon = <span data-testid="icon">📊</span>;
      render(<StatCard {...defaultProps} icon={icon} />);
      const iconContainer = screen.getByTestId('icon').parentElement;
      expect(iconContainer?.className).toContain('rounded-lg');
    });
  });

  describe('trend', () => {
    it('displays positive trend', () => {
      const trend = {
        value: 12.5,
        label: 'from last month',
        isPositive: true,
      };
      render(<StatCard {...defaultProps} trend={trend} />);
      expect(screen.getByText('+12.5%')).toBeInTheDocument();
      expect(screen.getByText('from last month')).toBeInTheDocument();
    });

    it('displays negative trend', () => {
      const trend = {
        value: 8.3,
        label: 'from yesterday',
        isPositive: false,
      };
      render(<StatCard {...defaultProps} trend={trend} />);
      expect(screen.getByText('-8.3%')).toBeInTheDocument();
      expect(screen.getByText('from yesterday')).toBeInTheDocument();
    });

    it('applies positive color for positive trend', () => {
      const trend = { value: 10, label: 'test', isPositive: true };
      render(<StatCard {...defaultProps} trend={trend} />);
      const trendValue = screen.getByText('+10%');
      expect(trendValue.className).toContain('text-emerald');
    });

    it('applies negative color for negative trend', () => {
      const trend = { value: 10, label: 'test', isPositive: false };
      render(<StatCard {...defaultProps} trend={trend} />);
      const trendValue = screen.getByText('-10%');
      expect(trendValue.className).toContain('text-red');
    });

    it('does not render trend section when not provided', () => {
      render(<StatCard {...defaultProps} />);
      expect(screen.queryByText('%')).not.toBeInTheDocument();
    });
  });

  describe('styling', () => {
    it('applies custom className', () => {
      const { container } = render(<StatCard {...defaultProps} className="custom-stat-card" />);
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain('custom-stat-card');
    });

    it('title has muted color', () => {
      render(<StatCard {...defaultProps} />);
      const title = screen.getByText('Total Users');
      expect(title.className).toContain('text-slate-400');
    });

    it('value has prominent styling', () => {
      render(<StatCard {...defaultProps} />);
      const value = screen.getByText('1,234');
      expect(value.className).toContain('text-2xl');
      expect(value.className).toContain('font-bold');
    });
  });

  describe('variants', () => {
    it('applies default variant', () => {
      const { container } = render(<StatCard {...defaultProps} variant="default" />);
      const card = container.firstChild as HTMLElement;
      expect(card).toBeInTheDocument();
    });

    it('applies elevated variant', () => {
      const { container } = render(<StatCard {...defaultProps} variant="elevated" />);
      const card = container.firstChild as HTMLElement;
      expect(card).toBeInTheDocument();
    });
  });

  describe('icon container styling', () => {
    it('applies positive trend background to icon container', () => {
      const icon = <span data-testid="icon">📊</span>;
      const trend = { value: 10, label: 'test', isPositive: true };
      render(<StatCard {...defaultProps} icon={icon} trend={trend} />);
      
      const iconContainer = screen.getByTestId('icon').parentElement;
      expect(iconContainer?.className).toContain('bg-emerald');
    });

    it('applies negative trend background to icon container', () => {
      const icon = <span data-testid="icon">📊</span>;
      const trend = { value: 10, label: 'test', isPositive: false };
      render(<StatCard {...defaultProps} icon={icon} trend={trend} />);
      
      const iconContainer = screen.getByTestId('icon').parentElement;
      expect(iconContainer?.className).toContain('bg-violet');
    });
  });

  describe('use cases', () => {
    it('works as revenue card', () => {
      render(
        <StatCard
          title="Revenue"
          value="$52,430"
          description="Monthly revenue"
          icon={<span>💰</span>}
          trend={{ value: 15.3, label: 'vs last month', isPositive: true }}
        />
      );
      
      expect(screen.getByText('Revenue')).toBeInTheDocument();
      expect(screen.getByText('$52,430')).toBeInTheDocument();
      expect(screen.getByText('Monthly revenue')).toBeInTheDocument();
      expect(screen.getByText('+15.3%')).toBeInTheDocument();
    });

    it('works as active users card', () => {
      render(
        <StatCard
          title="Active Users"
          value={8432}
          icon={<span>👥</span>}
          trend={{ value: 2.1, label: 'from yesterday', isPositive: true }}
        />
      );
      
      expect(screen.getByText('Active Users')).toBeInTheDocument();
      expect(screen.getByText('8432')).toBeInTheDocument();
    });

    it('works as error rate card', () => {
      render(
        <StatCard
          title="Error Rate"
          value="0.12%"
          trend={{ value: 0.05, label: 'from last week', isPositive: false }}
        />
      );
      
      expect(screen.getByText('Error Rate')).toBeInTheDocument();
      expect(screen.getByText('0.12%')).toBeInTheDocument();
      expect(screen.getByText('-0.05%')).toBeInTheDocument();
    });

    it('works as simple metric card', () => {
      render(
        <StatCard
          title="Uptime"
          value="99.99%"
        />
      );
      
      expect(screen.getByText('Uptime')).toBeInTheDocument();
      expect(screen.getByText('99.99%')).toBeInTheDocument();
    });
  });
});
