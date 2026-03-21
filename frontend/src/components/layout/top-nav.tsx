'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { ThemeToggle, UserProfile } from './user-profile';
import { NotificationCenter } from './notification-center';

export function TopNav() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header 
      className="fixed left-[--sidebar-width] right-0 top-0 z-30 h-[--topbar-height] border-b border-border-default bg-bg-panel/80 backdrop-blur-xl"
      style={{
        '--sidebar-width': '280px',
        '--topbar-height': '56px',
      } as React.CSSProperties}
      role="banner"
    >
      {/* Skip to main content link */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-2 focus:bg-bg-panel focus:text-text-primary focus:border focus:border-state-running focus:rounded"
      >
        Skip to main content
      </a>
      
      <div className="flex h-full items-center justify-between px-6">
        {/* Search */}
        <div className="flex max-w-md flex-1 items-center gap-4" role="search">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" aria-hidden="true" />
            <Input
              type="search"
              placeholder="Search projects, agents, or tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="border-border-default bg-bg-input pl-10 text-text-primary placeholder:text-text-tertiary focus-visible:border-state-running focus-visible:ring-3 focus-visible:ring-state-running/20"
              compact
              aria-label="Search projects, agents, or tasks"
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
