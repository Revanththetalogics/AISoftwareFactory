'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { RealtimeProvider } from '@/components/layout/realtime-provider';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <RealtimeProvider>
        <div className="h-screen w-screen overflow-hidden">
          {children}
        </div>
      </RealtimeProvider>
    </ProtectedRoute>
  );
}
