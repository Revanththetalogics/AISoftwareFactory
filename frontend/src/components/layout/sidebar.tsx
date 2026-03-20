'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FolderKanban,
  Bot,
  FlaskConical,
  GitBranch,
  Rocket,
  Settings,
  Sparkles,
  ShieldCheck,
  Brain,
  Code2,
  Workflow,
  TestTube,
  LineChart,
  Database,
  Cloud,
  Zap,
  FileCode,
  Eye,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { SidebarSection } from './sidebar-section';
import { SidebarStats } from './sidebar-stats';
import type { LucideIcon } from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
}

// Main Features - AI Agent Orchestration & Software Lifecycle
const mainNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Projects', href: '/projects', icon: FolderKanban },
];

// AI Agent Features
const agentNavItems: NavItem[] = [
  { label: 'Agent Crews', href: '/agents', icon: Bot, badge: '6 Crews' },
  { label: 'Workflows', href: '/workflows', icon: Workflow },
  { label: 'Knowledge Base', href: '/knowledge', icon: Brain },
];

// Code Generation & Validation
const codeNavItems: NavItem[] = [
  { label: 'Code Generator', href: '/codegen', icon: Code2 },
  { label: 'Architecture', href: '/architecture', icon: GitBranch },
  { label: 'File Manager', href: '/files', icon: FileCode },
];

// AI Testing & Quality Assurance
const testingNavItems: NavItem[] = [
  { label: 'Testing', href: '/testing', icon: TestTube, badge: 'AI' },
  { label: 'Simulations', href: '/simulations', icon: FlaskConical },
  { label: 'Visual Regression', href: '/visual-testing', icon: Eye },
];

// Infrastructure & Deployment
const infraNavItems: NavItem[] = [
  { label: 'Deployment', href: '/deployment', icon: Rocket },
  { label: 'Infrastructure', href: '/infrastructure', icon: Cloud },
  { label: 'Database', href: '/database', icon: Database },
];

// Observability & Security
const observabilityNavItems: NavItem[] = [
  { label: 'Monitoring', href: '/monitoring', icon: LineChart },
  { label: 'Security', href: '/security', icon: ShieldCheck },
  { label: 'Performance', href: '/performance', icon: Zap },
];

const bottomNavItems: NavItem[] = [
  { label: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-[280px] border-r border-slate-800 bg-slate-950/95 backdrop-blur-xl">
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
          {/* Main Navigation */}
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
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200',
                    )}
                  >
                    <Icon className={cn('h-5 w-5', isActive && 'text-violet-400')} />
                    <span className="flex-1">{item.label}</span>
                    {item.badge && (
                      <span className="rounded-full bg-violet-500/20 px-2 py-0.5 text-xs text-violet-300">
                        {item.badge}
                      </span>
                    )}
                  </Button>
                </Link>
              );
            })}
          </nav>

          <Separator className="my-4 bg-slate-800" />

          {/* AI Agent Orchestration */}
          <SidebarSection
            title="AI Agents"
            items={agentNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'from-blue-500/10 to-transparent text-blue-400 hover:bg-blue-500/20 hover:text-blue-300',
              inactive: 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200',
            }}
          />

          {/* Code Generation & Validation */}
          <SidebarSection
            title="Code Generation"
            items={codeNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'from-emerald-500/10 to-transparent text-emerald-400 hover:bg-emerald-500/20 hover:text-emerald-300',
              inactive: 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200',
            }}
          />

          {/* AI Testing & Quality Assurance */}
          <SidebarSection
            title="Testing & QA"
            items={testingNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'from-amber-500/10 to-transparent text-amber-400 hover:bg-amber-500/20 hover:text-amber-300',
              inactive: 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200',
            }}
          />

          {/* Infrastructure & Deployment */}
          <SidebarSection
            title="Infrastructure"
            items={infraNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'from-cyan-500/10 to-transparent text-cyan-400 hover:bg-cyan-500/20 hover:text-cyan-300',
              inactive: 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200',
            }}
          />

          {/* Observability & Security */}
          <SidebarSection
            title="Observability"
            items={observabilityNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'from-rose-500/10 to-transparent text-rose-400 hover:bg-rose-500/20 hover:text-rose-300',
              inactive: 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200',
            }}
          />

          {/* Quick Stats */}
          <SidebarStats />
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
    </aside>
  );
}
