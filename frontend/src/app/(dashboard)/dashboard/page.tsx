'use client';

export const dynamic = 'force-dynamic';

import { Bot, Brain, Activity, Sparkles, Zap, ArrowRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { AgentCard, AgentGrid } from '@/components/system/agent-card';
import { SystemMetrics } from '@/components/system/metric-panel';
import { ExecutionTimeline } from '@/components/system/execution-timeline';
import { MiniLogViewer } from '@/components/system/log-stream';
import { containerVariants, slideVariants } from '@/lib/motion-variants';
import type { TimelinePhase } from '@/components/system/execution-timeline';
import type { LogLevel, LogEntry } from '@/components/system/log-stream';

// Mock agent data
const agents = [
  {
    agentId: 'agent-001',
    name: 'Backend Engineer',
    role: 'executor' as const,
    status: 'running' as const,
    currentTask: 'Building authentication API endpoints',
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
    currentTask: 'Designing user onboarding flow',
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

// Mock timeline phases
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

export default function DashboardPage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div 
        variants={slideVariants} 
        initial="hidden" 
        animate="visible"
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
          <p className="mt-1 text-text-secondary">
            Monitor your AI Software Factory operations in real-time
          </p>
        </div>
        <Button variant="ai-action">
          <Sparkles className="mr-2 h-4 w-4" />
          New Project
        </Button>
      </motion.div>

      {/* System Metrics */}
      <motion.div variants={slideVariants} initial="hidden" animate="visible">
        <SystemMetrics 
          cpu={45}
          memory={62}
          network={128}
          disk={38}
        />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Agent Activity */}
        <motion.div 
          variants={slideVariants} 
          initial="hidden" 
          animate="visible"
          className="lg:col-span-2"
        >
          <Card className="border-border-default bg-bg-panel">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg text-text-primary">Active Agents</CardTitle>
                <p className="text-sm text-text-secondary">
                  Real-time status of AI engineering team
                </p>
              </div>
              <Badge variant="secondary" className="bg-state-running-dim text-state-running">
                <Activity className="mr-1 h-3 w-3" />
                Live
              </Badge>
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
        </motion.div>

        {/* Project Pipeline */}
        <motion.div variants={slideVariants} initial="hidden" animate="visible">
          <Card className="border-border-default bg-bg-panel">
            <CardHeader>
              <CardTitle className="text-lg text-text-primary">Project Pipeline</CardTitle>
              <p className="text-sm text-text-secondary">
                Development lifecycle stages
              </p>
            </CardHeader>
            <CardContent>
              <ExecutionTimeline 
                phases={timelinePhases}
                compact
              />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Section: Logs & Projects */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Activity Logs */}
        <motion.div variants={slideVariants} initial="hidden" animate="visible">
          <Card className="border-border-default bg-bg-panel">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg text-text-primary">Activity Logs</CardTitle>
                <p className="text-sm text-text-secondary">
                  Latest system events and actions
                </p>
              </div>
              <Button variant="ghost" size="sm" className="text-state-running hover:text-state-running">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <MiniLogViewer logs={recentLogs} limit={6} />
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Projects */}
        <motion.div variants={slideVariants} initial="hidden" animate="visible">
          <Card className="border-border-default bg-bg-panel">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg text-text-primary">Recent Projects</CardTitle>
                <p className="text-sm text-text-secondary">
                  Your active software projects
                </p>
              </div>
              <Button variant="ghost" size="sm" className="text-state-running hover:text-state-running">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentProjects.map((project) => (
                  <div
                    key={project.id}
                    className="rounded-xl border border-border-subtle bg-bg-elevated p-4 transition-all hover:border-emphasis hover:bg-bg-hover"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20">
                          <Zap className="h-5 w-5 text-violet-400" />
                        </div>
                        <div>
                          <h4 className="font-medium text-text-primary">{project.name}</h4>
                          <div className="flex items-center gap-2 text-xs text-text-secondary">
                            <span className="flex items-center gap-1">
                              <Bot className="h-3 w-3" />
                              {project.stage}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <Brain className="h-3 w-3" />
                              {project.agents} agents
                            </span>
                          </div>
                        </div>
                      </div>
                      <Badge
                        variant="secondary"
                        className="bg-state-success-dim text-state-success"
                      >
                        Active
                      </Badge>
                    </div>
                    <div className="mt-4">
                      <div className="mb-2 flex items-center justify-between text-xs">
                        <span className="text-text-secondary">Progress</span>
                        <span className="font-mono text-text-code">{project.progress}%</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-bg-base">
                        <div
                          className="h-2 rounded-full bg-gradient-to-r from-violet-500 to-indigo-500 transition-all duration-300"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
