'use client';

import { Card } from '@/components/ui/card';

export function SidebarStats() {
  return (
    <div className="px-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-text-tertiary">
        System Status
      </h3>
      <Card className="border-border-default bg-bg-panel/50 p-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-text-secondary">Agents</span>
            <span className="font-medium text-state-success">4 Active</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-text-secondary">Projects</span>
            <span className="font-medium text-state-running">2 Running</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-text-secondary">Health</span>
            <div className="flex items-center gap-1.5 font-medium text-state-success">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-state-success opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-state-success"></span>
              </span>
              Healthy
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
