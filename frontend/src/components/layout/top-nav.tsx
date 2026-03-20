'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ThemeToggle, UserProfile } from './user-profile';
import { NotificationCenter } from './notification-center';

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
  const [searchQuery, setSearchQuery] = useState('');

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
          <ThemeToggle />
          <NotificationCenter />
          <UserProfile />
        </div>
      </div>
    </motion.header>
  );
}
