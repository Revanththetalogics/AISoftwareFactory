'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { RealtimeProvider } from '@/components/layout/realtime-provider';
import { Sidebar } from '@/components/layout/sidebar';
import { TopNav } from '@/components/layout/top-nav';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { CommandPalette } from '@/components/shared/CommandPalette';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { commandPaletteOpen, setCommandPaletteOpen } = useKeyboardShortcuts();

  return (
    <ProtectedRoute>
      <RealtimeProvider>
        <div className="layout-container">
          <Sidebar />
          <div className="main-content">
            <TopNav />
            <div className="flex-1 overflow-auto">
              {children}
            </div>
          </div>
          <CommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />
        </div>
      </RealtimeProvider>
    </ProtectedRoute>
  );
}
