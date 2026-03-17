'use client';

import { Sidebar } from '@/components/layout/sidebar';
import { TopNav } from '@/components/layout/top-nav';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-950">
      <Sidebar />
      <TopNav />
      <main className="ml-[280px] mt-16 min-h-[calc(100vh-64px)] p-6">
        {children}
      </main>
    </div>
  );
}
