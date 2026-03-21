'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { Loader2, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';

/**
 * SkeletonBlock - Placeholder for loading content
 */
export interface SkeletonBlockProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'circular' | 'rounded' | 'square';
  animated?: boolean;
}

export function SkeletonBlock({
  className,
  width,
  height = '1rem',
  variant = 'rounded',
  animated = true,
}: SkeletonBlockProps) {
  return (
    <motion.div
      animate={animated ? {
        opacity: [0.5, 0.7, 0.5],
      } : {}}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      className={cn(
        'bg-bg-panel border border-border-subtle',
        variant === 'text' && 'h-4 rounded',
        variant === 'circular' && 'rounded-full',
        variant === 'rounded' && 'rounded-lg',
        variant === 'square' && 'rounded-none',
        className
      )}
      style={{ width, height }}
    />
  );
}

/**
 * StreamingText - Typewriter effect for AI output
 */
export interface StreamingTextProps {
  text: string;
  speed?: number;
  className?: string;
  cursor?: boolean;
  startOnMount?: boolean;
}

export function StreamingText({
  text,
  speed = 30,
  className,
  cursor = true,
  startOnMount = true,
}: StreamingTextProps) {
  return (
    <span className={cn('font-system text-text-code', className)}>
      {text.split('').map((char, index) => (
        <motion.span
          key={index}
          initial={{ opacity: 0 }}
          animate={startOnMount ? { opacity: 1 } : {}}
          transition={{ delay: index * speed / 1000 }}
        >
          {char}
        </motion.span>
      ))}
      {cursor && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="inline-block w-px h-4 bg-state-running ml-0.5"
        />
      )}
    </span>
  );
}

/**
 * ProgressDots - Sequential dot animation for loading
 */
export interface ProgressDotsProps {
  count?: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ProgressDots({
  count = 3,
  size = 'md',
  className,
}: ProgressDotsProps) {
  const sizeClasses = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
  };

  return (
    <div className={cn('flex items-center gap-1.5', className)} role="status" aria-label="Loading">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className={cn('rounded-full bg-state-running', sizeClasses[size])}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: i * 0.2,
          }}
          aria-hidden="true"
        />
      ))}
      <span className="sr-only">Loading...</span>
    </div>
  );
}

/**
 * ShimmerEffect - Gradient sweep overlay for loading states
 */
export interface ShimmerEffectProps {
  className?: string;
  direction?: 'horizontal' | 'vertical';
  speed?: 'slow' | 'normal' | 'fast';
}

export function ShimmerEffect({
  className,
  direction = 'horizontal',
  speed = 'normal',
}: ShimmerEffectProps) {
  const speeds = {
    slow: 3,
    normal: 1.5,
    fast: 0.8,
  };

  return (
    <motion.div
      className={cn(
        'absolute inset-0 overflow-hidden',
        className
      )}
      animate={{
        x: direction === 'horizontal' ? ['100%', '-100%'] : 0,
        y: direction === 'vertical' ? ['100%', '-100%'] : 0,
      }}
      transition={{
        duration: speeds[speed],
        repeat: Infinity,
        ease: 'linear',
      }}
    >
      <div className="w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </motion.div>
  );
}

/**
 * LoadingSpinner - Enhanced spinner with glow effect
 */
export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  text?: string;
  variant?: 'default' | 'ai';
}

export function LoadingSpinner({
  size = 'md',
  className,
  text,
  variant = 'default',
}: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)} role="status" aria-live="polite">
      <div className="relative">
        <Loader2 className={cn('animate-spin', sizes[size], 
          variant === 'ai' ? 'text-state-running' : 'text-text-secondary'
        )} aria-hidden="true" />
        {variant === 'ai' && (
          <div className="absolute inset-0 blur-md bg-state-running/20 rounded-full" aria-hidden="true" />
        )}
      </div>
      {text ? (
        <p className="text-sm text-text-secondary">{text}</p>
      ) : (
        <span className="sr-only">Loading...</span>
      )}
    </div>
  );
}

/**
 * ContentLoader - Composite loading state for cards/panels
 */
export interface ContentLoaderProps {
  lines?: number;
  showImage?: boolean;
  showAvatar?: boolean;
  className?: string;
}

export function ContentLoader({
  lines = 3,
  showImage = false,
  showAvatar = false,
  className,
}: ContentLoaderProps) {
  return (
    <div className={cn('space-y-3 p-4', className)}>
      {/* Header section */}
      {(showImage || showAvatar) && (
        <div className="flex items-center gap-3">
          {showAvatar && (
            <SkeletonBlock
              variant="circular"
              width="40px"
              height="40px"
            />
          )}
          {showImage && (
            <SkeletonBlock
              variant="rounded"
              width="100%"
              height="120px"
            />
          )}
        </div>
      )}

      {/* Text lines */}
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <SkeletonBlock
            key={i}
            variant="text"
            height="1rem"
            width={i === lines - 1 ? '60%' : '100%'}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * AILoading - Specialized loading state for AI operations
 */
export interface AILoadingProps {
  message?: string;
  tips?: string[];
  className?: string;
}

export function AILoading({
  message = 'AI is thinking...',
  tips = [],
  className,
}: AILoadingProps) {
  const [tipIndex, setTipIndex] = useState(0);

  useEffect(() => {
    if (tips.length === 0) return;
    
    const interval = setInterval(() => {
      setTipIndex(prev => (prev + 1) % tips.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [tips.length]);

  return (
    <div className={cn('flex flex-col items-center justify-center p-8 gap-6', className)} role="status" aria-live="polite" aria-busy="true">
      {/* Animated AI icon */}
      <motion.div
        className="relative"
        animate={{
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
        aria-hidden="true"
      >
        <div className="relative">
          <Sparkles className="w-12 h-12 text-state-running" />
          <motion.div
            className="absolute inset-0 blur-xl bg-state-running/30 rounded-full"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          />
        </div>
      </motion.div>

      {/* Message */}
      <div className="text-center space-y-2">
        <p className="text-text-primary font-medium">{message}</p>
        
        {/* Rotating tips */}
        {tips.length > 0 && (
          <motion.p
            className="text-sm text-text-tertiary max-w-xs"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            aria-live="off"
          >
            💡 Tip: {tips[tipIndex]}
          </motion.p>
        )}
      </div>

      {/* Progress dots */}
      <ProgressDots count={4} size="md" />
    </div>
  );
}
