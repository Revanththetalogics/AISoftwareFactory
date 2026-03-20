'use client';

import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Copy, CheckCheck } from 'lucide-react';
import { useState } from 'react';

export interface CodeBlockProps {
  children?: React.ReactNode;
  className?: string;
  language?: 'typescript' | 'javascript' | 'python' | 'bash' | 'json' | 'yaml' | 'plaintext';
  filename?: string;
  compact?: boolean;
  showLineNumbers?: boolean;
  highlightLines?: number[];
  maxLines?: number;
  onCopy?: () => void;
}

export function CodeBlock({
  children,
  className,
  language = 'plaintext',
  filename,
  compact = false,
  showLineNumbers = true,
  highlightLines = [],
  maxLines,
  onCopy,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (children && typeof children === 'string') {
      navigator.clipboard.writeText(children);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onCopy?.();
    }
  };

  const content = typeof children === 'string' ? children : String(children);
  const lines = content.split('\n');
  const displayLines = maxLines ? lines.slice(0, maxLines) : lines;
  const hasMore = maxLines && lines.length > maxLines;

  return (
    <div 
      className={cn(
        'group relative overflow-hidden rounded-lg border bg-bg-code font-system text-sm',
        'border-border-default',
        className
      )}
    >
      {/* Header with filename and copy button */}
      {(filename || !compact) && (
        <div className="flex items-center justify-between border-b border-border-subtle bg-bg-panel px-3 py-2">
          <div className="flex items-center gap-2">
            {language && (
              <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
                {language}
              </span>
            )}
            {filename && (
              <>
                <span className="text-text-tertiary">/</span>
                <span className="text-xs text-text-secondary">{filename}</span>
              </>
            )}
          </div>
          {!compact && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            >
              {copied ? (
                <CheckCheck className="h-3 w-3 text-state-success" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          )}
        </div>
      )}

      {/* Code content */}
      <ScrollArea 
        className={cn('max-h-[600px]', compact ? 'max-h-[200px]' : '')}
        orientation={maxLines ? 'both' : 'vertical'}
      >
        <pre 
          className={cn(
            'p-4 overflow-x-auto',
            compact && 'p-2 text-xs'
          )}
        >
          <code className={cn('text-text-code whitespace-pre')}>
            {displayLines.map((line, index) => (
              <div 
                key={index}
                className={cn(
                  'relative',
                  highlightLines.includes(index + 1) && 
                    'bg-state-running-dim -mx-4 px-4 border-l-2 border-state-running'
                )}
              >
                {showLineNumbers && (
                  <span className="inline-block w-8 pr-3 text-right select-none text-text-tertiary opacity-50">
                    {index + 1}
                  </span>
                )}
                <span>{line}</span>
              </div>
            ))}
          </code>
        </pre>
        
        {hasMore && (
          <div className="border-t border-border-subtle bg-bg-panel px-4 py-2 text-xs text-text-tertiary text-center">
            ... {lines.length - maxLines} more lines
          </div>
        )}
      </ScrollArea>
    </div>
  );
}

/**
 * InlineCode component for system text within paragraphs
 */
export function InlineCode({ 
  children, 
  className 
}: { 
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <code
      className={cn(
        'inline-flex items-center rounded-md border border-border-subtle',
        'bg-bg-input px-1.5 py-0.5',
        'font-system text-xs text-text-code',
        className
      )}
    >
      {children}
    </code>
  );
}

/**
 * LogLine component for terminal-style log output
 */
export function LogLine({
  level = 'info',
  children,
  timestamp,
  source,
  className,
}: {
  level?: 'info' | 'warn' | 'error' | 'debug' | 'success';
  children: React.ReactNode;
  timestamp?: string;
  source?: string;
  className?: string;
}) {
  const levelColors = {
    info: 'text-state-running',
    warn: 'text-state-warning',
    error: 'text-state-error',
    debug: 'text-text-tertiary',
    success: 'text-state-success',
  };

  const levelBg = {
    info: 'bg-state-running-dim',
    warn: 'bg-state-warning-dim',
    error: 'bg-state-error-dim',
    debug: 'bg-bg-panel',
    success: 'bg-state-success-dim',
  };

  return (
    <div 
      className={cn(
        'flex items-start gap-2 font-system text-sm py-0.5',
        'hover:bg-bg-hover transition-colors',
        className
      )}
    >
      {timestamp && (
        <span className="text-text-tertiary text-xs shrink-0 tabular-nums">
          [{timestamp}]
        </span>
      )}
      
      {source && (
        <span className={cn(
          'px-1.5 py-0.5 rounded text-xs font-medium shrink-0',
          levelBg[level]
        )}>
          {source}
        </span>
      )}
      
      <span className={cn(levelColors[level])}>
        {children}
      </span>
    </div>
  );
}
