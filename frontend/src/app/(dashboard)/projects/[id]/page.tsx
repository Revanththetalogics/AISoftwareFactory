'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Play,
  Pause,
  RotateCcw,
  GitBranch,
  FileCode,
  TestTube,
  Rocket,
  MoreHorizontal,
  Clock,
  CheckCircle2,
  Loader2,
  Terminal,
  Bot,
  Activity,
} from 'lucide-react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ExecutionTimeline } from '@/components/system/execution-timeline';
import { AgentCard, AgentGrid } from '@/components/system/agent-card';
import { MiniLogViewer } from '@/components/system/log-stream';
import { DeploymentStatusCard } from '@/components/system/deployment-status-card';
import type { TimelinePhase } from '@/components/system/execution-timeline';
import type { LogEntry, LogLevel } from '@/components/system/log-stream';

// Project phases pipeline
const projectPhases = [
  { id: 'idea', name: 'Idea', icon: Activity },
  { id: 'requirements', name: 'Requirements', icon: FileCode },
  { id: 'architecture', name: 'Architecture', icon: GitBranch },
  { id: 'implementation', name: 'Implementation', icon: Bot },
  { id: 'testing', name: 'Testing', icon: TestTube },
  { id: 'deployment', name: 'Deployment', icon: Rocket },
  { id: 'complete', name: 'Complete', icon: CheckCircle2 },
];

// Mock project data
const mockProject = {
  id: 'proj-001',
  name: 'SaaS Analytics Dashboard',
  description: 'AI-powered analytics platform with real-time data visualization and predictive insights.',
  status: 'active',
  currentPhase: 'implementation',
  progress: 65,
  createdAt: '2024-01-15T09:00:00',
  estimatedCompletion: '2024-02-01T18:00:00',
};

// Mock timeline phases
const timelinePhases: TimelinePhase[] = [
  {
    id: '1',
    name: 'Idea Validation',
    status: 'completed',
    startTime: new Date('2024-01-15T09:00:00'),
    endTime: new Date('2024-01-15T11:30:00'),
    duration: '2h 30m',
    steps: [
      { name: 'Market research analysis', status: 'completed', timestamp: new Date('2024-01-15T09:30:00') },
      { name: 'Competitor analysis', status: 'completed', timestamp: new Date('2024-01-15T10:15:00') },
      { name: 'Feasibility study', status: 'completed', timestamp: new Date('2024-01-15T11:30:00') },
    ],
  },
  {
    id: '2',
    name: 'Requirements Gathering',
    status: 'completed',
    startTime: new Date('2024-01-15T12:00:00'),
    endTime: new Date('2024-01-15T16:00:00'),
    duration: '4h 0m',
    steps: [
      { name: 'User stories defined', status: 'completed', timestamp: new Date('2024-01-15T13:00:00') },
      { name: 'Technical requirements', status: 'completed', timestamp: new Date('2024-01-15T14:30:00') },
      { name: 'API specifications', status: 'completed', timestamp: new Date('2024-01-15T16:00:00') },
    ],
  },
  {
    id: '3',
    name: 'Architecture Design',
    status: 'completed',
    startTime: new Date('2024-01-16T09:00:00'),
    endTime: new Date('2024-01-16T15:00:00'),
    duration: '6h 0m',
    steps: [
      { name: 'System architecture diagram', status: 'completed', timestamp: new Date('2024-01-16T11:00:00') },
      { name: 'Database schema design', status: 'completed', timestamp: new Date('2024-01-16T13:00:00') },
      { name: 'Microservices layout', status: 'completed', timestamp: new Date('2024-01-16T15:00:00') },
    ],
  },
  {
    id: '4',
    name: 'Implementation',
    status: 'running',
    startTime: new Date('2024-01-17T09:00:00'),
    duration: 'In progress',
    steps: [
      { name: 'Frontend components', status: 'completed', timestamp: new Date('2024-01-17T14:00:00') },
      { name: 'Backend API endpoints', status: 'running', timestamp: new Date('2024-01-18T10:00:00') },
      { name: 'Database migrations', status: 'pending', timestamp: new Date('2024-01-18T16:00:00') },
      { name: 'Authentication system', status: 'pending', timestamp: new Date('2024-01-19T09:00:00') },
    ],
  },
  {
    id: '5',
    name: 'Testing',
    status: 'pending',
    duration: 'Pending',
  },
  {
    id: '6',
    name: 'Deployment',
    status: 'pending',
    duration: 'Pending',
  },
];

