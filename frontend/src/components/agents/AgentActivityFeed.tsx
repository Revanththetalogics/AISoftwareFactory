'use client';

import { useEffect, useRef, useState } from 'react';
import { 
  Bot, 
  Code2, 
  FileText, 
  TestTube, 
  Rocket, 
  Brain,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Clock
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useEventStream } from '@/lib/hooks';
import { ScrollArea } from '@/components/ui/scroll-area';

interface AgentActivity {
  id: string;
  agent_id: string;
  agent_name: string;
  agent_role: string;
  action: string;
  target: string | null;
  status: 'idle' | 'working' | 'completed' | 'error';
  timestamp: string;
  progress?: number;
}

const roleIcons: Record<string, React.ElementType> = {
  ceo: Brain,
  'product-manager': FileText,
  architect: Brain,
  'backend-developer': Code2,
  'frontend-developer': Code2,
  'devops-engineer': Rocket,
  'qa-engineer': TestTube,
  default: Bot,
};

const statusConfig = {
  idle: {
    icon: Clock,
    color: 'text-text-tertiary',
    bgColor: 'bg-bg-base',
    label: 'Idle',
  },
  working: {
    icon: Loader2,
    color: 'text-state-running',
    bgColor: 'bg-state-running-dim',
    label: 'Working',
  },
  completed: {
    icon: CheckCircle2,
    color: 'text-state-success',
    bgColor: 'bg-state-success-dim',
    label: 'Completed',
  },
  error: {
    icon: AlertCircle,
    color: 'text-state-error',
    bgColor: 'bg-state-error-dim',
    label: 'Error',
  },
};

interface ActivityItemProps {
  activity: AgentActivity;
  isLatest?: boolean;
}

