'use client';

import { useState } from 'react';
import { Search, Wifi, WifiOff } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ThemeToggle, UserProfile } from './user-profile';
import { NotificationCenter } from './notification-center';
import { useRealtime } from './realtime-provider';

export function TopNav() {
  const [searchQuery, setSearchQuery] = useState('');
  const { isConnected, isConnecting } = useRealtime();

  return (
    <header 
      className="top-navbar"
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
          {/* Connection Status */}
          <Badge 
            variant="outline" 
            className={`hidden sm:inline-flex ${
              isConnected 
                ? 'bg-state-success-dim text-state-success border-state-success/30' 
                : isConnecting 
                ? 'bg-state-warning-dim text-state-warning border-state-warning/30'
                : 'bg-state-error-dim text-state-error border-state-error/30'
            }`}
          >
            {isConnected ? (
              <>
                <Wifi className="mr-1.5 h-3 w-3" />
                Live
              </>
            ) : isConnecting ? (
              <>
                <WifiOff className="mr-1.5 h-3 w-3 animate-pulse" />
                Connecting...
              </>
            ) : (
              <>
                <WifiOff className="mr-1.5 h-3 w-3" />
                Offline
              </>
            )}
          </Badge>
          <ThemeToggle />
          <NotificationCenter />
          <UserProfile />
        </div>
      </div>
    </header>
  );
}
