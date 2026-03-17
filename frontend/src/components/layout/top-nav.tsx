'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Bell,
  User,
  Moon,
  Sun,
  Settings,
} from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
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

export function TopNav() {
  const { theme, setTheme } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [unreadCount] = useState(3);

  return (
    <motion.header
      initial={{ y: -64 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="fixed left-[280px] right-0 top-0 z-30 h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl"
    >
      <div className="flex h-full items-center justify-between px-6">
        {/* Search */}
        <div className="flex max-w-md flex-1 items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              type="search"
              placeholder="Search projects, agents, or tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="border-slate-700 bg-slate-900/50 pl-10 text-slate-200 placeholder:text-slate-500 focus-visible:ring-violet-500"
            />
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="text-slate-400 hover:bg-slate-800 hover:text-slate-200"
          >
            <AnimatePresence mode="wait">
              {theme === 'dark' ? (
                <motion.div
                  key="moon"
                  initial={{ scale: 0, rotate: -90 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: 90 }}
                  transition={{ duration: 0.2 }}
                >
                  <Moon className="h-5 w-5" />
                </motion.div>
              ) : (
                <motion.div
                  key="sun"
                  initial={{ scale: 0, rotate: 90 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: -90 }}
                  transition={{ duration: 0.2 }}
                >
                  <Sun className="h-5 w-5" />
                </motion.div>
              )}
            </AnimatePresence>
          </Button>

          {/* Notifications */}
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
            <DropdownMenuContent
              align="end"
              className="w-[380px] border-slate-700 bg-slate-900"
            >
              <DropdownMenuLabel className="flex items-center justify-between">
                <span className="text-slate-200">Notifications</span>
                <Button variant="ghost" size="sm" className="h-auto text-xs text-violet-400 hover:text-violet-300">
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
                      <p className="text-sm font-medium text-slate-200">
                        {notification.title}
                      </p>
                      <p className="text-xs text-slate-400">
                        {notification.message}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {notification.timestamp}
                      </p>
                    </div>
                  </DropdownMenuItem>
                ))}
              </ScrollArea>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Profile */}
          <DropdownMenu>
            <DropdownMenuTrigger>
              <Button
                variant="ghost"
                className="relative h-9 w-9 rounded-full border border-slate-700 bg-slate-800 hover:bg-slate-700"
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-gradient-to-br from-violet-500 to-indigo-600 text-white text-sm">
                    JD
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-56 border-slate-700 bg-slate-900"
            >
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium text-slate-200">John Doe</p>
                  <p className="text-xs text-slate-400">john@example.com</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-slate-700" />
              <DropdownMenuItem className="text-slate-300 focus:bg-slate-800 focus:text-slate-200">
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="text-slate-300 focus:bg-slate-800 focus:text-slate-200">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-slate-700" />
              <DropdownMenuItem className="text-red-400 focus:bg-slate-800 focus:text-red-300">
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </motion.header>
  );
}
