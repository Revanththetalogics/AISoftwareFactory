'use client';

import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Filter, 
  Download, 
  Trash2, 
  ChevronDown,
  X,
  Terminal,
  Info,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { useState, useRef, useEffect, useMemo } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LogLine } from '@/components/typography/code-block';

export type LogLevel = 'info' | 'warn' | 'error' | 'debug' | 'success';

export interface LogEntry {
  id: string;
  level: LogLevel;
  source: string;
  message: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export interface LogFilter {
  levels?: LogLevel[];
  sources?: string[];
  search?: string;
}

export interface LogStreamProps {
  logs: LogEntry[];
  filter?: LogFilter;
  autoScroll?: boolean;
  maxLines?: number;
  showFilter?: boolean;
  compact?: boolean;
  className?: string;
  onLineClick?: (log: LogEntry) => void;
  onClear?: () => void;
}

const levelIcons: Record<LogLevel, React.ElementType> = {
  info: Info,
  warn: AlertTriangle,
  error: AlertCircle,
  debug: Terminal,
  success: CheckCircle2,
};

const levelColors: Record<LogLevel, string> = {
  info: 'text-state-running',
  warn: 'text-state-warning',
  error: 'text-state-error',
  debug: 'text-text-tertiary',
  success: 'text-state-success',
};

const levelBg: Record<LogLevel, string> = {
  info: 'bg-state-running-dim',
  warn: 'bg-state-warning-dim',
  error: 'bg-state-error-dim',
  debug: 'bg-bg-panel',
  success: 'bg-state-success-dim',
};

/**
 * LogStream - Real-time log viewer with filtering and virtualization
 * Terminal-style appearance optimized for high information density
 */
export function LogStream({
  logs,
  filter,
  autoScroll = true,
  maxLines = 1000,
  showFilter = true,
  compact = false,
  className,
  onLineClick,
  onClear,
}: LogStreamProps) {
  const [localFilter, setLocalFilter] = useState<LogFilter>(filter || {});
  const [showFilters, setShowFilters] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [logs, autoScroll]);

  // Filter logs
  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      // Level filter
      if (localFilter.levels && localFilter.levels.length > 0) {
        if (!localFilter.levels.includes(log.level)) return false;
      }
      
      // Source filter
      if (localFilter.sources && localFilter.sources.length > 0) {
        if (!localFilter.sources.includes(log.source)) return false;
      }
      
      // Search filter
      if (localFilter.search) {
        const searchLower = localFilter.search.toLowerCase();
        return (
          log.message.toLowerCase().includes(searchLower) ||
          log.source.toLowerCase().includes(searchLower)
        );
      }
      