// Mock agents
const projectAgents = [
  {
    agentId: 'agent-001',
    name: 'CEO Agent',
    role: 'orchestrator' as const,
    status: 'success' as const,
    currentTask: 'Project oversight complete',
    progress: 100,
    metrics: {
      tasksCompleted: 12,
      avgExecutionTime: '5m 20s',
      successRate: 98.5,
    },
  },
  {
    agentId: 'agent-002',
    name: 'Architect Agent',
    role: 'orchestrator' as const,
    status: 'success' as const,
    currentTask: 'Architecture finalized',
    progress: 100,
    metrics: {
      tasksCompleted: 8,
      avgExecutionTime: '12m 45s',
      successRate: 100,
    },
  },
  {
    agentId: 'agent-003',
    name: 'Backend Engineer',
    role: 'executor' as const,
    status: 'running' as const,
    currentTask: 'Building API authentication layer',
    progress: 72,
    metrics: {
      tasksCompleted: 24,
      avgExecutionTime: '8m 30s',
      successRate: 94.2,
    },
  },
  {
    agentId: 'agent-004',
    name: 'Frontend Engineer',
    role: 'executor' as const,
    status: 'running' as const,
    currentTask: 'Implementing dashboard charts',
    progress: 58,
    metrics: {
      tasksCompleted: 18,
      avgExecutionTime: '6m 15s',
      successRate: 96.8,
    },
  },
  {
    agentId: 'agent-005',
    name: 'QA Engineer',
    role: 'validator' as const,
    status: 'idle' as const,
    currentTask: undefined,
    progress: 0,
    metrics: {
      tasksCompleted: 0,
      avgExecutionTime: '4m 50s',
      successRate: 99.1,
    },
  },
  {
    agentId: 'agent-006',
    name: 'DevOps Engineer',
    role: 'deployer' as const,
    status: 'idle' as const,
    currentTask: undefined,
    progress: 0,
    metrics: {
      tasksCompleted: 0,
      avgExecutionTime: '10m 20s',
      successRate: 100,
    },
  },
];

// Mock logs
const projectLogs: LogEntry[] = [
  {
    id: '1',
    level: 'info' as LogLevel,
    source: 'Backend Agent',
    message: 'Generated authentication middleware with JWT support',
    timestamp: new Date(Date.now() - 1000 * 60 * 2),
  },
  {
    id: '2',
    level: 'success' as LogLevel,
    source: 'Frontend Agent',
    message: 'Completed dashboard layout component with responsive grid',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
  {
    id: '3',
    level: 'info' as LogLevel,
    source: 'Architect Agent',
    message: 'Updated API specification with rate limiting details',
    timestamp: new Date(Date.now() - 1000 * 60 * 12),
  },
  {
    id: '4',
    level: 'warn' as LogLevel,
    source: 'Backend Agent',
    message: 'Database connection pool approaching limit (85%)',
    timestamp: new Date(Date.now() - 1000 * 60 * 18),
  },
  {
    id: '5',
    level: 'info' as LogLevel,
    source: 'CEO Agent',
    message: 'Phase transition: Architecture → Implementation',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    id: '6',
    level: 'success' as LogLevel,
    source: 'System',
    message: 'All microservices health checks passed',
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.25, 0.25, 0, 1] as const },
  },
};

