'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  variant?: 'fullscreen' | 'component' | 'page';
  className?: string;
  children?: React.ReactNode;
}

const LoadingOverlay = ({
  isLoading,
  message,
  variant = 'component',
  className,
  children
}: LoadingOverlayProps) => {
  if (!isLoading) return children;

  const overlayVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  };

  const spinnerVariants = {
    animate: {
      rotate: 360,
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: "linear" as const
      }
    }
  };

  const contentVariants = {
    hidden: { scale: 0.95, opacity: 0 },
    visible: { scale: 1, opacity: 1 }
  };

  const getOverlayClasses = () => {
    switch (variant) {
      case 'fullscreen':
        return 'fixed inset-0 z-50 flex items-center justify-center bg-bg-base/80 backdrop-blur-sm';
      case 'page':
        return 'absolute inset-0 z-40 flex items-center justify-center bg-bg-base/60 backdrop-blur-xs min-h-[400px]';
      case 'component':
      default:
        return 'absolute inset-0 z-30 flex items-center justify-center bg-bg-base/50 rounded-lg';
    }
  };

  return (
    <>
      {children}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={overlayVariants}
        className={cn(getOverlayClasses(), className)}
      >
        <motion.div
          initial="hidden"
          animate="visible"
          variants={contentVariants}
          className="text-center p-6 rounded-xl bg-bg-surface border border-border-default shadow-lg"
        >
          <motion.div
            variants={spinnerVariants}
            animate="animate"
            className="mx-auto mb-4"
          >
            <Loader2 className="h-8 w-8 text-accent-primary" />
          </motion.div>
          
          {message && (
            <p className="text-text-secondary font-medium">{message}</p>
          )}
        </motion.div>
      </motion.div>
    </>
  );
};

interface ProgressBarProps {
  isLoading: boolean;
  progress?: number;
  className?: string;
}

const ProgressBar = ({ isLoading, progress = 0, className }: ProgressBarProps) => {
  if (!isLoading) return null;

  return (
    <div className={cn('w-full h-1.5 bg-bg-surface rounded-full overflow-hidden', className)}>
      <motion.div
        className="h-full bg-accent-primary rounded-full"
        initial={{ width: '0%' }}
        animate={{ 
          width: progress > 0 ? `${progress}%` : '100%' 
        }}
        transition={{ 
          duration: progress > 0 ? 0.3 : 2,
          repeat: progress <= 0 ? Infinity : 0,
          repeatType: "reverse"
        }}
      />
    </div>
  );
};

interface PulseLoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const PulseLoader = ({ size = 'md', className }: PulseLoaderProps) => {
  const sizeClasses = {
    sm: 'h-2 w-2',
    md: 'h-3 w-3',
    lg: 'h-4 w-4'
  };

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className={cn(
            sizeClasses[size],
            'rounded-full bg-accent-primary'
          )}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: index * 0.2
          }}
        />
      ))}
    </div>
  );
};

interface WaveLoaderProps {
  barCount?: number;
  className?: string;
}

const WaveLoader = ({ barCount = 5, className }: WaveLoaderProps) => {
  return (
    <div className={cn('flex items-end gap-1 h-8', className)}>
      {Array.from({ length: barCount }).map((_, index) => (
        <motion.div
          key={index}
          className="w-2 bg-accent-primary rounded-t"
          animate={{
            height: ['20%', '100%', '20%']
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: index * 0.1
          }}
        />
      ))}
    </div>
  );
};

export { LoadingOverlay, ProgressBar, PulseLoader, WaveLoader };