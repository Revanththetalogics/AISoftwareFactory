'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { 
  Bot, 
  Brain, 
  Activity, 
  Zap, 
  ArrowRight, 
  Plus, 
  Search,
  Bell,
  Settings,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  Terminal,
  GitBranch,
  Play,
  Pause,
  RotateCcw,
  MoreHorizontal,
  Filter,
  LayoutGrid,
  List,
  ChevronRight,
  Flame,
  Target,
  Users,
  Code2,
  Rocket,
  Shield,
  Database,
  Cpu,
  HardDrive,
  Globe
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { motion, AnimatePresence } from 'framer-motion';
import { AgentCard, AgentGrid } from '@/components/system/agent-card';
import { SystemMetrics } from '@/components/system/metric-panel';
import { ExecutionTimeline } from '@/components/system/execution-timeline';
import { MiniLogViewer } from '@/components/system/log-stream';
import { QuickStartButton } from '@/components/project/QuickStartButton';
import { TemplateSelector } from '@/components/project/TemplateSelector';
import { AgentActivityFeed } from '@/components/agents/AgentActivityFeed';
import { AgentCollaborationView } from '@/components/agents/AgentCollaborationView';
import { CodeReviewInterface } from '@/components/codegen/CodeReviewInterface';
import { AutoTestGenerator } from '@/components/testing/AutoTestGenerator';
import { DeploymentPipeline } from '@/components/deployment/DeploymentPipeline';
import { DeploymentPreview } from '@/components/deployment/DeploymentPreview';
import { OptimizationAdvisor } from '@/components/infrastructure/OptimizationAdvisor';
import { CostEstimator } from '@/components/infrastructure/CostEstimator';
import { containerVariants, slideVariants } from '@/lib/motion-variants';
import { cn } from '@/lib/utils';
import type { TimelinePhase } from '@/components/system/execution-timeline';
import type { LogLevel, LogEntry } from '@/components/system/log-stream';

// ============================================
// MODERN DASHBOARD DATA MODEL
// ============================================

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'paused' | 'failed';
  progress: number;
  agents: number;
  stage: string;
  lastActive: string;
  icon: React.ElementType;
  color: string;
}

interface Agent {
  id: string;
  name: string;
  role: 'orchestrator' | 'executor' | 'validator' | 'deployer';
  status: 'idle' | 'running' | 'success' | 'error' | 'queued';
  currentTask?: string;
  progress: number;
  avatar: string;
  skills: string[];
}

interface Activity {
  id: string;
  type: 'code' | 'test' | 'deploy' | 'review' | 'design';
  message: string;
  agent: string;
  timestamp: string;
  project: string;
}

// Modern project data
const projects: Project[] = [
  {
    id: '1',
    name: 'SaaS Dashboard',
    description: 'AI-powered analytics platform',
    status: 'active',
    progress: 67,
    agents: 4,
    stage: 'Implementation',
    lastActive: '2 min ago',
    icon: LayoutGrid,
    color: 'from-violet-500 to-purple-600',
  },
  {
    id: '2',
    name: 'E-commerce API',
    description: 'Headless commerce backend',
    status: 'active',
    progress: 34,
    agents: 3,
    stage: 'Architecture',
    lastActive: '15 min ago',
    icon: Database,
    color: 'from-blue-500 to-cyan-600',
  },
  {
    id: '3',
    name: 'Mobile App',
    description: 'React Native fitness tracker',
    status: 'paused',
    progress: 89,
    agents: 2,
    stage: 'Testing',
    lastActive: '2 hours ago',
    icon: Globe,
    color: 'from-emerald-500 to-teal-600',
  },
];

