import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/ui/badge';

describe('Badge', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<Badge>Badge Text</Badge>);
      expect(screen.getByText('Badge Text')).toBeInTheDocument();
    });

    it('renders as span by default', () => {
      render(<Badge data-testid="badge">Badge</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge.tagName).toBe('SPAN');
    });

    it('renders children correctly', () => {
      render(<Badge>Status: Active</Badge>);
      expect(screen.getByText('Status: Active')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<Badge className="custom-badge">Badge</Badge>);
      const badge = screen.getByText('Badge');
      expect(badge.className).toContain('custom-badge');
    });
  });

  describe('variants', () => {
    it('renders default variant', () => {
      render(<Badge variant="default">Default</Badge>);
      const badge = screen.getByText('Default');
      expect(badge.className).toContain('bg-primary');
    });

    it('renders secondary variant', () => {
      render(<Badge variant="secondary">Secondary</Badge>);
      const badge = screen.getByText('Secondary');
      expect(badge.className).toContain('bg-secondary');
    });

    it('renders destructive variant', () => {
      render(<Badge variant="destructive">Destructive</Badge>);
      const badge = screen.getByText('Destructive');
      expect(badge.className).toContain('destructive');
    });

    it('renders outline variant', () => {
      render(<Badge variant="outline">Outline</Badge>);
      const badge = screen.getByText('Outline');
      expect(badge.className).toContain('border-border');
    });

    it('renders ghost variant', () => {
      render(<Badge variant="ghost">Ghost</Badge>);
      const badge = screen.getByText('Ghost');
      expect(badge.className).toContain('hover:bg-muted');
    });

    it('renders link variant', () => {
      render(<Badge variant="link">Link</Badge>);
      const badge = screen.getByText('Link');
      expect(badge.className).toContain('underline-offset-4');
    });
  });

  describe('styling', () => {
    it('has rounded styling', () => {
      render(<Badge>Rounded</Badge>);
      const badge = screen.getByText('Rounded');
      expect(badge.className).toContain('rounded');
    });

    it('has inline-flex display', () => {
      render(<Badge>Flex</Badge>);
      const badge = screen.getByText('Flex');
      expect(badge.className).toContain('inline-flex');
    });

    it('has proper font size', () => {
      render(<Badge>Small Text</Badge>);
      const badge = screen.getByText('Small Text');
      expect(badge.className).toContain('text-xs');
    });

    it('has font-medium weight', () => {
      render(<Badge>Medium</Badge>);
      const badge = screen.getByText('Medium');
      expect(badge.className).toContain('font-medium');
    });
  });

  describe('integration with icons', () => {
    it('renders with icon element', () => {
      render(
        <Badge>
          <span data-testid="icon">✓</span> Success
        </Badge>
      );
      expect(screen.getByTestId('icon')).toBeInTheDocument();
      expect(screen.getByText('Success')).toBeInTheDocument();
    });
  });

  describe('use cases', () => {
    it('works as status indicator', () => {
      render(<Badge variant="default">Active</Badge>);
      expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('works as count indicator', () => {
      render(<Badge variant="destructive">3</Badge>);
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('works as label', () => {
      render(<Badge variant="secondary">Beta</Badge>);
      expect(screen.getByText('Beta')).toBeInTheDocument();
    });

    it('works as tag', () => {
      render(<Badge variant="outline">TypeScript</Badge>);
      expect(screen.getByText('TypeScript')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('renders semantic content', () => {
      render(<Badge>Notification</Badge>);
      const badge = screen.getByText('Notification');
      expect(badge).toBeInTheDocument();
    });

    it('can have aria-label', () => {
      render(<Badge aria-label="New notifications: 5">5</Badge>);
      const badge = screen.getByLabelText('New notifications: 5');
      expect(badge).toBeInTheDocument();
    });
  });
});
