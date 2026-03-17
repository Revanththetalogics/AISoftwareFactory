'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  FolderKanban,
  Bot,
  FlaskConical,
  GitBranch,
  Rocket,
  Settings,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const mainNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Projects', href: '/projects', icon: FolderKanban },
  { label: 'Agents', href: '/agents', icon: Bot },
  { label: 'Simulations', href: '/simulations', icon: FlaskConical },
  { label: 'Architecture', href: '/architecture', icon: GitBranch },
  { label: 'Deployment', href: '/deployment', icon: Rocket },
];

const bottomNavItems: NavItem[] = [
  { label: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <motion.aside
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="fixed left-0 top-0 z-40 h-screen w-[280px] border-r border-slate-800 bg-slate-950/95 backdrop-blur-xl"
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-100">AI Factory</h1>
            <p className="text-xs text-slate-400">Software Engineering</p>
          </div>
        </div>

        <ScrollArea className="flex-1 py-4">
          <nav className="space-y-1 px-3">
            {mainNavItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;

              return (
                <Link key={item.href} href={item.href}>
                  <Button
                    variant="ghost"
                    className={cn(
                      'w-full justify-start gap-3 px-3 py-5 text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'bg-gradient-to-r from-violet-500/10 to-transparent text-violet-400 hover:bg-violet-500/20 hover:text-violet-300'
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    )}
                  >
                    <Icon className={cn('h-5 w-5', isActive && 'text-violet-400')} />
                    <span className="flex-1">{item.label}</span>
                    {item.badge && (
                      <span className="rounded-full bg-violet-500/20 px-2 py-0.5 text-xs text-violet-300">
                        {item.badge}
                      </span>
                    )}
                    {isActive && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="absolute right-3 h-1.5 w-1.5 rounded-full bg-violet-400"
                      />
                    )}
                  </Button>
                </Link>
              );
            })}
          </nav>

          <Separator className="my-4 bg-slate-800" />

          {/* Quick Stats */}
          <div className="px-4">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
              System Status
            </h3>
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
                <span className="flex items-center gap-1.5 font-medium text-emerald-400">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  Healthy
                </span>
              </div>
            </div>
          </div>
        </ScrollArea>

        {/* Bottom Navigation */}
        <div className="border-t border-slate-800 p-3">
          {bottomNavItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link key={item.href} href={item.href}>
                <Button
                  variant="ghost"
                  className={cn(
                    'w-full justify-start gap-3 px-3 py-5 text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-slate-800 text-slate-200'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span className="flex-1">{item.label}</span>
                </Button>
              </Link>
            );
          })}
        </div>
      </div>
    </motion.aside>
  );
}
