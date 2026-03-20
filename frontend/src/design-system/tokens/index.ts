/**
 * ThetaAI Design System - Design Tokens
 * Centralized token definitions for consistent theming
 * 
 * These tokens are defined in globals.css and exported here
 * for programmatic access in JavaScript/TypeScript
 */

/**
 * Color tokens organized by category
 */
export const colors = {
  // System state colors
  state: {
    idle: 'oklch(0.6 0.05 260)',
    running: 'oklch(0.7 0.15 250)',
    success: 'oklch(0.7 0.18 145)',
    warning: 'oklch(0.75 0.18 65)',
    error: 'oklch(0.65 0.2 35)',
    queued: 'oklch(0.65 0.2 290)',
  },
  
  // Background layers
  bg: {
    base: 'oklch(0.12 0.02 260)',
    panel: 'oklch(0.15 0.02 260)',
    elevated: 'oklch(0.18 0.02 260)',
    overlay: 'oklch(0.2 0.02 260)',
    code: 'oklch(0.1 0.02 260)',
    input: 'oklch(0.16 0.02 260)',
    selected: 'oklch(0.22 0.02 260)',
  },
  
  // Text hierarchy
  text: {
    primary: 'oklch(0.98 0 0)',
    secondary: 'oklch(0.7 0 0)',
    tertiary: 'oklch(0.5 0 0)',
    code: 'oklch(0.85 0 0)',
    link: 'oklch(0.7 0.15 250)',
  },
  
  // Border hierarchy
  border: {
    subtle: 'oklch(1 0 0 / 0.08)',
    default: 'oklch(1 0 0 / 0.12)',
    emphasis: 'oklch(1 0 0 / 0.2)',
    state: 'oklch(1 0 0 / 0.3)',
  },
};

/**
 * Typography tokens
 */
export const typography = {
  fonts: {
    system: "'JetBrains Mono', 'Fira Code', monospace",
    ui: "'Inter', system-ui, sans-serif",
  },
  
  sizes: {
    xsCode: '0.7rem',
    smCode: '0.8125rem',
    mdCode: '0.9375rem',
    lgCode: '1.0625rem',
  },
  
  lineHeights: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};

/**
 * Layout tokens
 */
export const layout = {
  dimensions: {
    sidebarWidth: '280px',
    sidebarCollapsedWidth: '64px',
    topbarHeight: '56px',
  },
  
  spacing: {
    grid: '4px',
    compact: '8px',
    standard: '12px',
    relaxed: '16px',
    comfortable: '20px',
  },
  
  constraints: {
    panelMinWidth: '200px',
    panelMaxWidth: '800px',
  },
};

/**
 * Animation timing tokens
 */
export const animation = {
  duration: {
    instant: '100ms',
    fast: '200ms',
    normal: '300ms',
    slow: '500ms',
    slower: '800ms',
  },
  
  easing: {
    outExpo: 'cubic-bezier(0.16, 1, 0.3, 1)',
    inOutQuad: 'cubic-bezier(0.45, 0, 0.55, 1)',
    spring: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    smooth: 'cubic-bezier(0.25, 0.25, 0, 1)',
  },
};

/**
 * Gradient definitions
 */
export const gradients = {
  aiPrimary: 'linear-gradient(135deg, oklch(0.7 0.15 280), oklch(0.65 0.2 250))',
  aiSecondary: 'linear-gradient(135deg, oklch(0.6 0.15 180), oklch(0.7 0.15 280))',
  aiSuccess: 'linear-gradient(135deg, oklch(0.7 0.18 145), oklch(0.65 0.15 160))',
  aiWarning: 'linear-gradient(135deg, oklch(0.75 0.18 65), oklch(0.7 0.18 55))',
  aiError: 'linear-gradient(135deg, oklch(0.65 0.2 35), oklch(0.6 0.2 25))',
};

/**
 * Shadow definitions
 */
export const shadows = {
  glowRunning: '0 0 20px oklch(0.7 0.15 250 / 0.3)',
  glowSuccess: '0 0 20px oklch(0.7 0.18 145 / 0.3)',
  glowError: '0 0 20px oklch(0.65 0.2 35 / 0.3)',
};

/**
 * Border radius scale
 */
export const radius = {
  sm: 'calc(var(--radius) * 0.6)',
  md: 'calc(var(--radius) * 0.8)',
  lg: 'var(--radius)',
  xl: 'calc(var(--radius) * 1.4)',
  '2xl': 'calc(var(--radius) * 1.8)',
  '3xl': 'calc(var(--radius) * 2.2)',
  '4xl': 'calc(var(--radius) * 2.6)',
};

/**
 * Z-index scale
 */
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  fixed: 1200,
  modalBackdrop: 1300,
  modal: 1400,
  popover: 1500,
  tooltip: 1600,
  toast: 1700,
};

/**
 * Breakpoints (Tailwind v4 compatible)
 */
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

/**
 * Helper function to get CSS variable name
 */
export function cssVar(name: string): string {
  return `var(--${name})`;
}

/**
 * Get state color as CSS variable
 */
export function getStateColor(state: keyof typeof colors.state, variant: 'solid' | 'dim' = 'solid'): string {
  if (variant === 'dim') {
    return cssVar(`state-${state}-dim`);
  }
  return cssVar(`state-${state}`);
}

/**
 * Get background color as CSS variable
 */
export function getBackground(name: keyof typeof colors.bg): string {
  return cssVar(`bg-${name}`);
}

/**
 * Get text color as CSS variable
 */
export function getTextColor(name: keyof typeof colors.text): string {
  return cssVar(`text-${name}`);
}

/**
 * Export all tokens as a single object
 */
export const tokens = {
  colors,
  typography,
  layout,
  animation,
  gradients,
  shadows,
  radius,
  zIndex,
  breakpoints,
};

export default tokens;