// Modern agent data (mapped to AgentCard props)
const agents = [
  {
    agentId: 'agent-001',
    name: 'Backend Engineer',
    role: 'executor' as const,
    status: 'running' as const,
    currentTask: 'Building authentication API',
    progress: 67,
    metrics: {
      tasksCompleted: 24,
      avgExecutionTime: '2m 34s',
      successRate: 96.5,
    },
  },
  {
    agentId: 'agent-002',
    name: 'UX Designer',
    role: 'executor' as const,
    status: 'running' as const,
    currentTask: 'Designing onboarding flow',
    progress: 45,
    metrics: {
      tasksCompleted: 18,
      avgExecutionTime: '3m 12s',
      successRate: 94.2,
    },
  },
  {
    agentId: 'agent-003',
    name: 'QA Engineer',
    role: 'validator' as const,
    status: 'success' as const,
    currentTask: 'Integration tests completed',
    progress: 100,
    metrics: {
      tasksCompleted: 32,
      avgExecutionTime: '1m 48s',
      successRate: 98.1,
    },
  },
  {
    agentId: 'agent-004',
    name: 'DevOps Engineer',
    role: 'deployer' as const,
    status: 'idle' as const,
    currentTask: undefined,
    progress: 0,
    metrics: {
      tasksCompleted: 15,
      avgExecutionTime: '4m 05s',
      successRate: 100,
    },
  },
];

// Recent projects for backward compatibility
const recentProjects = [
  {
    id: '1',
    name: 'SaaS Dashboard',
    stage: 'Design',
    progress: 45,
    agents: 3,
    status: 'active',
  },
  {
    id: '2',
    name: 'E-commerce API',
    stage: 'Planning',
    progress: 25,
    agents: 2,
    status: 'active',
  },
];

// Modern activity feed
const activities: Activity[] = [
  { id: '1', type: 'code', message: 'Generated 12 API endpoints', agent: 'Backend Engineer', timestamp: '2m ago', project: 'SaaS Dashboard' },
  { id: '2', type: 'test', message: 'All tests passed (48/48)', agent: 'QA Engineer', timestamp: '5m ago', project: 'SaaS Dashboard' },
  { id: '3', type: 'design', message: 'Completed wireframe v2', agent: 'UX Designer', timestamp: '12m ago', project: 'E-commerce API' },
  { id: '4', type: 'deploy', message: 'Deployed to staging', agent: 'DevOps Engineer', timestamp: '30m ago', project: 'SaaS Dashboard' },
];

// Stats data
const stats = [
  { label: 'Active Projects', value: 3, change: '+1', trend: 'up', icon: Target },
  { label: 'AI Agents', value: 12, change: '+4', trend: 'up', icon: Bot },
  { label: 'Tasks Completed', value: 284, change: '+24', trend: 'up', icon: CheckCircle2 },
  { label: 'Success Rate', value: '96.5%', change: '+2.1%', trend: 'up', icon: TrendingUp },
];

// Timeline phases
const timelinePhases: TimelinePhase[] = [
  {
    id: '1',
    name: 'Idea',
    status: 'completed',
    startTime: new Date('2024-01-15T09:00:00'),
    endTime: new Date('2024-01-15T10:30:00'),
    duration: '1h 30m',
    steps: [
      { name: 'Product concept defined', status: 'completed', timestamp: new Date('2024-01-15T09:00:00') },
      { name: 'Market research completed', status: 'completed', timestamp: new Date('2024-01-15T10:30:00') },
    ],
  },
  {
    id: '2',
    name: 'Planning',
    status: 'completed',
    startTime: new Date('2024-01-15T11:00:00'),
    endTime: new Date('2024-01-15T14:00:00'),
    duration: '3h 0m',
    steps: [
      { name: 'Requirements gathered', status: 'completed', timestamp: new Date('2024-01-15T11:00:00') },
      { name: 'Technical specs defined', status: 'completed', timestamp: new Date('2024-01-15T14:00:00') },
    ],
  },
  {
    id: '3',
    name: 'Design',
    status: 'running',
    startTime: new Date('2024-01-15T14:30:00'),
    duration: 'In progress',
    steps: [
      { name: 'Architecture design', status: 'completed', timestamp: new Date('2024-01-15T14:30:00') },
      { name: 'UX wireframes', status: 'running', timestamp: new Date('2024-01-15T16:00:00') },
      { name: 'UI mockups', status: 'pending', timestamp: new Date('2024-01-15T17:00:00') },
    ],
  },
  {
    id: '4',
    name: 'Engineering',
    status: 'pending',
    duration: 'Pending',
  },
];

