'use client';

import React, { useState, useEffect } from 'react';
import { Loader2, Circle, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

// Loading state types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error' | 'partial';

// Loading configuration
interface LoadingConfig {
  delay?: number; // Delay before showing loading state (ms)
  minDuration?: number; // Minimum time to show loading state (ms)
  successDuration?: number; // Time to show success state (ms)
  errorDuration?: number; // Time to show error state (ms)
}

// Loading state hook
export function useLoadingState(config: LoadingConfig = {}) {
  const {
    delay = 300,
    minDuration = 500,
    successDuration = 2000,
    errorDuration = 3000
  } = config;

  const [state, setState] = useState<LoadingState>('idle');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState<string>('');
  
  // Timing refs
  const loadingStartTime = React.useRef<number>(0);
  const minDurationTimer = React.useRef<NodeJS.Timeout | null>(null);
  const stateTimer = React.useRef<NodeJS.Timeout | null>(null);

  // Start loading
  const startLoading = (msg?: string) => {
    setMessage(msg || 'Loading...');
    
    // Set delay timer
    if (delay > 0) {
      setTimeout(() => {
        setState('loading');
        loadingStartTime.current = Date.now();
        setProgress(0);
        
        // Start progress simulation
        const interval = setInterval(() => {
          setProgress(prev => {
            if (prev >= 90) {
              clearInterval(interval);
              return 90;
            }
            return prev + Math.random() * 15;
          });
        }, 200);
      }, delay);
    } else {
      setState('loading');
      loadingStartTime.current = Date.now();
      setProgress(0);
    }
  };

  // Complete with success
  const completeSuccess = (msg?: string) => {
    const elapsed = Date.now() - loadingStartTime.current;
    const remainingMinTime = Math.max(0, minDuration - elapsed);
    
    if (remainingMinTime > 0) {
      minDurationTimer.current = setTimeout(() => {
        setState('success');
        setMessage(msg || 'Completed successfully!');
        setProgress(100);
        
        stateTimer.current = setTimeout(() => {
          setState('idle');
          setProgress(0);
        }, successDuration);
      }, remainingMinTime);
    } else {
      setState('success');
      setMessage(msg || 'Completed successfully!');
      setProgress(100);
      
      stateTimer.current = setTimeout(() => {
        setState('idle');
        setProgress(0);
      }, successDuration);
    }
  };

  // Complete with error
  const completeError = (msg?: string) => {
    const elapsed = Date.now() - loadingStartTime.current;
    const remainingMinTime = Math.max(0, minDuration - elapsed);
    
    if (remainingMinTime > 0) {
      minDurationTimer.current = setTimeout(() => {
        setState('error');
        setMessage(msg || 'Operation failed');
        setProgress(0);
        
        stateTimer.current = setTimeout(() => {
          setState('idle');
          setProgress(0);
        }, errorDuration);
      }, remainingMinTime);
    } else {
      setState('error');
      setMessage(msg || 'Operation failed');
      setProgress(0);
      
      stateTimer.current = setTimeout(() => {
        setState('idle');
        setProgress(0);
      }, errorDuration);
    }
  };

  // Reset to idle
  const reset = () => {
    setState('idle');
    setProgress(0);
    setMessage('');
    
    if (minDurationTimer.current) {
      clearTimeout(minDurationTimer.current);
      minDurationTimer.current = null;
    }
    
    if (stateTimer.current) {
      clearTimeout(stateTimer.current);
      stateTimer.current = null;
    }
  };

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (minDurationTimer.current) {
        clearTimeout(minDurationTimer.current);
      }
      if (stateTimer.current) {
        clearTimeout(stateTimer.current);
      }
    };
  }, []);

  return {
    state,
    progress,
    message,
    startLoading,
    completeSuccess,
    completeError,
    reset,
    isLoading: state === 'loading',
    isSuccess: state === 'success',
    isError: state === 'error'
  };
}

// Loading spinner component
export const LoadingSpinner: React.FC<{
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ size = 'md', className }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <Loader2 
      className={cn(
        'animate-spin text-state-queued',
        sizeClasses[size],
        className
      )} 
    />
  );
};

