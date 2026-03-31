'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Workflow,
  Play,
  Pause,
  RotateCcw,
  GitBranch,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Plus,
  Search,

  Terminal,
  Activity,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useWorkflows } from '@/lib/hooks/useWorkflows';
import { ExecutionTimeline, type TimelinePhase } from '@/components/system/execution-timeline';
import { MiniLogViewer } from '@/components/system/log-stream';
import type { LogEntry, LogLevel } from '@/components/system/log-stream';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

// Workflow data will be fetched from database

// Mock timeline phases for active workflow
const activeWorkflowPhases: TimelinePhase[] = [
  {
    id: '1',
    name: 'Idea Validation',
    status: 'completed',
    startTime: new Date('2024-01-15T09:00:00'),
    endTime: new Date('2024-01-15T11:30:00'),
    duration: '2h 30m',
    steps: [
      { name: 'Market research', status: 'completed', timestamp: new Date('2024-01-15T10:00:00') },
      { name: 'Feasibility study', status: 'completed', timestamp: new Date('2024-01-15T11:30:00') },
    ],
  },
  {
    id: '2',
    name: 'Requirements',
    status: 'completed',
    startTime: new Date('2024-01-15T12:00:00'),
    endTime: new Date('2024-01-15T16:00:00'),
    duration: '4h 0m',
    steps: [
      { name: 'User stories', status: 'completed', timestamp: new Date('2024-01-15T13:00:00') },
      { name: 'API specs', status: 'completed', timestamp: new Date('2024-01-15T16:00:00') },
    ],
  },
  {
    id: '3',
    name: 'Architecture',
    status: 'completed',
    startTime: new Date('2024-01-16T09:00:00'),
    endTime: new Date('2024-01-16T15:00:00'),
    duration: '6h 0m',
    steps: [
      { name: 'System design', status: 'completed', timestamp: new Date('2024-01-16T11:00:00') },
      { name: 'Database schema', status: 'completed', timestamp: new Date('2024-01-16T15:00:00') },
    ],
  },
  {
    id: '4',
    name: 'Implementation',
    status: 'running',
    startTime: new Date('2024-01-17T09:00:00'),
    duration: 'In progress',
    steps: [
      { name: 'Frontend setup', status: 'completed', timestamp: new Date('2024-01-17T12:00:00') },
      { name: 'Backend API', status: 'running', timestamp: new Date('2024-01-17T14:00:00') },
      { name: 'Authentication', status: 'pending', timestamp: new Date('2024-01-18T09:00:00') },
      { name: 'Database layer', status: 'pending', timestamp: new Date('2024-01-18T16:00:00') },
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

// Mock logs
const workflowLogs: LogEntry[] = [
  {
    id: '1',
    level: 'info' as LogLevel,
    source: 'Orchestrator',
    message: 'Workflow execution started for project SaaS Analytics Dashboard',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48),
  },
  {
    id: '2',
    level: 'success' as LogLevel,
    source: 'CEO Agent',
    message: 'Idea validation phase completed successfully',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 46),
  },
  {
    id: '3',
    level: 'info' as LogLevel,
    source: 'Product Manager',
    message: 'Generated 24 user stories from requirements',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 42),
  },
  {
    id: '4',
    level: 'success' as LogLevel,
    source: 'Architect',
    message: 'System architecture approved with microservices pattern',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 36),
  },
  {
    id: '5',
    level: 'info' as LogLevel,
    source: 'Frontend Engineer',
    message: 'Initialized Next.js project with TypeScript',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
  },
  {
    id: '6',
    level: 'warn' as LogLevel,
    source: 'Backend Engineer',
    message: 'Database connection pool size increased to 20',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 12),
  },
  {
    id: '7',
    level: 'info' as LogLevel,
    source: 'Backend Engineer',
    message: 'Generated 15 GraphQL resolvers',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
];

// Performance data
const executionTimeData = [
  { phase: 'Idea', planned: 4, actual: 2.5 },
  { phase: 'Requirements', planned: 6, actual: 4 },
  { phase: 'Architecture', planned: 8, actual: 6 },
  { phase: 'Implementation', planned: 24, actual: 18 },
  { phase: 'Testing', planned: 12, actual: 0 },
  { phase: 'Deployment', planned: 4, actual: 0 },
];

