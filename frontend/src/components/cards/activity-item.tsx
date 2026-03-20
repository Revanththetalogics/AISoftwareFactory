'use client';

import { memo, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface ActivityItemProps {
  icon: ReactNode;
  title: string;
  description: string;
  timestamp?: string;
  status?: 'running' | 'completed' | 'paused' | 'error';
  progress?: number;
}

export const ActivityItem = memo(function ActivityItem({
  icon,
  title,
  description,
  timestamp,
  status = 'completed',
  progress,
}: ActivityItemProps) {
  const statusColors = {
    running: 'text-violet-400 bg-violet-500/10',
    completed: 'text-emerald-400 bg-emerald-500/10',
    paused: 'text-amber-400 bg-amber-500/10',
    error: 'text-red-400 bg-red-500/10',
  };

  return (
    <div className={cn(
      'flex items-start gap-3 rounded-lg border border-slate-800/50 p-3 transition-colors hover:bg-slate-800/50',
      statusColors[status]
    )}>
      <div className={cn(
        'rounded-lg p-2',
        status === 'running' ? 'bg-violet-500/10' : 'bg-emerald-500/10'
      )}>
        {icon}
      </div>
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <p className="font-medium text-slate-200">{title}</p>
          {timestamp && (
            <span className="text-xs text-slate-500">{timestamp}</span>
          )}
        </div>
        <p className="text-sm text-slate-400">{description}</p>
        {progress !== undefined && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Progress</span>
              <span className="text-slate-300">{Math.round(progress)}%</span>
            </div>
            <div className="mt-1 h-1.5 w-full rounded-full bg-slate-800">
              <div
                className="h-1.5 rounded-full bg-violet-400 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
      {status === 'running' && (
        <div className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400"></span>
          <span className="text-xs text-violet-400">Working</span>
        </div>
      )}
    </div>
  );
});