// Mock recent logs
const recentLogs: LogEntry[] = [
  {
    id: '1',
    level: 'info' as LogLevel,
    source: 'Backend Agent',
    message: 'Generated 12 API endpoints successfully',
    timestamp: new Date(Date.now() - 1000 * 60 * 2),
  },
  {
    id: '2',
    level: 'success' as LogLevel,
    source: 'QA Agent',
    message: 'All integration tests passed (48/48)',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
  {
    id: '3',
    level: 'warn' as LogLevel,
    source: 'UX Agent',
    message: 'Component complexity slightly above threshold',
    timestamp: new Date(Date.now() - 1000 * 60 * 12),
  },
  {
    id: '4',
    level: 'info' as LogLevel,
    source: 'DevOps Agent',
    message: 'Docker containers health check passed',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
];

// ============================================
// MODERN DASHBOARD COMPONENT
// ============================================

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-bg-base">
        {/* Modern Header */}
        <header className="sticky top-0 z-30 border-b border-border-default bg-bg-panel/80 backdrop-blur-xl">
          <div className="flex h-16 items-center justify-between px-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-state-queued to-state-running">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-text-primary">AI Factory</h1>
                  <p className="text-xs text-text-secondary">Software Engineering</p>
                </div>
              </div>
              <Separator orientation="vertical" className="h-8" />
              <nav className="hidden md:flex items-center gap-1">
                <Button variant="ghost" size="sm" className="text-text-secondary">Dashboard</Button>
                <Button variant="ghost" size="sm" className="text-text-secondary">Projects</Button>
                <Button variant="ghost" size="sm" className="text-text-secondary">Agents</Button>
              </nav>
            </div>
            <div className="flex items-center gap-3">
              <div className="relative hidden sm:block">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
                <Input 
                  placeholder="Search projects, agents..." 
                  className="w-64 pl-9 bg-bg-elevated border-border-subtle"
                />
              </div>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5 text-text-secondary" />
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-state-error" />
              </Button>
              <Avatar className="h-9 w-9 border-2 border-border-default">
                <AvatarFallback className="bg-state-queued-dim text-state-queued text-sm font-medium">
                  JD
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="p-6">
          <div className="mx-auto max-w-7xl space-y-8">
            {/* Welcome Section */}
            <section className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-text-primary">Good morning, John</h2>
                <p className="text-text-secondary mt-1">
                  Your AI team has completed <span className="text-state-success font-medium">24 tasks</span> today
                </p>
              </div>
              <div className="flex items-center gap-3">
                <TemplateSelector />
                <QuickStartButton />
              </div>
            </section>

            {/* Stats Grid */}
            <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="border-border-default bg-bg-panel hover:border-emphasis transition-colors">
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-sm text-text-secondary">{stat.label}</p>
                          <p className="text-2xl font-bold text-text-primary mt-1">{stat.value}</p>
                        </div>
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-state-running-dim">
                          <stat.icon className="h-5 w-5 text-state-running" />
                        </div>
                      </div>
                      <div className="flex items-center gap-1 mt-3">
                        <TrendingUp className="h-3 w-3 text-state-success" />
                        <span className="text-xs text-state-success font-medium">{stat.change}</span>
                        <span className="text-xs text-text-tertiary">vs last week</span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </section>

            {/* Main Dashboard Grid */}
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Left Column - Projects & Agents */}
              <div className="lg:col-span-2 space-y-6">
                {/* Active Projects */}
                <Card className="border-border-default bg-bg-panel">
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">Active Projects</CardTitle>
                        <CardDescription>Your ongoing software projects</CardDescription>
                      </div>
                      <Button variant="outline" size="sm">
                        View All
                        <ChevronRight className="ml-1 h-4 w-4" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {projects.map((project) => (
                      <div
                        key={project.id}
                        className="group flex items-center gap-4 p-4 rounded-xl border border-border-subtle bg-bg-elevated/50 hover:bg-bg-hover hover:border-emphasis transition-all cursor-pointer"
                      >
                        <div className={cn(
                          "flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br",
                          project.color
                        )}>
                          <project.icon className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-text-primary truncate">{project.name}</h3>
                            <Badge 
                              variant={project.status === 'active' ? 'default' : 'secondary'}
                              className="text-xs"
                            >
                              {project.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-text-secondary truncate">{project.description}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-text-tertiary">
                            <span className="flex items-center gap-1">
                              <Target className="h-3 w-3" />
                              {project.stage}
                            </span>
                            <span className="flex items-center gap-1">
                              <Bot className="h-3 w-3" />
                              {project.agents} agents
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {project.lastActive}
                            </span>
                          </div>
                        </div>
                        <div className="w-24">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-text-tertiary">{project.progress}%</span>
                          </div>
                          <Progress value={project.progress} className="h-1.5" />
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* AI Agents */}
                <Card className="border-border-default bg-bg-panel">
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">AI Agents</CardTitle>
                        <CardDescription>Your engineering team status</CardDescription>
                      </div>
                      <Badge variant="outline" className="bg-state-running-dim text-state-running">
                        <Activity className="mr-1 h-3 w-3" />
                        Live
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <AgentGrid columns={2}>
                      {agents.map((agent) => (
                        <AgentCard
                          key={agent.agentId}
                          agentId={agent.agentId}
                          name={agent.name}
                          role={agent.role}
                          status={agent.status}
                          currentTask={agent.currentTask}
                          progress={agent.progress}
                          metrics={agent.metrics}
                          compact
                        />
                      ))}
                    </AgentGrid>
                  </CardContent>
                </Card>
              </div>

              {/* Right Column - Activity & Quick Actions */}
              <div className="space-y-6">
                {/* Quick Actions */}
                <Card className="border-border-default bg-bg-panel">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-lg">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button variant="outline" className="w-full justify-start h-auto py-3 px-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-state-queued-dim mr-3">
                        <Plus className="h-5 w-5 text-state-queued" />
                      </div>
                      <div className="text-left">
                        <p className="font-medium text-text-primary">New Project</p>
                        <p className="text-xs text-text-secondary">Start building with AI</p>
                      </div>
                    </Button>
                    <Button variant="outline" className="w-full justify-start h-auto py-3 px-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-state-running-dim mr-3">
                        <Terminal className="h-5 w-5 text-state-running" />
                      </div>
                      <div className="text-left">
                        <p className="font-medium text-text-primary">Code Review</p>
                        <p className="text-xs text-text-secondary">Analyze recent changes</p>
                      </div>
                    </Button>
                    <Button variant="outline" className="w-full justify-start h-auto py-3 px-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-state-success-dim mr-3">
                        <Rocket className="h-5 w-5 text-state-success" />
                      </div>
                      <div className="text-left">
                        <p className="font-medium text-text-primary">Deploy</p>
                        <p className="text-xs text-text-secondary">Push to production</p>
                      </div>
                    </Button>
                  </CardContent>
                </Card>

                {/* Recent Activity */}
                <Card className="border-border-default bg-bg-panel">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-lg">Recent Activity</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {activities.map((activity) => (
                      <div key={activity.id} className="flex items-start gap-3">
                        <div className={cn(
                          "flex h-8 w-8 items-center justify-center rounded-lg shrink-0",
                          activity.type === 'code' && "bg-state-running-dim",
                          activity.type === 'test' && "bg-state-success-dim",
                          activity.type === 'design' && "bg-state-queued-dim",
                          activity.type === 'deploy' && "bg-state-warning-dim"
                        )}>
                          {activity.type === 'code' && <Code2 className="h-4 w-4 text-state-running" />}
                          {activity.type === 'test' && <CheckCircle2 className="h-4 w-4 text-state-success" />}
                          {activity.type === 'design' && <LayoutGrid className="h-4 w-4 text-state-queued" />}
                          {activity.type === 'deploy' && <Rocket className="h-4 w-4 text-state-warning" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-text-primary">{activity.message}</p>
                          <p className="text-xs text-text-secondary">
                            {activity.agent} • {activity.timestamp}
                          </p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* System Health */}
                <Card className="border-border-default bg-bg-panel">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-lg">System Health</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Cpu className="h-5 w-5 text-text-secondary" />
                        <span className="text-sm text-text-secondary">CPU</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress value={45} className="w-20 h-1.5" />
                        <span className="text-sm font-medium text-text-primary w-10 text-right">45%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Database className="h-5 w-5 text-text-secondary" />
                        <span className="text-sm text-text-secondary">Memory</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress value={62} className="w-20 h-1.5" />
                        <span className="text-sm font-medium text-text-primary w-10 text-right">62%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <HardDrive className="h-5 w-5 text-text-secondary" />
                        <span className="text-sm text-text-secondary">Storage</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress value={38} className="w-20 h-1.5" />
                        <span className="text-sm font-medium text-text-primary w-10 text-right">38%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </main>
      </div>
    </TooltipProvider>
  );
}
