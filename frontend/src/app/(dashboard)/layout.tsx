'use client';

import { Sidebar } from '@/components/layout/sidebar';
import { TopNav } from '@/components/layout/top-nav';
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
        <div className="min-h-screen bg-bg-base">
          <Sidebar />
          <TopNav />
          <main 
            id="main-content"
            role="main"
            className="fixed left-[--sidebar-width] right-0 top-[--topbar-height] bottom-0 overflow-auto bg-bg-base p-6"
            style={{
              '--sidebar-width': '280px',
              '--topbar-height': '56px',
            } as React.CSSProperties}
          >
            <div className="mx-auto max-w-[1600px]">
              {children}
            </div>
          </main>
        </div>
      </RealtimeProvider>
    </ProtectedRoute>
  );
}
