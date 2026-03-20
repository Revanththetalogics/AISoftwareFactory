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
          className="relative text-slate-400 hover:bg-slate-800 hover:text-slate-200"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -right-1 -top-1 h-5 w-5 items-center justify-center rounded-full p-0 text-xs"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[380px] border-slate-700 bg-slate-900">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span className="text-slate-200">Notifications</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-auto text-xs text-violet-400 hover:text-violet-300"
          >
            Mark all read
          </Button>
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-slate-700" />
        <ScrollArea className="h-[300px]">
          {mockNotifications.map((notification) => (
            <DropdownMenuItem
              key={notification.id}
              className="flex cursor-pointer items-start gap-3 p-3 focus:bg-slate-800"
            >
              <div
                className={`mt-0.5 h-2 w-2 rounded-full ${
                  notification.type === 'success'
                    ? 'bg-emerald-400'
                    : notification.type === 'warning'
                      ? 'bg-amber-400'
                      : notification.type === 'error'
                        ? 'bg-red-400'
                        : 'bg-blue-400'
                }`}
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-200">{notification.title}</p>
                <p className="text-xs text-slate-400">{notification.message}</p>
                <p className="mt-1 text-xs text-slate-500">{notification.timestamp}</p>
              </div>
            </DropdownMenuItem>
          ))}
        </ScrollArea>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
