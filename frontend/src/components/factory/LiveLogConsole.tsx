'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Terminal, 
  Copy, 
  Trash2,
  Play,
  Pause,
  Activity,
  AlertTriangle,
  CheckCircle,
  Info,
  X
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'success';

export interface LiveLogEntry {
  id: string;
  timestamp: Date;
  level: LogLevel;
  source: string;
  message: string;
  details?: Record<string, unknown>;
}

interface LiveLogConsoleProps {
  logs: LiveLogEntry[];
  className?: string;
  maxHeight?: string;
  autoScroll?: boolean;
  showLevelFilters?: boolean;
  onClear?: () => void;
  onPause?: () => void;
  onResume?: () => void;
  isPaused?: boolean;
}

const getLogLevelConfig = (level: LogLevel) => {
  switch (level) {
    case 'error':
      return {
        icon: X,
        color: 'text-error',
        bgColor: 'bg-error/10',
        borderColor: 'border-error/20',
      };
    case 'warn':
      return {
        icon: AlertTriangle,
        color: 'text-warning',
        bgColor: 'bg-warning/10',
        borderColor: 'border-warning/20',
      };
    case 'success':
      return {
        icon: CheckCircle,
        color: 'text-success',
        bgColor: 'bg-success/10',
        borderColor: 'border-success/20',
      };
    case 'info':
      return {
        icon: Info,
        color: 'text-primary',
        bgColor: 'bg-primary/10',
        borderColor: 'border-primary/20',
      };
    case 'debug':
      return {
        icon: Terminal,
        color: 'text-text-secondary',
        bgColor: 'bg-bg-surface',
        borderColor: 'border-border',
      };
  }
};

const formatTimestamp = (date: Date) => {
  return date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    fractionalSecondDigits: 3
  });
};

export function LiveLogConsole({ 
  logs, 
  className,
  maxHeight = 'h-80',
  autoScroll = true,
  showLevelFilters = true,
  onClear,
  onPause,
  onResume,
  isPaused = false
}: LiveLogConsoleProps) {
  const [enabledLevels, setEnabledLevels] = useState<Record<LogLevel, boolean>>({
    debug: true,
    info: true,
    warn: true,
    error: true,
    success: true
  });
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const wasManuallyScrolled = useRef(false);

  // Filter logs based on enabled levels using useMemo
  const filteredLogs = useMemo(() => {
    return logs.filter(log => enabledLevels[log.level]);
  }, [logs, enabledLevels]);

  // Auto-scroll to bottom when new logs arrive (if not manually scrolled)
  useEffect(() => {
    if (autoScroll && !wasManuallyScrolled.current && scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [filteredLogs, autoScroll]);

  // Track manual scroll state
  const [showResumeHint, setShowResumeHint] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setShowResumeHint(wasManuallyScrolled.current);
    }, 100); // Check every 100ms
    
    return () => clearInterval(interval);
  }, []);

  const handleLevelToggle = (level: LogLevel) => {
    setEnabledLevels(prev => ({
      ...prev,
      [level]: !prev[level]
    }));
  };

  const handleCopyLogs = () => {
    const logText = filteredLogs.map(log => 
      `[${formatTimestamp(log.timestamp)}] ${log.level.toUpperCase()}: [${log.source}] ${log.message}`
    ).join('\n');
    
    navigator.clipboard.writeText(logText).catch(console.error);
  };

  const handleClearLogs = () => {
    onClear?.();
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    // If user scrolls up significantly, pause auto-scroll
    if (scrollTop < scrollHeight - clientHeight - 100) {
      wasManuallyScrolled.current = true;
    } else {
      wasManuallyScrolled.current = false;
    }
  };

  const handleResumeAutoScroll = () => {
    wasManuallyScrolled.current = false;
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  };

  return (
    <div className={cn('flex flex-col', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-text-primary">Live Logs</h3>
          <Badge variant="secondary" className="text-xs">
            {filteredLogs.length} entries
          </Badge>
        </div>
        
        <div className="flex items-center gap-2">
          {showLevelFilters && (
            <div className="flex gap-1">
              {(Object.keys(enabledLevels) as LogLevel[]).map(level => {
                const config = getLogLevelConfig(level);
                return (
                  <Button
                    key={level}
                    variant={enabledLevels[level] ? 'default' : 'outline'}
                    size="sm"
                    className="h-6 px-2 text-xs"
                    onClick={() => handleLevelToggle(level)}
                  >
                    <config.icon className="w-3 h-3 mr-1" />
                    {level}
                  </Button>
                );
              })}
            </div>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={isPaused ? onResume : onPause}
            title={isPaused ? 'Resume auto-scroll' : 'Pause auto-scroll'}
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={handleCopyLogs}
            title="Copy logs"
          >
            <Copy className="w-4 h-4" />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={handleClearLogs}
            title="Clear logs"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Logs Container */}
      <div className={cn(maxHeight, 'flex-1')}>
        <ScrollArea 
          ref={scrollAreaRef}
          className="h-full rounded-lg border border-border bg-bg-code p-3 font-mono-system text-xs"
          onScroll={handleScroll}
        >
          <AnimatePresence>
            {filteredLogs.length === 0 ? (
              <div className="flex items-center justify-center h-full text-text-secondary">
                <Activity className="w-8 h-8 mr-2 animate-pulse" />
                <span>No logs to display</span>
              </div>
            ) : (
              <div className="space-y-1">
                {filteredLogs.map((log) => {
                  const config = getLogLevelConfig(log.level);
                  const Icon = config.icon;
                  
                  return (
                    <motion.div
                      key={log.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className={cn(
                        'flex items-start gap-2 p-2 rounded border',
                        config.bgColor,
                        config.borderColor
                      )}
                    >
                      <Icon className={cn('w-4 h-4 mt-0.5 flex-shrink-0', config.color)} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-text-tertiary text-[10px] font-mono">
                            {formatTimestamp(log.timestamp)}
                          </span>
                          <Badge 
                            variant="outline" 
                            className={cn('text-[10px] font-mono', config.color)}
                          >
                            {log.level.toUpperCase()}
                          </Badge>
                          <span className="text-text-secondary text-[10px] truncate">
                            [{log.source}]
                          </span>
                        </div>
                        <div className={cn('whitespace-pre-wrap', config.color)}>
                          {log.message}
                        </div>
                        {log.details && (
                          <pre className="text-[10px] text-text-secondary mt-1 overflow-x-auto">
                            {JSON.stringify(log.details, null, 2)}
                          </pre>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </AnimatePresence>
        </ScrollArea>
      </div>

      {/* Auto-scroll resume hint */}
      {showResumeHint && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-center"
        >
          <Button
            variant="ghost"
            size="sm"
            className="text-xs text-text-secondary hover:text-primary"
            onClick={handleResumeAutoScroll}
          >
            <Activity className="w-3 h-3 mr-1" />
            Resume auto-scroll
          </Button>
        </motion.div>
      )}
    </div>
  );
}