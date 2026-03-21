import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  SkeletonBlock,
  StreamingText,
  ProgressDots,
  ShimmerEffect,
  LoadingSpinner,
  ContentLoader,
  AILoading,
} from '@/components/system/loading-states';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, className, ...props }: React.PropsWithChildren<{ className?: string }>) => (
      <div className={className} {...props}>{children}</div>
    ),
    span: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <span {...props}>{children}</span>
    ),
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}));

describe('SkeletonBlock', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      const { container } = render(<SkeletonBlock />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('applies custom width', () => {
      const { container } = render(<SkeletonBlock width="200px" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton).toHaveStyle({ width: '200px' });
    });

    it('applies custom height', () => {
      const { container } = render(<SkeletonBlock height="50px" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton).toHaveStyle({ height: '50px' });
    });

    it('applies custom className', () => {
      const { container } = render(<SkeletonBlock className="custom-skeleton" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('custom-skeleton');
    });
  });

  describe('variants', () => {
    it('applies text variant', () => {
      const { container } = render(<SkeletonBlock variant="text" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('h-4');
    });

    it('applies circular variant', () => {
      const { container } = render(<SkeletonBlock variant="circular" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('rounded-full');
    });

    it('applies rounded variant (default)', () => {
      const { container } = render(<SkeletonBlock variant="rounded" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('rounded-lg');
    });

    it('applies square variant', () => {
      const { container } = render(<SkeletonBlock variant="square" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('rounded-none');
    });
  });
});

describe('StreamingText', () => {
  describe('rendering', () => {
    it('renders text content', () => {
      render(<StreamingText text="Hello World" />);
      // Each character is rendered separately
      expect(screen.getByText('H')).toBeInTheDocument();
      expect(screen.getByText('W')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(<StreamingText text="Test" className="custom-text" />);
      const container = document.querySelector('.custom-text');
      expect(container).toBeInTheDocument();
    });
  });

  describe('cursor', () => {
    it('shows cursor by default', () => {
      render(<StreamingText text="Test" />);
      // Cursor is a motion.span element
      const spans = document.querySelectorAll('span');
      // Last span should be the cursor
      expect(spans.length).toBeGreaterThan(4); // 4 chars + cursor
    });

    it('hides cursor when cursor prop is false', () => {
      render(<StreamingText text="Test" cursor={false} />);
      const spans = document.querySelectorAll('span');
      expect(spans.length).toBe(5); // Just the 4 chars + wrapper
    });
  });
});

describe('ProgressDots', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<ProgressDots />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('has loading aria-label', () => {
      render(<ProgressDots />);
      expect(screen.getByLabelText('Loading')).toBeInTheDocument();
    });

    it('renders 3 dots by default', () => {
      const { container } = render(<ProgressDots />);
      const dots = container.querySelectorAll('[aria-hidden="true"]');
      expect(dots.length).toBe(3);
    });

    it('renders custom count of dots', () => {
      const { container } = render(<ProgressDots count={5} />);
      const dots = container.querySelectorAll('[aria-hidden="true"]');
      expect(dots.length).toBe(5);
    });

    it('has sr-only loading text', () => {
      render(<ProgressDots />);
      expect(screen.getByText('Loading...')).toHaveClass('sr-only');
    });
  });

  describe('sizes', () => {
    it('applies small size', () => {
      const { container } = render(<ProgressDots size="sm" />);
      const dot = container.querySelector('[aria-hidden="true"]');
      expect(dot?.className).toContain('w-1.5');
    });

    it('applies medium size (default)', () => {
      const { container } = render(<ProgressDots size="md" />);
      const dot = container.querySelector('[aria-hidden="true"]');
      expect(dot?.className).toContain('w-2');
    });

    it('applies large size', () => {
      const { container } = render(<ProgressDots size="lg" />);
      const dot = container.querySelector('[aria-hidden="true"]');
      expect(dot?.className).toContain('w-2.5');
    });
  });

  describe('accessibility', () => {
    it('has role=status', () => {
      render(<ProgressDots />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });
});

describe('ShimmerEffect', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      const { container } = render(<ShimmerEffect />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('applies custom className', () => {
      const { container } = render(<ShimmerEffect className="custom-shimmer" />);
      const shimmer = container.firstChild as HTMLElement;
      expect(shimmer.className).toContain('custom-shimmer');
    });
  });
});

describe('LoadingSpinner', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<LoadingSpinner />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('has aria-live polite', () => {
      const { container } = render(<LoadingSpinner />);
      const spinner = container.firstChild as HTMLElement;
      expect(spinner).toHaveAttribute('aria-live', 'polite');
    });

    it('shows text when provided', () => {
      render(<LoadingSpinner text="Loading data..." />);
      expect(screen.getByText('Loading data...')).toBeInTheDocument();
    });

    it('shows sr-only text when no text provided', () => {
      render(<LoadingSpinner />);
      expect(screen.getByText('Loading...')).toHaveClass('sr-only');
    });

    it('applies custom className', () => {
      const { container } = render(<LoadingSpinner className="custom-spinner" />);
      const spinner = container.firstChild as HTMLElement;
      expect(spinner.className).toContain('custom-spinner');
    });
  });

  describe('sizes', () => {
    it('renders with small size', () => {
      render(<LoadingSpinner size="sm" />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('renders with medium size (default)', () => {
      render(<LoadingSpinner size="md" />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('renders with large size', () => {
      render(<LoadingSpinner size="lg" />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  describe('variants', () => {
    it('applies default variant', () => {
      const { container } = render(<LoadingSpinner variant="default" />);
      // The icon is inside the relative div
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('applies AI variant', () => {
      const { container } = render(<LoadingSpinner variant="ai" />);
      // The AI variant includes a blur effect
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has role=status', () => {
      render(<LoadingSpinner />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });
});

describe('ContentLoader', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<ContentLoader />);
      // Should render skeleton lines
      const container = document.querySelector('.space-y-3');
      expect(container).toBeInTheDocument();
    });

    it('renders default 3 lines', () => {
      const { container } = render(<ContentLoader />);
      const skeletons = container.querySelectorAll('[class*="bg-bg-panel"]');
      expect(skeletons.length).toBe(3);
    });

    it('renders custom number of lines', () => {
      const { container } = render(<ContentLoader lines={5} />);
      const skeletons = container.querySelectorAll('[class*="bg-bg-panel"]');
      expect(skeletons.length).toBe(5);
    });

    it('applies custom className', () => {
      const { container } = render(<ContentLoader className="custom-loader" />);
      const loader = container.firstChild as HTMLElement;
      expect(loader.className).toContain('custom-loader');
    });
  });

  describe('avatar option', () => {
    it('shows avatar when showAvatar is true', () => {
      const { container } = render(<ContentLoader showAvatar />);
      const circular = container.querySelector('[class*="rounded-full"]');
      expect(circular).toBeInTheDocument();
    });

    it('does not show avatar by default', () => {
      const { container } = render(<ContentLoader />);
      const circular = container.querySelector('[class*="rounded-full"]');
      expect(circular).not.toBeInTheDocument();
    });
  });

  describe('image option', () => {
    it('shows image placeholder when showImage is true', () => {
      const { container } = render(<ContentLoader showImage />);
      // Image placeholder should have specific height
      const skeletons = container.querySelectorAll('[class*="rounded-lg"]');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });
});

describe('AILoading', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<AILoading />);
      // AILoading and ProgressDots both have role=status
      const statuses = screen.getAllByRole('status');
      expect(statuses.length).toBeGreaterThanOrEqual(1);
    });

    it('displays default message', () => {
      render(<AILoading />);
      expect(screen.getByText('AI is thinking...')).toBeInTheDocument();
    });

    it('displays custom message', () => {
      render(<AILoading message="Analyzing code..." />);
      expect(screen.getByText('Analyzing code...')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      const { container } = render(<AILoading className="custom-ai-loading" />);
      const loader = container.firstChild as HTMLElement;
      expect(loader.className).toContain('custom-ai-loading');
    });
  });

  describe('tips', () => {
    it('does not show tips section when no tips', () => {
      render(<AILoading tips={[]} />);
      expect(screen.queryByText(/Tip:/)).not.toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has role=status', () => {
      render(<AILoading />);
      // AILoading and ProgressDots both have role=status
      const statuses = screen.getAllByRole('status');
      expect(statuses.length).toBeGreaterThanOrEqual(1);
    });

    it('has aria-live polite', () => {
      const { container } = render(<AILoading />);
      const loader = container.firstChild as HTMLElement;
      expect(loader).toHaveAttribute('aria-live', 'polite');
    });

    it('has aria-busy true', () => {
      const { container } = render(<AILoading />);
      const loader = container.firstChild as HTMLElement;
      expect(loader).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('progress dots', () => {
    it('includes progress dots', () => {
      render(<AILoading />);
      // ProgressDots also has role=status, so there should be 2
      const statuses = screen.getAllByRole('status');
      expect(statuses.length).toBe(2);
    });
  });
});