const throughputData = [
  { time: '00:00', workflows: 2 },
  { time: '04:00', workflows: 1 },
  { time: '08:00', workflows: 4 },
  { time: '12:00', workflows: 6 },
  { time: '16:00', workflows: 5 },
  { time: '20:00', workflows: 3 },
  { time: '23:59', workflows: 2 },
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

const getStatusColor = (status: string) => {
  switch (status) {
    case 'running':
      return 'bg-state-running-dim text-state-running border-state-running/30';
    case 'completed':
      return 'bg-state-success-dim text-state-success border-state-success/30';
    case 'failed':
      return 'bg-state-error-dim text-state-error border-state-error/30';
    case 'queued':
      return 'bg-state-queued-dim text-state-queued border-state-queued/30';
    default:
      return 'bg-bg-elevated text-text-secondary border-border-default';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'running':
      return <Loader2 className="h-4 w-4 animate-spin" />;
    case 'completed':
      return <CheckCircle2 className="h-4 w-4" />;
    case 'failed':
      return <AlertCircle className="h-4 w-4" />;
    case 'queued':
      return <Clock className="h-4 w-4" />;
    default:
      return null;
  }
};

export default function WorkflowsPage() {
  // Fetch real workflows from database
  const { data: workflows, isLoading, error } = useWorkflows();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  const filteredWorkflows = (workflows || []).filter((workflow: any) => {
    const matchesSearch =
      workflow.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      workflow.project_id?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || workflow.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const activeWorkflow = workflows?.find((w: { workflow_id: string }) => w.workflow_id === selectedWorkflow);

  const statusCounts = (workflows || []).reduce((acc: any, wf: any) => {
    const status = wf.status || 'pending';
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Workflows</h1>
          <p className="text-text-secondary">
            {isLoading ? 'Loading workflows...' : `${workflows?.length || 0} workflows in database`}
          </p>
        </div>
        <Button variant="ai-action">
          <Plus className="mr-2 h-4 w-4" />
          New Workflow
        </Button>
      </motion.div>

      {/* Stats Cards */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        {[
          { label: 'Active', value: statusCounts.running || 0, color: 'text-state-running', icon: Activity },
          { label: 'Completed', value: statusCounts.completed || 0, color: 'text-state-success', icon: CheckCircle2 },
          { label: 'Failed', value: statusCounts.failed || 0, color: 'text-state-error', icon: AlertCircle },
          { label: 'Queued', value: statusCounts.queued || 0, color: 'text-state-queued', icon: Clock },
        ].map((stat) => (
          <Card key={stat.label} className="border-border-default bg-bg-panel">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-secondary">{stat.label}</p>
                  <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                </div>
                <stat.icon className={`h-8 w-8 ${stat.color} opacity-50`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Main Content */}
      <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-3">
        {/* Workflows List */}
        <Card className="lg:col-span-1 border-border-default bg-bg-panel">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg text-text-primary">All Workflows</CardTitle>
              <Badge variant="outline" className="text-text-secondary">
                {filteredWorkflows.length}
              </Badge>
            </div>
            <div className="space-y-2 pt-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
                <Input
                  placeholder="Search workflows..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="border-border-default bg-bg-input pl-10 text-text-primary"
                />
              </div>
              <div className="flex flex-wrap gap-1">
                {['running', 'completed', 'failed', 'queued'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(statusFilter === status ? null : status)}
                    className={`px-2 py-1 rounded-md text-xs font-medium transition-all ${
                      statusFilter === status
                        ? 'bg-state-running-dim text-state-running'
                        : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <span className="ml-2 text-text-secondary">Loading workflows...</span>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center py-12">
                <p className="text-error">Error loading workflows</p>
              </div>
            ) : filteredWorkflows.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Workflow className="w-12 h-12 text-text-tertiary mb-2" />
                <p className="text-text-secondary">No workflows found</p>
              </div>
            ) : (
              filteredWorkflows.map((workflow) => (
                <button
                  key={workflow.workflow_id}
                  onClick={() => setSelectedWorkflow(workflow.workflow_id)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${
                    selectedWorkflow === workflow.workflow_id
                      ? 'border-state-running bg-state-running-dim'
                      : 'border-border-subtle bg-bg-elevated hover:border-emphasis'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Workflow className="h-4 w-4 text-text-secondary" />
                      <span className="font-medium text-text-primary text-sm">
                        {workflow.name ?? workflow.workflow_id}
                      </span>
                    </div>
                    <Badge variant="outline" className={`text-xs ${getStatusColor(workflow.status)}`}>
                      {getStatusIcon(workflow.status)}
                    </Badge>
                  </div>
                <p className="text-xs text-text-secondary mb-2 line-clamp-1">{workflow.description || 'No description'}</p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-tertiary">{workflow.project_id || 'Unknown'}</span>
                  <span className="font-mono text-text-code">{workflow.status}</span>
                </div>
                <Progress value={50} className="h-1 mt-2 bg-bg-base" />
              </button>
              ))
            )}
          </CardContent>
        </Card>

        {/* Workflow Detail */}
        <div className="lg:col-span-2 space-y-6">
          {activeWorkflow && (
            <>
              {/* Workflow Header */}
              <Card className="border-border-default bg-bg-panel">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-xl font-bold text-text-primary">
                          {activeWorkflow.name ?? activeWorkflow.workflow_id}
                        </h2>
                        <Badge variant="outline" className={getStatusColor(activeWorkflow.status)}>
                          {getStatusIcon(activeWorkflow.status)}
                          <span className="ml-1 capitalize">{activeWorkflow.status}</span>
                        </Badge>
                      </div>
                      <p className="text-text-secondary">{activeWorkflow.description || 'No description available'}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {activeWorkflow.status === 'running' ? (
                        <Button variant="outline" size="sm" className="border-border-default">
                          <Pause className="mr-2 h-4 w-4" />
                          Pause
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm" className="border-border-default">
                          <Play className="mr-2 h-4 w-4" />
                          Resume
                        </Button>
                      )}
                      <Button variant="outline" size="sm" className="border-border-default">
                        <RotateCcw className="mr-2 h-4 w-4" />
                        Restart
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-6 text-sm">
                      <div>
                        <span className="text-text-tertiary">Project</span>
                        <p className="font-medium text-text-primary">{activeWorkflow.project_id || 'Unknown'}</p>
                      </div>
                      <div>
                        <span className="text-text-tertiary">Started</span>
                        <p className="font-medium text-text-primary">
                          {activeWorkflow.started_at ? new Date(activeWorkflow.started_at).toLocaleDateString() : 'Not started'}
                        </p>
                      </div>
                      <div>
                        <span className="text-text-tertiary">Status</span>
                        <p className="font-medium text-state-running">{activeWorkflow.status}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-bold text-text-primary font-mono">
                        {activeWorkflow.status}
                      </span>
                    </div>
                  </div>
                  <Progress value={50} className="h-2 bg-bg-base" />
                </CardContent>
              </Card>

              {/* Timeline & Logs Tabs */}
              <Tabs defaultValue="timeline" className="space-y-4">
                <TabsList className="bg-bg-panel border border-border-default">
                  <TabsTrigger
                    value="timeline"
                    className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running"
                  >
                    <GitBranch className="mr-2 h-4 w-4" />
                    Timeline
                  </TabsTrigger>
                  <TabsTrigger
                    value="logs"
                    className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running"
                  >
                    <Terminal className="mr-2 h-4 w-4" />
                    Logs
                  </TabsTrigger>
                  <TabsTrigger
                    value="metrics"
                    className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running"
                  >
                    <Activity className="mr-2 h-4 w-4" />
                    Metrics
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="timeline">
                  <Card className="border-border-default bg-bg-panel">
                    <CardHeader>
                      <CardTitle className="text-lg text-text-primary">Execution Timeline</CardTitle>
                      <CardDescription className="text-text-secondary">
                        Real-time progress through development phases
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ExecutionTimeline phases={activeWorkflowPhases} />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="logs">
                  <Card className="border-border-default bg-bg-panel">
                    <CardHeader className="flex flex-row items-center justify-between">
                      <div>
                        <CardTitle className="text-lg text-text-primary">Execution Logs</CardTitle>
                        <CardDescription className="text-text-secondary">
                          Real-time activity from all agents
                        </CardDescription>
                      </div>
                      <Badge variant="outline" className="bg-state-running-dim text-state-running">
                        <span className="w-2 h-2 rounded-full bg-state-running animate-pulse mr-1" />
                        Live
                      </Badge>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[400px] bg-bg-code rounded-lg border border-border-subtle p-4 overflow-auto font-system text-sm">
                        <MiniLogViewer logs={workflowLogs} limit={50} />
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="metrics">
                  <div className="grid gap-4 md:grid-cols-2">
                    <Card className="border-border-default bg-bg-panel">
                      <CardHeader>
                        <CardTitle className="text-lg text-text-primary">Phase Timing</CardTitle>
                        <CardDescription className="text-text-secondary">
                          Planned vs actual execution time
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="h-[250px]">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={executionTimeData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                              <XAxis dataKey="phase" stroke="var(--text-tertiary)" fontSize={11} />
                              <YAxis stroke="var(--text-tertiary)" fontSize={12} />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: 'var(--bg-elevated)',
                                  border: '1px solid var(--border-default)',
                                  borderRadius: '8px',
                                }}
                              />
                              <Bar dataKey="planned" fill="var(--state-idle)" name="Planned (h)" radius={[4, 4, 0, 0]} />
                              <Bar dataKey="actual" fill="var(--state-running)" name="Actual (h)" radius={[4, 4, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="border-border-default bg-bg-panel">
                      <CardHeader>
                        <CardTitle className="text-lg text-text-primary">Throughput</CardTitle>
                        <CardDescription className="text-text-secondary">
                          Workflow executions over time
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="h-[250px]">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={throughputData}>
                              <defs>
                                <linearGradient id="colorWorkflows" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="0%" stopColor="var(--state-success)" stopOpacity={0.3} />
                                  <stop offset="100%" stopColor="var(--state-success)" stopOpacity={0} />
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                              <XAxis dataKey="time" stroke="var(--text-tertiary)" fontSize={12} />
                              <YAxis stroke="var(--text-tertiary)" fontSize={12} />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: 'var(--bg-elevated)',
                                  border: '1px solid var(--border-default)',
                                  borderRadius: '8px',
                                }}
                              />
                              <Area
                                type="monotone"
                                dataKey="workflows"
                                stroke="var(--state-success)"
                                strokeWidth={2}
                                fill="url(#colorWorkflows)"
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
