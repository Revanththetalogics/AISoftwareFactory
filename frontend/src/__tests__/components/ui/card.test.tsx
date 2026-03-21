import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  CardAction,
} from '@/components/ui/card';

describe('Card', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<Card>Card content</Card>);
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('renders as a div', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card.tagName).toBe('DIV');
    });

    it('renders children correctly', () => {
      render(
        <Card>
          <div data-testid="child">Child content</div>
        </Card>
      );
      expect(screen.getByTestId('child')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<Card className="custom-card" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card.className).toContain('custom-card');
    });
  });

  describe('sizes', () => {
    it('renders default size', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveAttribute('data-size', 'default');
    });

    it('renders small size', () => {
      render(<Card size="sm" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveAttribute('data-size', 'sm');
    });
  });

  describe('styling', () => {
    it('has rounded corners', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card.className).toContain('rounded-xl');
    });

    it('has proper background', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card.className).toContain('bg-card');
    });

    it('has proper text color', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card.className).toContain('text-card-foreground');
    });
  });
});

describe('CardHeader', () => {
  it('renders without crashing', () => {
    render(<CardHeader>Header content</CardHeader>);
    expect(screen.getByText('Header content')).toBeInTheDocument();
  });

  it('renders as a div', () => {
    render(<CardHeader data-testid="header">Header</CardHeader>);
    const header = screen.getByTestId('header');
    expect(header.tagName).toBe('DIV');
  });

  it('renders with custom className', () => {
    render(<CardHeader className="custom-header" data-testid="header">Header</CardHeader>);
    const header = screen.getByTestId('header');
    expect(header.className).toContain('custom-header');
  });

  it('has grid layout', () => {
    render(<CardHeader data-testid="header">Header</CardHeader>);
    const header = screen.getByTestId('header');
    expect(header.className).toContain('grid');
  });
});

describe('CardTitle', () => {
  it('renders without crashing', () => {
    render(<CardTitle>Title</CardTitle>);
    expect(screen.getByText('Title')).toBeInTheDocument();
  });

  it('renders as a div', () => {
    render(<CardTitle data-testid="title">Title</CardTitle>);
    const title = screen.getByTestId('title');
    expect(title.tagName).toBe('DIV');
  });

  it('renders with custom className', () => {
    render(<CardTitle className="custom-title" data-testid="title">Title</CardTitle>);
    const title = screen.getByTestId('title');
    expect(title.className).toContain('custom-title');
  });

  it('has proper font styling', () => {
    render(<CardTitle data-testid="title">Title</CardTitle>);
    const title = screen.getByTestId('title');
    expect(title.className).toContain('font-medium');
  });
});

describe('CardDescription', () => {
  it('renders without crashing', () => {
    render(<CardDescription>Description</CardDescription>);
    expect(screen.getByText('Description')).toBeInTheDocument();
  });

  it('renders as a div', () => {
    render(<CardDescription data-testid="desc">Description</CardDescription>);
    const desc = screen.getByTestId('desc');
    expect(desc.tagName).toBe('DIV');
  });

  it('has muted text color', () => {
    render(<CardDescription data-testid="desc">Description</CardDescription>);
    const desc = screen.getByTestId('desc');
    expect(desc.className).toContain('text-muted-foreground');
  });
});

describe('CardContent', () => {
  it('renders without crashing', () => {
    render(<CardContent>Content</CardContent>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders as a div', () => {
    render(<CardContent data-testid="content">Content</CardContent>);
    const content = screen.getByTestId('content');
    expect(content.tagName).toBe('DIV');
  });

  it('has proper padding', () => {
    render(<CardContent data-testid="content">Content</CardContent>);
    const content = screen.getByTestId('content');
    expect(content.className).toContain('px-4');
  });
});

describe('CardFooter', () => {
  it('renders without crashing', () => {
    render(<CardFooter>Footer</CardFooter>);
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('renders as a div', () => {
    render(<CardFooter data-testid="footer">Footer</CardFooter>);
    const footer = screen.getByTestId('footer');
    expect(footer.tagName).toBe('DIV');
  });

  it('has flex layout', () => {
    render(<CardFooter data-testid="footer">Footer</CardFooter>);
    const footer = screen.getByTestId('footer');
    expect(footer.className).toContain('flex');
  });

  it('has border-top styling', () => {
    render(<CardFooter data-testid="footer">Footer</CardFooter>);
    const footer = screen.getByTestId('footer');
    expect(footer.className).toContain('border-t');
  });
});

describe('CardAction', () => {
  it('renders without crashing', () => {
    render(<CardAction>Action</CardAction>);
    expect(screen.getByText('Action')).toBeInTheDocument();
  });

  it('renders as a div', () => {
    render(<CardAction data-testid="action">Action</CardAction>);
    const action = screen.getByTestId('action');
    expect(action.tagName).toBe('DIV');
  });

  it('positions correctly in grid', () => {
    render(<CardAction data-testid="action">Action</CardAction>);
    const action = screen.getByTestId('action');
    expect(action.className).toContain('col-start-2');
  });
});

describe('Card composition', () => {
  it('renders complete card structure', () => {
    render(
      <Card data-testid="card">
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card description text</CardDescription>
          <CardAction>
            <button>Action</button>
          </CardAction>
        </CardHeader>
        <CardContent>
          <p>Main content goes here</p>
        </CardContent>
        <CardFooter>
          <button>Footer button</button>
        </CardFooter>
      </Card>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card description text')).toBeInTheDocument();
    expect(screen.getByText('Main content goes here')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Footer button' })).toBeInTheDocument();
  });

  it('renders minimal card', () => {
    render(
      <Card>
        <CardContent>Simple content</CardContent>
      </Card>
    );
    expect(screen.getByText('Simple content')).toBeInTheDocument();
  });

  it('renders card with only header and content', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Title Only</CardTitle>
        </CardHeader>
        <CardContent>Content only</CardContent>
      </Card>
    );
    expect(screen.getByText('Title Only')).toBeInTheDocument();
    expect(screen.getByText('Content only')).toBeInTheDocument();
  });
});

describe('Card accessibility', () => {
  it('supports aria attributes', () => {
    render(<Card aria-label="Information card" data-testid="card">Content</Card>);
    const card = screen.getByTestId('card');
    expect(card).toHaveAttribute('aria-label', 'Information card');
  });

  it('can have role', () => {
    render(<Card role="article" data-testid="card">Content</Card>);
    const card = screen.getByRole('article');
    expect(card).toBeInTheDocument();
  });
});
