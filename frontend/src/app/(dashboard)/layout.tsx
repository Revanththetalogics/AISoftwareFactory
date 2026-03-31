'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { RealtimeProvider } from '@/components/layout/realtime-provider';
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
        <div className="h-screen w-screen overflow-hidden">
          {children}
          <CommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />
        </div>
      </RealtimeProvider>
    </ProtectedRoute>
  );
}
