'use client';

import { Card } from '@/components/ui/card';

export function SidebarStats() {
  return (
    <div className="px-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
        System Status
      </h3>
      <Card className="border-slate-800 bg-slate-900/50 p-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Agents</span>
            <span className="font-medium text-emerald-400">4 Active</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Projects</span>
            <span className="font-medium text-blue-400">2 Running</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Health</span>
            <div className="flex items-center gap-1.5 font-medium text-emerald-400">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400"></span>
              </span>
              Healthy
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
