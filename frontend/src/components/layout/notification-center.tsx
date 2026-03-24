'use client';

import { Bell } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
}

const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'success',
    title: 'Deployment Complete',
    message: 'Project "SaaS App" deployed to staging',
    timestamp: '2 min ago',
  },
  {
    id: '2',
    type: 'info',
    title: 'Agent Activity',
    message: 'Backend Engineer completed API design',
    timestamp: '15 min ago',
  },
  {
    id: '3',
    type: 'warning',
    title: 'Simulation Alert',
    message: 'Architecture simulation needs review',
    timestamp: '1 hour ago',
  },
];

export function NotificationCenter() {
  const [unreadCount] = useState(3);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <Button
          variant="ghost"
          size="icon"
          className="relative text-text-secondary hover:bg-bg-hover hover:text-text-primary"
          aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ''}`}
          aria-haspopup="menu"
        >
          <Bell className="h-5 w-5" aria-hidden="true" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -right-1 -top-1 h-5 w-5 items-center justify-center rounded-full p-0 text-xs"
              aria-hidden="true"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[380px] border-border-default bg-bg-elevated" role="menu" aria-label="Notifications">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span className="text-text-primary">Notifications</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-auto text-xs text-state-running hover:text-state-running"
            aria-label="Mark all notifications as read"
          >
            Mark all read
          </Button>
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-border-default" />
        <ScrollArea className="h-[300px]" role="list" aria-label="Notification list">
          {mockNotifications.map((notification) => (
            <DropdownMenuItem
              key={notification.id}
              className="flex cursor-pointer items-start gap-3 p-3 focus:bg-bg-hover"
              role="listitem"
            >
              <div
                className={`mt-0.5 h-2 w-2 rounded-full ${
                  notification.type === 'success'
                    ? 'bg-state-success'
                    : notification.type === 'warning'
                      ? 'bg-state-warning'
                      : notification.type === 'error'
                        ? 'bg-state-error'
                        : 'bg-state-running'
                }`}
                aria-hidden="true"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-text-primary">{notification.title}</p>
                <p className="text-xs text-text-secondary">{notification.message}</p>
                <p className="mt-1 text-xs text-text-tertiary">{notification.timestamp}</p>
              </div>
            </DropdownMenuItem>
          ))}
        </ScrollArea>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