      return true;
    }).slice(-maxLines); // Keep only last N lines
  }, [logs, localFilter, maxLines]);

  // Extract unique sources
  const sources = useMemo(() => {
    return Array.from(new Set(logs.map(log => log.source)));
  }, [logs]);

  const handleLevelToggle = (level: LogLevel) => {
    setLocalFilter(prev => {
      const currentLevels = prev.levels || ['info', 'warn', 'error', 'debug', 'success'];
      const newLevels = currentLevels.includes(level)
        ? currentLevels.filter(l => l !== level)
        : [...currentLevels, level];
      return { ...prev, levels: newLevels };
    });
  };

  const handleExport = () => {
    const logText = filteredLogs.map(log => 
      `[${log.timestamp.toISOString()}] [${log.level.toUpperCase()}] [${log.source}] ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={cn(
      'flex flex-col h-full border border-border-default rounded-lg overflow-hidden',
      'bg-bg-code',
      className
    )}>
      {/* Toolbar */}
      {showFilter && (
        <div className="flex items-center justify-between gap-2 p-3 border-b border-border-subtle bg-bg-panel">
          <div className="flex items-center gap-2 flex-1">
            <Terminal className="w-4 h-4 text-text-tertiary" />
            
            {/* Search input */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary" />
              <Input
                placeholder="Search logs..."
                value={localFilter.search || ''}
                onChange={(e) => setLocalFilter(prev => ({ ...prev, search: e.target.value }))}
                className="pl-8 h-8 text-sm"
                compact
              />
              {localFilter.search && (
                <button
                  onClick={() => setLocalFilter(prev => ({ ...prev, search: undefined }))}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Filter toggle */}
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={() => setShowFilters(!showFilters)}
              className={showFilters ? 'bg-state-running-dim text-state-running' : ''}
            >
              <Filter className="w-4 h-4" />
            </Button>

            {/* Export */}
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={handleExport}
              title="Export logs"
            >
              <Download className="w-4 h-4" />
            </Button>

            {/* Clear */}
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={onClear}
              title="Clear logs"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Filter panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-b border-border-subtle bg-bg-panel"
          >
            <div className="p-3 space-y-3">
              {/* Level filters */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-text-secondary">Log Levels</label>
                <div className="flex flex-wrap gap-1.5">
                  {(['info', 'warn', 'error', 'debug', 'success'] as LogLevel[]).map(level => (
                    <button
                      key={level}
                      onClick={() => handleLevelToggle(level)}
                      className={cn(
                        'inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors',
                        !localFilter.levels?.includes(level)
                          ? 'opacity-50 bg-bg-base text-text-tertiary'
                          : levelBg[level],
                        levelColors[level]
                      )}
                    >
                      {level.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              {/* Source filters */}
              {sources.length > 0 && (
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-text-secondary">Sources</label>
                  <div className="flex flex-wrap gap-1.5">
                    {sources.map(source => (
                      <button
                        key={source}
                        onClick={() => setLocalFilter(prev => ({
                          ...prev,
                          sources: prev.sources?.includes(source)
                            ? prev.sources?.filter(s => s !== source)
                            : [...(prev.sources || []), source]
                        }))}
                        className={cn(
                          'inline-flex items-center px-2 py-1 rounded text-xs font-medium transition-colors',
                          !localFilter.sources?.includes(source)
                            ? 'bg-bg-base text-text-tertiary'
                            : 'bg-state-running-dim text-state-running'
                        )}
                      >
                        {source}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Log entries */}
      <ScrollArea ref={scrollRef} className="flex-1">
        <div className="p-2 font-system text-sm">
          {filteredLogs.length === 0 ? (
            <div className="flex items-center justify-center py-12 text-text-tertiary">
              <Terminal className="w-8 h-8 mr-2 opacity-50" />
              <span>No logs to display</span>
            </div>
          ) : (
            filteredLogs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
                className={cn(
                  'cursor-pointer rounded-sm px-2 -mx-2 transition-colors',
                  'hover:bg-bg-hover',
                  compact && 'py-0.5',
                  !compact && 'py-1'
                )}
                onClick={() => onLineClick?.(log)}
              >
                <LogLine
                  level={log.level}
                  source={log.source}
                  timestamp={log.timestamp.toLocaleTimeString()}
                  className={compact ? 'text-xs' : ''}
                >
                  <span className="break-words">{log.message}</span>
                </LogLine>
                
                {/* Metadata expandable section */}
                {log.metadata && Object.keys(log.metadata).length > 0 && (
                  <div className="mt-1 ml-8 text-xs font-mono text-text-tertiary">
                    {Object.entries(log.metadata).map(([key, value]) => (
                      <div key={key} className="flex gap-2">
                        <span className="text-text-secondary">{key}:</span>
                        <span className="text-text-code">{JSON.stringify(value)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            ))
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Status bar */}
      <div className="border-t border-border-subtle bg-bg-panel px-3 py-1.5 flex items-center justify-between text-xs text-text-tertiary">
        <div className="flex items-center gap-3">
          <span>Total: <span className="font-mono text-text-code">{filteredLogs.length}</span></span>
          {logs.length !== filteredLogs.length && (
            <span>Filtered: <span className="font-mono text-text-code">{logs.length}</span></span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {autoScroll && (
            <span className="flex items-center gap-1 text-state-running">
              <span className="w-1.5 h-1.5 rounded-full bg-state-running animate-pulse" />
              Live
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * MiniLogViewer - Compact log viewer for dashboards
 */
export function MiniLogViewer({
  logs,
  limit = 10,
  className,
}: {
  logs: LogEntry[];
  limit?: number;
  className?: string;
}) {
  const recentLogs = logs.slice(-limit);

  return (
    <div className={cn('space-y-1 font-system text-xs', className)}>
      {recentLogs.map((log, index) => (
        <div key={log.id} className="flex items-start gap-2 opacity-75 hover:opacity-100 transition-opacity">
          <span className="text-text-tertiary shrink-0">
            {log.timestamp.toLocaleTimeString()}
          </span>
          <span className={cn('shrink-0', levelColors[log.level])}>
            [{log.level.toUpperCase()}]
          </span>
          <span className="text-text-code truncate">{log.message}</span>
        </div>
      ))}
    </div>
  );
}
