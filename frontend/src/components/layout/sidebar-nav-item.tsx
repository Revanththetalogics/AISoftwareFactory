'use client';

import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';

interface SidebarNavItemProps {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
  isActive: boolean;
  colorScheme: {
    active: string;
    inactive: string;
  };
}

export function SidebarNavItem({
  label,
  href,
  icon: Icon,
  badge,
  isActive,
  colorScheme,
}: SidebarNavItemProps) {
  return (
    <Link 
      key={href} 
      href={href}
      aria-current={isActive ? 'page' : undefined}
    >
      <button
        className={cn(
          'w-full justify-start gap-3 px-3 py-4 text-sm font-medium transition-all duration-200',
          isActive
            ? `${colorScheme.active} bg-gradient-to-r`
            : colorScheme.inactive,
        )}
      >
        <Icon className={cn('h-4 w-4', isActive && colorScheme.active.split(' ')[1])} aria-hidden="true" />
        <span className="flex-1">{label}</span>
        {badge && (
          <span 
            className={`rounded-full ${colorScheme.active.split(' ')[2]} px-2 py-0.5 text-xs`}
            aria-label={`${label} badge: ${badge}`}
          >
            {badge}
          </span>
        )}
      </button>
    </Link>
  );
}
