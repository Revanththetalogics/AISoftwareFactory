import { cva, type VariantProps } from 'class-variance-authority';

// Card variants for consistent styling across the app
export const cardVariants = cva(
  'border-slate-800 bg-slate-900/50 backdrop-blur-sm',
  {
    variants: {
      variant: {
        default: 'border-slate-800 bg-slate-900/50 backdrop-blur-sm',
        elevated: 'border-slate-700 bg-slate-800/50 backdrop-blur-md shadow-lg',
        interactive: 'border-slate-800 bg-slate-900/50 backdrop-blur-sm transition-all hover:border-slate-700 hover:bg-slate-800/50 cursor-pointer',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

// Button variants extending the existing UI component
export const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'underline-offset-4 hover:underline text-primary',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3 rounded-md',
        lg: 'h-11 px-8 rounded-md',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

// Badge variants
export const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
        secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
        outline: 'text-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

// Status badge variants for agent/project status
export const statusBadgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium',
  {
    variants: {
      status: {
        active: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400',
        idle: 'border-slate-500/20 bg-slate-500/10 text-slate-400',
        paused: 'border-amber-500/20 bg-amber-500/10 text-amber-400',
        error: 'border-red-500/20 bg-red-500/10 text-red-400',
        running: 'border-violet-500/20 bg-violet-500/10 text-violet-400',
        completed: 'border-blue-500/20 bg-blue-500/10 text-blue-400',
        pending: 'border-slate-500/20 bg-slate-500/10 text-slate-400',
      },
    },
    defaultVariants: {
      status: 'pending',
    },
  }
);

// Input variants
export const inputVariants = cva(
  'flex h-10 w-full rounded-md border bg-transparent px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'border-input bg-background',
        dark: 'border-slate-700 bg-slate-900/50 text-slate-200',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

// Animation variants (for framer-motion)
export const fadeInVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.25, 0, 1] as const,
    },
  },
};

export const slideUpVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.25, 0, 1] as const,
    },
  },
};

export const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export type CardVariants = VariantProps<typeof cardVariants>;
export type ButtonVariants = VariantProps<typeof buttonVariants>;
export type BadgeVariants = VariantProps<typeof badgeVariants>;
export type StatusBadgeVariants = VariantProps<typeof statusBadgeVariants>;
export type InputVariants = VariantProps<typeof inputVariants>;
