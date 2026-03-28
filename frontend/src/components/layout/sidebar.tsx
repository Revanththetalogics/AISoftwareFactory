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
    <aside 
      className="sidebar-panel"
      role="complementary"
      aria-label="Application sidebar"
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-[--topbar-height] items-center gap-3 border-b border-border-default px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-state-queued to-state-running shadow-lg shadow-state-running/20" aria-hidden="true">
            <Sparkles className="h-5 w-5 text-text-primary" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-text-primary">AI Factory</h1>
            <p className="text-xs text-text-secondary">Software Engineering</p>
          </div>
        </div>

        <ScrollArea className="flex-1 py-4">
          {/* Main Navigation */}
          <nav className="space-y-1 px-3" role="navigation" aria-label="Main navigation">
            {mainNavItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;

              return (
                <Link 
                  key={item.href} 
                  href={item.href}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Button
                    variant="ghost"
                    className={cn(
                      'w-full justify-start gap-3 px-3 py-5 text-sm font-medium transition-all duration-fast ease-smooth',
                      isActive
                        ? 'bg-state-running-dim text-state-running hover:bg-state-running-dim/30 hover:text-state-running'
                        : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary',
                    )}
                  >
                    <Icon className={cn('h-5 w-5', isActive && 'text-state-running')} aria-hidden="true" />
                    <span className="flex-1">{item.label}</span>
                    {item.badge && (
                      <span className="rounded-full bg-state-running-dim px-2 py-0.5 text-xs text-state-running" aria-label={`${item.label} badge: ${item.badge}`}>
                        {item.badge}
                      </span>
                    )}
                  </Button>
                </Link>
              );
            })}
          </nav>

          <Separator className="my-4 bg-border-subtle" />

          {/* AI Agent Orchestration */}
          <SidebarSection
            title="AI Agents"
            items={agentNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'bg-state-running-dim text-state-running hover:bg-state-running-dim/30',
              inactive: 'text-text-secondary hover:bg-bg-hover hover:text-text-primary',
            }}
          />

          {/* Code Generation & Validation */}
          <SidebarSection
            title="Code Generation"
            items={codeNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'bg-state-success-dim text-state-success hover:bg-state-success-dim/30',
              inactive: 'text-text-secondary hover:bg-bg-hover hover:text-text-primary',
            }}
          />

          {/* AI Testing & Quality Assurance */}
          <SidebarSection
            title="Testing & QA"
            items={testingNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'bg-state-warning-dim text-state-warning hover:bg-state-warning-dim/30',
              inactive: 'text-text-secondary hover:bg-bg-hover hover:text-text-primary',
            }}
          />

          {/* Infrastructure & Deployment */}
          <SidebarSection
            title="Infrastructure"
            items={infraNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'bg-state-running-dim text-state-running hover:bg-state-running-dim/30',
              inactive: 'text-text-secondary hover:bg-bg-hover hover:text-text-primary',
            }}
          />

          {/* Observability & Security */}
          <SidebarSection
            title="Observability"
            items={observabilityNavItems}
            pathname={pathname}
            colorScheme={{
              active: 'bg-state-error-dim text-state-error hover:bg-state-error-dim/30',
              inactive: 'text-text-secondary hover:bg-bg-hover hover:text-text-primary',
            }}
          />

          {/* Quick Stats */}
          <SidebarStats />
        </ScrollArea>

        {/* Bottom Navigation */}
        <nav className="border-t border-border-default p-3" role="navigation" aria-label="Settings navigation">
          {bottomNavItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link 
                key={item.href} 
                href={item.href}
                aria-current={isActive ? 'page' : undefined}
              >
                <Button
                  variant="ghost"
                  className={cn(
                    'w-full justify-start gap-3 px-3 py-5 text-sm font-medium transition-all duration-fast ease-smooth',
                    isActive
                      ? 'bg-bg-selected text-text-primary'
                      : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
                  )}
                >
                  <Icon className="h-5 w-5" aria-hidden="true" />
                  <span className="flex-1">{item.label}</span>
                </Button>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
