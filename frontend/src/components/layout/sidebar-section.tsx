'use client';

import { Separator } from '@/components/ui/separator';
import { SidebarNavItem } from './sidebar-nav-item';
import type { LucideIcon } from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
}

interface SidebarSectionProps {
  title: string;
  items: NavItem[];
  pathname: string;
  colorScheme: {
    active: string;
    inactive: string;
  };
}

export function SidebarSection({ title, items, pathname, colorScheme }: SidebarSectionProps) {
  return (
    <>
      <div className="mb-2 px-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </h3>
      </div>
      <nav className="space-y-1 px-3">
        {items.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <SidebarNavItem
              key={item.href}
              {...item}
              isActive={isActive}
              colorScheme={colorScheme}
            />
          );
        })}
      </nav>
      <Separator className="my-4 bg-slate-800" />
    </>
  );
}