// Progress bar component
export const ProgressBar: React.FC<{
  progress: number;
  className?: string;
  showPercentage?: boolean;
}> = ({ progress, className, showPercentage = false }) => {
  return (
    <div className={cn('w-full bg-bg-overlay rounded-full h-2', className)}>
      <motion.div
        className="bg-state-queued h-2 rounded-full"
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      />
      {showPercentage && (
        <span className="text-xs text-text-secondary mt-1 block text-center">
          {Math.round(progress)}%
        </span>
      )}
    </div>
  );
};

// Status indicator component
export const StatusIndicator: React.FC<{
  state: LoadingState;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ state, size = 'md', className }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const getStateIcon = () => {
    switch (state) {
      case 'loading':
        return <LoadingSpinner size={size} />;
      case 'success':
        return <CheckCircle2 className={cn('text-state-success', sizeClasses[size])} />;
      case 'error':
        return <XCircle className={cn('text-state-error', sizeClasses[size])} />;
      case 'partial':
        return <AlertCircle className={cn('text-state-warning', sizeClasses[size])} />;
      default:
        return <Circle className={cn('text-text-tertiary', sizeClasses[size])} />;
    }
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      {getStateIcon()}
    </div>
  );
};

// Loading overlay component
export const LoadingOverlay: React.FC<{
  isVisible: boolean;
  message?: string;
  progress?: number;
  variant?: 'fullscreen' | 'component' | 'card';
  className?: string;
  children?: React.ReactNode;
}> = ({ 
  isVisible, 
  message, 
  progress, 
  variant = 'component',
  className,
  children 
}) => {
  const variantClasses = {
    fullscreen: 'fixed inset-0 z-50 bg-bg-base/80 backdrop-blur-sm',
    component: 'absolute inset-0 z-10 bg-bg-base/60 backdrop-blur-xs',
    card: 'absolute inset-0 z-10 bg-bg-card/70 backdrop-blur-xs rounded-lg'
  };

  if (!isVisible) return children || null;

  return (
    <>
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className={cn(
              'flex items-center justify-center',
              variantClasses[variant],
              className
            )}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="flex flex-col items-center gap-4 p-6 bg-bg-card border border-border-default rounded-lg shadow-lg"
            >
              <LoadingSpinner size="lg" />
              {message && (
                <p className="text-text-primary font-medium text-center">
                  {message}
                </p>
              )}
              {progress !== undefined && (
                <ProgressBar progress={progress} className="w-48" showPercentage />
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

// Skeleton loader components
export const Skeleton: React.FC<{
  className?: string;
  height?: string;
  width?: string;
  rounded?: boolean;
}> = ({ className, height = 'h-4', width = 'w-full', rounded = true }) => {
  return (
    <div 
      className={cn(
        'animate-pulse bg-bg-overlay',
        height,
        width,
        rounded ? 'rounded' : '',
        className
      )}
    />
  );
};

export const CardSkeleton: React.FC<{
  className?: string;
}> = ({ className }) => {
  return (
    <div className={cn('space-y-3 p-4 border border-border-default rounded-lg bg-bg-card', className)}>
      <Skeleton className="h-6 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-8 w-20 rounded-full" />
        <Skeleton className="h-8 w-20 rounded-full" />
      </div>
    </div>
  );
};

export const ListSkeleton: React.FC<{
  count?: number;
  className?: string;
}> = ({ count = 3, className }) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
};

// Context for global loading state
interface LoadingContextType {
  isLoading: boolean;
  message: string;
  showGlobalLoading: (message?: string) => void;
  hideGlobalLoading: () => void;
}

const LoadingContext = React.createContext<LoadingContextType | undefined>(undefined);

export const LoadingProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const showGlobalLoading = (msg = 'Loading...') => {
    setIsLoading(true);
    setMessage(msg);
  };

  const hideGlobalLoading = () => {
    setIsLoading(false);
    setMessage('');
  };

  return (
    <LoadingContext.Provider value={{
      isLoading,
      message,
      showGlobalLoading,
      hideGlobalLoading
    }}>
      {children}
      <LoadingOverlay
        isVisible={isLoading}
        message={message}
        variant="fullscreen"
      />
    </LoadingContext.Provider>
  );
};

export const useGlobalLoading = () => {
  const context = React.useContext(LoadingContext);
  if (context === undefined) {
    throw new Error('useGlobalLoading must be used within a LoadingProvider');
  }
  return context;
};