export default function ProjectDetailPage() {
  const [isWorkflowRunning, setIsWorkflowRunning] = useState(true);
  // Project ID available via useParams().id when needed

  const getPhaseStatus = (phaseId: string) => {
    const phaseIndex = projectPhases.findIndex((p) => p.id === phaseId);
    const currentIndex = projectPhases.findIndex((p) => p.id === mockProject.currentPhase);
    
    if (phaseIndex < currentIndex) return 'completed';
    if (phaseIndex === currentIndex) return 'running';
    return 'pending';
  };

  const getPhaseIconColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-state-success bg-state-success-dim border-state-success/30';
      case 'running':
        return 'text-state-running bg-state-running-dim border-state-running/30 animate-pulse';
      default:
        return 'text-text-tertiary bg-bg-panel border-border-subtle';
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Link href="/projects">
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-text-secondary">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-text-primary">{mockProject.name}</h1>
            <Badge
              variant="outline"
              className="bg-state-success-dim text-state-success border-state-success/30"
            >
              Active
            </Badge>
          </div>
          <p className="text-text-secondary pl-10">{mockProject.description}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="border-border-default text-text-secondary"
            onClick={() => setIsWorkflowRunning(!isWorkflowRunning)}
          >
            {isWorkflowRunning ? (
              <>
                <Pause className="mr-2 h-4 w-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Resume
              </>
            )}
          </Button>
          <Button variant="outline" size="sm" className="border-border-default text-text-secondary">
            <RotateCcw className="mr-2 h-4 w-4" />
            Restart
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-text-secondary">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </motion.div>

      {/* Progress Overview */}
      <motion.div variants={itemVariants}>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h2 className="text-lg font-semibold text-text-primary">Project Progress</h2>
                  <span className="text-2xl font-bold text-state-running font-mono">
                    {mockProject.progress}%
                  </span>
                </div>
                <p className="text-sm text-text-secondary">
                  Current Phase: <span className="text-state-running font-medium capitalize">{mockProject.currentPhase}</span>
                  <span className="mx-2">•</span>
                  <span className="text-text-tertiary">
                    Est. completion: {new Date(mockProject.estimatedCompletion).toLocaleDateString()}
                  </span>
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-text-secondary">
                <Clock className="h-4 w-4" />
                <span>Started {new Date(mockProject.createdAt).toLocaleDateString()}</span>
              </div>
            </div>
            <Progress value={mockProject.progress} className="h-3 bg-bg-base" />
          </CardContent>
        </Card>
      </motion.div>

      {/* Phase Pipeline */}
      <motion.div variants={itemVariants}>
        <Card className="border-border-default bg-bg-panel">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">Development Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              {projectPhases.map((phase, index) => {
                const status = getPhaseStatus(phase.id);
                const Icon = phase.icon;
                const isLast = index === projectPhases.length - 1;

                return (
                  <div key={phase.id} className="flex items-center flex-1">
                    <div className="flex flex-col items-center">
                      <div
                        className={`flex h-12 w-12 items-center justify-center rounded-xl border-2 transition-all ${getPhaseIconColor(
                          status
                        )}`}
                      >
                        <Icon className="h-5 w-5" />
                      </div>
                      <span
                        className={`mt-2 text-xs font-medium ${
                          status === 'running'
                            ? 'text-state-running'
                            : status === 'completed'
                            ? 'text-state-success'
                            : 'text-text-tertiary'
                        }`}
                      >
                        {phase.name}
                      </span>
                    </div>
                    {!isLast && (
                      <div
                        className={`flex-1 h-0.5 mx-2 ${
                          status === 'completed' ? 'bg-state-success' : 'bg-border-default'
                        }`}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tabs Content */}
      <motion.div variants={itemVariants}>
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-bg-panel border border-border-default">
            <TabsTrigger value="overview" className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running">
              Overview
            </TabsTrigger>
            <TabsTrigger value="workflow" className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running">
              Workflow
            </TabsTrigger>
            <TabsTrigger value="agents" className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running">
              Agents
            </TabsTrigger>
            <TabsTrigger value="logs" className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running">
              Logs
            </TabsTrigger>
            <TabsTrigger value="deployment" className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running">
              Deployment
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-3">
              <Card className="lg:col-span-2 border-border-default bg-bg-panel">
                <CardHeader>
                  <CardTitle className="text-lg text-text-primary">Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <ExecutionTimeline phases={timelinePhases} compact />
                </CardContent>
              </Card>

              <Card className="border-border-default bg-bg-panel">
                <CardHeader>
                  <CardTitle className="text-lg text-text-primary">Active Agents</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {projectAgents
                      .filter((a) => a.status === 'running')
                      .map((agent) => (
                        <div
                          key={agent.agentId}
                          className="flex items-center gap-3 p-3 rounded-lg bg-bg-elevated border border-border-subtle"
                        >
                          <div className="w-2 h-2 rounded-full bg-state-running animate-pulse" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-text-primary truncate">
                              {agent.name}
                            </p>
                            <p className="text-xs text-text-secondary truncate">
                              {agent.currentTask}
                            </p>
                          </div>
                          <span className="text-xs font-mono text-state-running">
                            {agent.progress}%
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Workflow Tab */}
          <TabsContent value="workflow">
            <Card className="border-border-default bg-bg-panel">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg text-text-primary">Workflow Execution</CardTitle>
                  <p className="text-sm text-text-secondary">Real-time execution timeline</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-2 text-sm text-text-secondary">
                    <Loader2 className="h-4 w-4 animate-spin text-state-running" />
                    <span>Running</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <ExecutionTimeline phases={timelinePhases} />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Agents Tab */}
          <TabsContent value="agents">
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">AI Agent Team</CardTitle>
                <p className="text-sm text-text-secondary">
                  Specialized AI agents working on this project
                </p>
              </CardHeader>
              <CardContent>
                <AgentGrid columns={3}>
                  {projectAgents.map((agent) => (
                    <AgentCard
                      key={agent.agentId}
                      agentId={agent.agentId}
                      name={agent.name}
                      role={agent.role}
                      status={agent.status}
                      currentTask={agent.currentTask}
                      progress={agent.progress}
                      metrics={agent.metrics}
                    />
                  ))}
                </AgentGrid>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs">
            <Card className="border-border-default bg-bg-panel">
              <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-3">
                  <Terminal className="h-5 w-5 text-text-secondary" />
                  <div>
                    <CardTitle className="text-lg text-text-primary">System Logs</CardTitle>
                    <p className="text-sm text-text-secondary">Real-time activity stream</p>
                  </div>
                </div>
                <Badge variant="outline" className="bg-state-running-dim text-state-running">
                  <span className="w-2 h-2 rounded-full bg-state-running animate-pulse mr-1" />
                  Live
                </Badge>
              </CardHeader>
              <CardContent>
                <MiniLogViewer logs={projectLogs} limit={20} />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Deployment Tab */}
          <TabsContent value="deployment">
            <div className="grid gap-6 lg:grid-cols-2">
              <DeploymentStatusCard
                environment="staging"
                status="running"
                version="v1.2.3"
                commitHash="abc1234"
                deployedAt={new Date('2024-01-18T14:30:00')}
                buildDuration="8m 30s"
                healthChecks={[
                  { name: 'API', status: 'passing', lastCheck: new Date(), responseTime: 45 },
                  { name: 'Database', status: 'passing', lastCheck: new Date(), responseTime: 12 },
                ]}
                metrics={{ cpu: 42.5, memory: 68.2, requests: 1250, latency: 45 }}
              />
              <DeploymentStatusCard
                environment="production"
                status="building"
                version="v1.3.0"
                commitHash="def5678"
                buildDuration="In progress"
                healthChecks={[]}
              />
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </motion.div>
  );
}
