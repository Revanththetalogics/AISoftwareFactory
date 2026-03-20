/**
 * ThetaAI Design System - Motion Variants
 * Framer Motion animation presets for consistent UI animations
 */

import type { Variants } from 'framer-motion';

/**
 * Container animations for staggered children
 */
export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

/**
 * Item animations for staggered lists
 */
export const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.16, 1, 0.3, 1], // ease-out-expo
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * Status indicator animations
 */
export const statusVariants: Variants = {
  idle: { 
    scale: 1, 
    opacity: 0.5,
    transition: { duration: 0.2 }
  },
  running: { 
    scale: [1, 1.1, 1],
    opacity: 1,
    transition: { 
      repeat: Infinity, 
      duration: 2,
      ease: "easeInOut"
    }
  },
  success: { 
    scale: [1, 1.2, 1], 
    opacity: 1,
    transition: { duration: 0.3 }
  },
  error: {
    x: [-5, 5, -5, 5, 0],
    opacity: 1,
    transition: { 
      duration: 0.4,
      repeat: Infinity,
      repeatDelay: 2
    }
  },
};

/**
 * Page transition animations
 */
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.16, 1, 0.3, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
      ease: [0.16, 1, 0.3, 1],
    },
  },
};

/**
 * Modal/Dialog animations
 */
export const modalVariants: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.2,
      ease: [0.175, 0.885, 0.32, 1.275], // spring
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.15,
    },
  },
};

/**
 * Tooltip animations
 */
export const tooltipVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 5,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.15,
      ease: "easeOut",
    },
  },
  exit: {
    opacity: 0,
    y: 5,
    transition: {
      duration: 0.1,
    },
  },
};

/**
 * Progress bar animations
 */
export const progressVariants: Variants = {
  initial: {
    width: 0,
  },
  animate: (width: number) => ({
    width: `${width}%`,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  }),
};

/**
 * Fade in/out simple animations
 */
export const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.2 }
  },
  exit: { 
    opacity: 0,
    transition: { duration: 0.15 }
  },
};

/**
 * Slide up/down animations
 */
export const slideVariants: Variants = {
  hidden: (direction: 'up' | 'down') => ({
    opacity: 0,
    y: direction === 'up' ? 20 : -20,
  }),
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.16, 1, 0.3, 1],
    },
  },
  exit: {
    opacity: 0,
    y: 0,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * Scale animations for cards and panels
 */
export const scaleVariants: Variants = {
  hidden: {
    scale: 0.9,
    opacity: 0,
  },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: 0.2,
      ease: [0.175, 0.885, 0.32, 1.275],
    },
  },
  exit: {
    scale: 0.9,
    opacity: 0,
    transition: {
      duration: 0.15,
    },
  },
};

/**
 * Workflow node state transitions
 */
export const workflowNodeVariants: Variants = {
  pending: {
    opacity: 0.5,
    scale: 1,
  },
  active: {
    opacity: 1,
    scale: [1, 1.05, 1],
    boxShadow: [
      '0 0 0 0 rgba(99, 102, 241, 0)',
      '0 0 0 10px rgba(99, 102, 241, 0.2)',
      '0 0 0 0 rgba(99, 102, 241, 0)',
    ],
    transition: {
      duration: 1.5,
      repeat: Infinity,
    },
  },
  completed: {
    opacity: 1,
    scale: 1,
  },
  failed: {
    opacity: 1,
    x: [-5, 5, -5, 5, 0],
    transition: {
      duration: 0.5,
    },
  },
};

/**
 * Log entry animations
 */
export const logEntryVariants: Variants = {
  hidden: {
    opacity: 0,
    x: -10,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.15,
    },
  },
  exit: {
    opacity: 0,
    x: 10,
    transition: {
      duration: 0.1,
    },
  },
};

/**
 * Loading spinner rotation
 */
export const spinVariants: Variants = {
  spin: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: "linear",
    },
  },
};

/**
 * Pulse animation for status indicators
 */
export const pulseVariants: Variants = {
  pulse: {
    scale: [1, 1.1, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

/**
 * Shimmer effect for loading states
 */
export const shimmerVariants: Variants = {
  shimmer: {
    x: ['-100%', '100%'],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: "linear",
    },
  },
};

/**
 * Export all variants as a single object for easy access
 */
export const variants = {
  container: containerVariants,
  item: itemVariants,
  status: statusVariants,
  page: pageVariants,
  modal: modalVariants,
  tooltip: tooltipVariants,
  progress: progressVariants,
  fade: fadeVariants,
  slide: slideVariants,
  scale: scaleVariants,
  workflowNode: workflowNodeVariants,
  logEntry: logEntryVariants,
  spin: spinVariants,
  pulse: pulseVariants,
  shimmer: shimmerVariants,
};
