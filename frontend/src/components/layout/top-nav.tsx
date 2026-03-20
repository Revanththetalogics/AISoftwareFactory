'use client';

import { useState } from 'react';
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

export function TopNav() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header className="fixed left-[280px] right-0 top-0 z-30 h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl">
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
    </header>
  );
}
