'use client';

import { cn } from '@/lib/utils';
import { GripVertical, GripHorizontal } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState, useRef, useCallback, useEffect } from 'react';

export interface ResizablePanelProps {
  children: React.ReactNode;
  className?: string;
  initialSize?: number | string;
  minSize?: number | string;
  maxSize?: number | string;
  orientation?: 'horizontal' | 'vertical';
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  onResize?: (size: number) => void;
  onCollapse?: (collapsed: boolean) => void;
  resizeHandleClassName?: string;
}

/**
 * ResizablePanel - A flexible panel component with drag-to-resize functionality
 * Supports both horizontal and vertical resizing with smooth animations
 */
export function ResizablePanel({
  children,
  className,
  initialSize = 300,
  minSize = 200,
  maxSize = 800,
  orientation = 'horizontal',
  collapsible = true,
  defaultCollapsed = false,
  onResize,
  onCollapse,
  resizeHandleClassName,
}: ResizablePanelProps) {
  const [isResizing, setIsResizing] = useState(false);
  const [size, setSize] = useState<number | string>(initialSize);
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const containerRef = useRef<HTMLDivElement>(null);
  const startPos = useRef(0);
  const startSize = useRef(0);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (collapsed && orientation === 'horizontal') return;
    
    e.preventDefault();
    setIsResizing(true);
    startPos.current = orientation === 'horizontal' ? e.clientX : e.clientY;
    startSize.current = typeof size === 'number' ? size : parseInt(size as string, 10);
    
    document.body.style.cursor = orientation === 'horizontal' ? 'col-resize' : 'row-resize';
    document.body.style.userSelect = 'none';
  }, [collapsed, orientation, size]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing || !containerRef.current) return;

    const currentPos = orientation === 'horizontal' ? e.clientX : e.clientY;
    const delta = currentPos - startPos.current;
    const newSize = Math.max(
      typeof minSize === 'number' ? minSize : parseInt(minSize as string, 10),
      Math.min(
        typeof maxSize === 'number' ? maxSize : parseInt(maxSize as string, 10),
        startSize.current + (orientation === 'horizontal' ? delta : -delta)
      )
    );

    setSize(newSize);
    onResize?.(newSize);
  }, [isResizing, orientation, minSize, maxSize, onResize]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, []);

  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, handleMouseMove, handleMouseUp]);

  const toggleCollapse = useCallback(() => {
    const newCollapsed = !collapsed;
    setCollapsed(newCollapsed);
    onCollapse?.(newCollapsed);
  }, [collapsed, onCollapse]);

  const dimension = orientation === 'horizontal' ? 'width' : 'height';
  const value = collapsed ? 0 : size;

  return (
    <div 
      ref={containerRef}
      className={cn('relative flex shrink-0', className)}
      style={{
        [dimension]: typeof value === 'number' ? `${value}px` : value,
        overflow: 'hidden',
      }}
    >
      {children}
      
      {/* Resize Handle */}
      {!collapsed && (
        <div
          className={cn(
            'absolute z-10 flex items-center justify-center',
            'bg-transparent hover:bg-state-running-dim/50 transition-colors',
            'group/resize-handle',
            orientation === 'horizontal' 
              ? 'right-0 top-0 h-full w-1 cursor-col-resize' 
              : 'bottom-0 left-0 w-full h-1 cursor-row-resize',
            isResizing && 'bg-state-running-dim',
            resizeHandleClassName
          )}
          onMouseDown={handleMouseDown}
          onDoubleClick={toggleCollapse}
        >
          {/* Grip Indicator */}
          <motion.div
            className={cn(
              'opacity-0 group-hover/resize-handle:opacity-100 transition-opacity',
              'flex items-center justify-center p-1 rounded-md bg-bg-overlay border border-border-default',
              orientation === 'horizontal' ? 'h-8 w-4' : 'w-8 h-4'
            )}
            animate={isResizing ? { scale: 1.1 } : {}}
          >
            {orientation === 'horizontal' ? (
              <GripVertical className="h-3 w-3 text-text-secondary" />
            ) : (
              <GripHorizontal className="h-3 w-3 text-text-secondary" />
            )}
          </motion.div>
        </div>
      )}
      
      {/* Collapse Toggle (when collapsed) */}
      {collapsible && collapsed && (
        <button
          onClick={toggleCollapse}
          className={cn(
            'absolute inset-0 w-full h-full',
            'flex items-center justify-center',
            'bg-bg-panel border border-border-default',
            'hover:bg-state-running-dim/30 hover:border-state-running transition-colors',
            'group/collapse-toggle'
          )}
          title="Expand panel"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className={cn(
              'p-2 rounded-lg bg-bg-elevated border border-border-subtle',
              'group-hover/collapse-toggle:border-state-running'
            )}
          >
            {orientation === 'horizontal' ? (
              <GripHorizontal className="h-4 w-4 text-text-secondary" />
            ) : (
              <GripVertical className="h-4 w-4 text-text-secondary" />
            )}
          </motion.div>
        </button>
      )}
    </div>
  );
}

/**
 * ResizablePanelGroup - Container for multiple resizable panels
 */
export interface PanelGroupProps {
  children: React.ReactNode;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

export function ResizablePanelGroup({
  children,
  className,
  orientation = 'horizontal',
}: PanelGroupProps) {
  return (
    <div
      className={cn(
        'flex w-full h-full',
        orientation === 'horizontal' ? 'flex-row' : 'flex-col',
        className
      )}
    >
      {children}
    </div>
  );
}

/**
 * SplitPane - Two resizable panels side by side
 */
export interface SplitPaneProps {
  left: React.ReactNode;
  right: React.ReactNode;
  top?: React.ReactNode;
  bottom?: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
  initialSize?: number;
  minSize?: number;
  maxSize?: number;
  className?: string;
}

export function SplitPane({
  left,
  right,
  top,
  bottom,
  orientation = 'horizontal',
  initialSize = 50,
  minSize = 200,
  maxSize = 800,
  className,
}: SplitPaneProps) {
  const [leftSize, setLeftSize] = useState(initialSize);

  const handleResize = useCallback((newSize: number) => {
    setLeftSize(newSize);
  }, []);

  if (orientation === 'horizontal') {
    return (
      <ResizablePanelGroup className={className}>
        <ResizablePanel
          initialSize={leftSize}
          minSize={minSize}
          maxSize={maxSize}
          orientation="horizontal"
          onResize={handleResize}
        >
          <div className="w-full h-full overflow-auto">{left}</div>
        </ResizablePanel>
        <ResizablePanel
          initialSize="1fr"
          orientation="horizontal"
          resizeHandleClassName="resize-handle-vertical"
        >
          <div className="w-full h-full overflow-auto">{right}</div>
        </ResizablePanel>
      </ResizablePanelGroup>
    );
  }

  // Vertical split
  return (
    <ResizablePanelGroup orientation="vertical" className={className}>
      <ResizablePanel
        initialSize={leftSize}
        minSize={minSize}
        maxSize={maxSize}
        orientation="vertical"
        onResize={handleResize}
      >
        <div className="w-full h-full overflow-auto">{top}</div>
      </ResizablePanel>
      <ResizablePanel
        initialSize="1fr"
        orientation="vertical"
        resizeHandleClassName="resize-handle-horizontal"
      >
        <div className="w-full h-full overflow-auto">{bottom}</div>
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}
