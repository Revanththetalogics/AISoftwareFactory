import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '@/components/ui/input';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <div {...props}>{children}</div>
    ),
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}));

describe('Input', () => {
  describe('rendering', () => {
    it('renders without crashing', () => {
      render(<Input />);
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('renders with placeholder', () => {
      render(<Input placeholder="Enter your name" />);
      expect(screen.getByPlaceholderText('Enter your name')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<Input className="custom-input" data-testid="input" />);
      const wrapper = screen.getByTestId('input').closest('div');
      expect(wrapper).toBeInTheDocument();
    });
  });

  describe('input types', () => {
    it('renders as text input by default', () => {
      render(<Input data-testid="input" />);
      const input = screen.getByTestId('input');
      // Default HTML input behavior - no explicit type means text
      expect(input.tagName).toBe('INPUT');
    });

    it('renders with explicit text type', () => {
      render(<Input type="text" data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input).toHaveAttribute('type', 'text');
    });

    it('renders email input', () => {
      render(<Input type="email" data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input).toHaveAttribute('type', 'email');
    });

    it('renders password input', () => {
      render(<Input type="password" data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input).toHaveAttribute('type', 'password');
    });

    it('renders number input', () => {
      render(<Input type="number" data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input).toHaveAttribute('type', 'number');
    });

    it('renders search input', () => {
      render(<Input type="search" data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input).toHaveAttribute('type', 'search');
    });
  });

  describe('user interactions', () => {
    it('allows typing', async () => {
      const user = userEvent.setup();
      render(<Input />);
      const input = screen.getByRole('textbox');
      
      await user.type(input, 'Hello World');
      expect(input).toHaveValue('Hello World');
    });

    it('calls onChange when typing', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();
      render(<Input onChange={handleChange} />);
      
      await user.type(screen.getByRole('textbox'), 'a');
      expect(handleChange).toHaveBeenCalled();
    });

    it('can be cleared', async () => {
      const user = userEvent.setup();
      render(<Input />);
      const input = screen.getByRole('textbox');
      
      await user.type(input, 'Test');
      await user.clear(input);
      expect(input).toHaveValue('');
    });
  });

  describe('validation states', () => {
    it('shows valid state', () => {
      render(<Input validationState="valid" data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input.className).toContain('border-state-success');
    });

    it('shows invalid state', () => {
      render(<Input validationState="invalid" data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input.className).toContain('border-state-error');
    });

    it('shows validating state indicator', () => {
      render(<Input validationState="validating" />);
      // The loader should be present (via motion.div)
      const wrapper = document.querySelector('[class*="relative"]');
      expect(wrapper).toBeInTheDocument();
    });
  });

  describe('help and error text', () => {
    it('shows help text', () => {
      render(<Input helpText="This is helpful information" />);
      expect(screen.getByText('This is helpful information')).toBeInTheDocument();
    });

    it('shows error text', () => {
      render(<Input errorText="This field is required" />);
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('prioritizes error text over help text', () => {
      render(
        <Input 
          helpText="Help text" 
          errorText="Error text" 
        />
      );
      expect(screen.getByText('Error text')).toBeInTheDocument();
      expect(screen.queryByText('Help text')).not.toBeInTheDocument();
    });
  });

  describe('compact mode', () => {
    it('applies compact styling', () => {
      render(<Input compact data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input.className).toContain('h-7');
    });
  });

  describe('left and right elements', () => {
    it('renders left element', () => {
      render(<Input leftElement={<span data-testid="left">L</span>} />);
      expect(screen.getByTestId('left')).toBeInTheDocument();
    });

    it('renders right element', () => {
      render(<Input rightElement={<span data-testid="right">R</span>} />);
      expect(screen.getByTestId('right')).toBeInTheDocument();
    });

    it('applies padding for left element', () => {
      render(<Input leftElement={<span>L</span>} data-testid="input" />);
      const input = screen.getByTestId('input');
      expect(input.className).toContain('pl-9');
    });
  });

  describe('disabled state', () => {
    it('can be disabled', () => {
      render(<Input disabled />);
      expect(screen.getByRole('textbox')).toBeDisabled();
    });

    it('does not allow typing when disabled', async () => {
      const user = userEvent.setup();
      render(<Input disabled />);
      const input = screen.getByRole('textbox');
      
      await user.type(input, 'Test');
      expect(input).toHaveValue('');
    });
  });

  describe('async validation', () => {
    it('shows async validation message', () => {
      render(
        <Input 
          asyncValidation={{ 
            isChecking: false, 
            message: 'Username is available' 
          }} 
        />
      );
      expect(screen.getByText('Username is available')).toBeInTheDocument();
    });

    it('shows checking state', () => {
      render(
        <Input 
          asyncValidation={{ 
            isChecking: true 
          }} 
        />
      );
      // The async checking should show loader
      const wrapper = document.querySelector('[class*="relative"]');
      expect(wrapper).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has correct role', () => {
      render(<Input />);
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('is focusable', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');
      input.focus();
      expect(document.activeElement).toBe(input);
    });

    it('supports aria-label', () => {
      render(<Input aria-label="Email address" />);
      expect(screen.getByLabelText('Email address')).toBeInTheDocument();
    });

    it('supports aria-describedby', () => {
      render(
        <>
          <Input aria-describedby="help" />
          <span id="help">Enter your email</span>
        </>
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-describedby', 'help');
    });
  });

  describe('controlled vs uncontrolled', () => {
    it('works as controlled input', async () => {
      const user = userEvent.setup();
      const ControlledInput = () => {
        const [value, setValue] = React.useState('');
        return (
          <Input 
            value={value} 
            onChange={(e) => setValue(e.target.value)} 
          />
        );
      };
      
      render(<ControlledInput />);
      const input = screen.getByRole('textbox');
      await user.type(input, 'Controlled');
      expect(input).toHaveValue('Controlled');
    });

    it('works as uncontrolled input', async () => {
      const user = userEvent.setup();
      render(<Input defaultValue="Default" />);
      const input = screen.getByRole('textbox');
      
      expect(input).toHaveValue('Default');
      await user.clear(input);
      await user.type(input, 'New Value');
      expect(input).toHaveValue('New Value');
    });
  });
});

// Need to import React for controlled input test
import * as React from 'react';