function ActivityItem({ activity, isLatest }: ActivityItemProps) {
  const Icon = roleIcons[activity.agent_role] || roleIcons.default;
  const status = statusConfig[activity.status];
  const StatusIcon = status.icon;

  const timeAgo = (timestamp: string) => {
    const now = typeof window !== 'undefined' ? Date.now() : 0;
    const seconds = Math.floor((now - new Date(timestamp).getTime()) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-3 rounded-lg transition-all',
        isLatest ? 'bg-state-queued-dim border border-state-queued/20' : 'hover:bg-bg-hover'
      )}
    >
      {/* Agent Avatar */}
      <div className={cn(
        'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg',
        status.bgColor
      )}>
        <Icon className={cn('h-5 w-5', status.color)} />
      </div>
      
      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-text-primary">
            {activity.agent_name}
          </span>
          <span className="text-xs text-text-tertiary">
            {activity.agent_role}
          </span>
          {isLatest && (
            <span className="px-1.5 py-0.5 text-xs rounded-full bg-state-queued text-white">
              Latest
            </span>
          )}
        </div>
        
        <p className="text-sm text-text-secondary mt-0.5">
          {activity.action}
          {activity.target && (
            <span className="text-text-tertiary"> → {activity.target}</span>
          )}
        </p>
        
        {/* Progress bar for working status */}
        {activity.status === 'working' && activity.progress !== undefined && (
          <div className="mt-2">
            <div className="h-1.5 w-full rounded-full bg-bg-base overflow-hidden">
              <div 
                className="h-full rounded-full bg-state-running transition-all duration-500"
                style={{ width: `${activity.progress}%` }}
              />
            </div>
            <span className="text-xs text-text-tertiary mt-1">
              {activity.progress}%
            </span>
          </div>
        )}
        
        <div className="flex items-center gap-2 mt-1.5">
          <StatusIcon className={cn('h-3 w-3', status.color)} />
          <span className={cn('text-xs', status.color)}>
            {status.label}
          </span>
          <span className="text-xs text-text-tertiary">
            {timeAgo(activity.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
}

interface AgentActivityFeedProps {
// Remove unused _projectId parameter
  maxItems?: number;
  className?: string;
}

export function AgentActivityFeed({
  maxItems = 50,
  className
}: AgentActivityFeedProps) {
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const { lastMessage, isConnected } = useEventStream();

  // Load initial activities - use ref to avoid effect re-running
  const initialLoadRef = useRef(false);
  useEffect(() => {
    if (initialLoadRef.current) return;
    initialLoadRef.current = true;

    // TODO: Fetch initial activities from API
    const mockActivities: AgentActivity[] = [
      {
        id: '1',
        agent_id: 'agent-1',
        agent_name: 'Product Manager',
        agent_role: 'product-manager',
        action: 'Analyzing requirements',
        target: 'User authentication system',
        status: 'completed',
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      },
      {
        id: '2',
        agent_id: 'agent-2',
        agent_name: 'System Architect',
        agent_role: 'architect',
        action: 'Designing database schema',
        target: 'PostgreSQL schema',
        status: 'working',
        timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
        progress: 65,
      },
      {
        id: '3',
        agent_id: 'agent-3',
        agent_name: 'Backend Developer',
        agent_role: 'backend-developer',
        action: 'Waiting for architecture',
        target: null,
        status: 'idle',
        timestamp: new Date(Date.now() - 1000 * 30).toISOString(),
      },
    ];
    setActivities(mockActivities);
  }, []);

  // Handle real-time updates
  useEffect(() => {
    if (lastMessage?.type === 'agent_status') {
      const activity = lastMessage.data as AgentActivity;
      setActivities(prev => {
        // Update existing or add new
        const exists = prev.find(a => a.id === activity.id);
        if (exists) {
          return prev.map(a => a.id === activity.id ? activity : a);
        }
        return [activity, ...prev].slice(0, maxItems);
      });
    }
  }, [lastMessage, maxItems]);

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-default">
        <h3 className="font-semibold text-text-primary">Agent Activity</h3>
        <div className="flex items-center gap-2">
          <span className={cn(
            'h-2 w-2 rounded-full',
            isConnected ? 'bg-state-success animate-pulse' : 'bg-state-error'
          )} />
          <span className="text-xs text-text-secondary">
            {isConnected ? 'Live' : 'Disconnected'}
          </span>
        </div>
      </div>
      
      {/* Activity List */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {activities.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-text-tertiary">
              <Bot className="h-8 w-8 mb-2 opacity-50" />
              <p className="text-sm">No activity yet</p>
              <p className="text-xs">Agents will appear here when they start working</p>
            </div>
          ) : (
            activities.map((activity, index) => (
              <ActivityItem 
                key={activity.id} 
                activity={activity}
                isLatest={index === 0}
              />
            ))
          )}
        </div>
      </ScrollArea>
      
      {/* Footer Stats */}
      <div className="px-4 py-2 border-t border-border-default bg-bg-panel/50">
        <div className="flex items-center justify-between text-xs text-text-secondary">
          <span>{activities.filter(a => a.status === 'working').length} active</span>
          <span>{activities.filter(a => a.status === 'completed').length} completed</span>
        </div>
      </div>
    </div>
  );
}

// Compact version for dashboard
export function AgentActivityFeedCompact({ className }: { className?: string }) {
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const { lastMessage } = useEventStream();

  useEffect(() => {
    if (lastMessage?.type === 'agent_status') {
      const activity = lastMessage.data as AgentActivity;
      setActivities(prev => [activity, ...prev].slice(0, 5));
    }
  }, [lastMessage]);

  return (
    <div className={cn('space-y-2', className)}>
      {activities.slice(0, 3).map((activity) => {
        const Icon = roleIcons[activity.agent_role] || roleIcons.default;
        const status = statusConfig[activity.status];
        
        return (
          <div 
            key={activity.id}
            className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-hover"
          >
            <div className={cn('h-8 w-8 rounded-lg flex items-center justify-center', status.bgColor)}>
              <Icon className={cn('h-4 w-4', status.color)} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary truncate">
                {activity.agent_name}
              </p>
              <p className="text-xs text-text-secondary truncate">
                {activity.action}
              </p>
            </div>
            <status.icon className={cn('h-4 w-4', status.color)} />
          </div>
        );
      })}
      
      {activities.length === 0 && (
        <p className="text-sm text-text-tertiary text-center py-4">
          No recent activity
        </p>
      )}
    </div>
  );
}
