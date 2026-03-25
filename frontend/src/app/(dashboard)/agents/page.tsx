'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bot,
  Users,
  Activity,
  TrendingUp,
  Target,
  Search,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AgentCard, AgentGrid, type AgentStatus, type AgentRole } from '@/components/system/agent-card';
import { MetricPanel, type MetricData } from '@/components/system/metric-panel';
import { AgentCreator } from '@/components/agents/AgentCreator';
import { CrewCreator } from '@/components/agents/CrewCreator';
import { useCustomAgents, useCustomCrews, useDeleteAgent, useDeleteCrew } from '@/lib/hooks';
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

// Mock agent data
const agents = [
  {
    agentId: 'agent-001',
    name: 'CEO Agent',
    role: 'orchestrator' as AgentRole,
    status: 'success' as AgentStatus,
    currentTask: 'Project oversight and coordination',
    progress: 100,
    metrics: {
      tasksCompleted: 156,
      avgExecutionTime: '4m 30s',
      successRate: 98.5,
      totalTokens: 2450000,
      activeDuration: '48h 12m',
    },
    crew: 'Leadership',
  },
  {
    agentId: 'agent-002',
    name: 'Product Manager',
    role: 'orchestrator' as AgentRole,
    status: 'running' as AgentStatus,
    currentTask: 'Defining user stories for v2.0',
    progress: 78,
    metrics: {
      tasksCompleted: 89,
      avgExecutionTime: '6m 15s',
      successRate: 96.2,
      totalTokens: 1890000,
      activeDuration: '36h 45m',
    },
    crew: 'Leadership',
  },
  {
    agentId: 'agent-003',
    name: 'System Architect',
    role: 'orchestrator' as AgentRole,
    status: 'success' as AgentStatus,
    currentTask: 'Reviewing microservices design',
    progress: 100,
    metrics: {
      tasksCompleted: 67,
      avgExecutionTime: '15m 20s',
      successRate: 99.1,
      totalTokens: 3200000,
      activeDuration: '52h 30m',
    },
    crew: 'Architecture',
  },
  {
    agentId: 'agent-004',
    name: 'Backend Engineer',
    role: 'executor' as AgentRole,
    status: 'running' as AgentStatus,
    currentTask: 'Implementing GraphQL resolvers',
    progress: 65,
    metrics: {
      tasksCompleted: 234,
      avgExecutionTime: '8m 45s',
      successRate: 94.8,
      totalTokens: 4120000,
      activeDuration: '72h 15m',
    },
    crew: 'Engineering',
  },
  {
    agentId: 'agent-005',
    name: 'Frontend Engineer',
    role: 'executor' as AgentRole,
    status: 'running' as AgentStatus,
    currentTask: 'Building dashboard components',
    progress: 82,
    metrics: {
      tasksCompleted: 198,
      avgExecutionTime: '7m 30s',
      successRate: 95.5,
      totalTokens: 3650000,
      activeDuration: '68h 20m',
    },
    crew: 'Engineering',
  },
  {
    agentId: 'agent-006',
    name: 'Database Engineer',
    role: 'executor' as AgentRole,
    status: 'idle' as AgentStatus,
    currentTask: undefined,
    progress: 0,
    metrics: {
      tasksCompleted: 145,
      avgExecutionTime: '10m 15s',
      successRate: 97.3,
      totalTokens: 2100000,
      activeDuration: '45h 30m',
    },
    crew: 'Engineering',
  },
  {
    agentId: 'agent-007',
    name: 'QA Engineer',
    role: 'validator' as AgentRole,
    status: 'queued' as AgentStatus,
    currentTask: 'Waiting for build completion',
    progress: 15,
    metrics: {
      tasksCompleted: 312,
      avgExecutionTime: '5m 20s',
      successRate: 98.9,
      totalTokens: 1580000,
      activeDuration: '38h 45m',
    },
    crew: 'Quality Assurance',
  },
  {
    agentId: 'agent-008',
    name: 'Security Auditor',
    role: 'validator' as AgentRole,
    status: 'idle' as AgentStatus,
    currentTask: undefined,
    progress: 0,
    metrics: {
      tasksCompleted: 89,
      avgExecutionTime: '12m 40s',
      successRate: 99.5,
      totalTokens: 980000,
      activeDuration: '28h 15m',
    },
    crew: 'Quality Assurance',
  },
  {
    agentId: 'agent-009',
    name: 'DevOps Engineer',
    role: 'deployer' as AgentRole,
    status: 'running' as AgentStatus,
    currentTask: 'Configuring Kubernetes cluster',
    progress: 45,
    metrics: {
      tasksCompleted: 178,
      avgExecutionTime: '14m 30s',
      successRate: 96.8,
      totalTokens: 1950000,
      activeDuration: '42h 30m',
    },
    crew: 'Infrastructure',
  },
  {
    agentId: 'agent-010',
    name: 'UX Designer',
    role: 'executor' as AgentRole,
    status: 'error' as AgentStatus,
    currentTask: 'Design system token generation failed',
    progress: 30,
    metrics: {
      tasksCompleted: 67,
      avgExecutionTime: '18m 20s',
      successRate: 88.5,
      totalTokens: 1250000,
      activeDuration: '32h 10m',
    },
    crew: 'Design',
  },
];

// Agent crews
const crews = [
  { name: 'Leadership', count: 2, color: '#8b5cf6' },
  { name: 'Architecture', count: 1, color: '#3b82f6' },
  { name: 'Engineering', count: 3, color: '#10b981' },
  { name: 'Quality Assurance', count: 2, color: '#f59e0b' },
  { name: 'Infrastructure', count: 1, color: '#ef4444' },
  { name: 'Design', count: 1, color: '#ec4899' },
];

// Performance data for charts
const performanceData = [
  { time: '00:00', tasks: 12, tokens: 45000 },
  { time: '04:00', tasks: 8, tokens: 32000 },
  { time: '08:00', tasks: 25, tokens: 98000 },
  { time: '12:00', tasks: 32, tokens: 125000 },
  { time: '16:00', tasks: 28, tokens: 110000 },
  { time: '20:00', tasks: 18, tokens: 72000 },
  { time: '23:59', tasks: 15, tokens: 58000 },
];

const successRateData = [
  { name: 'Orchestrator', rate: 97.8, tasks: 312 },
  { name: 'Executor', rate: 94.5, tasks: 645 },
  { name: 'Validator', rate: 98.9, tasks: 401 },
  { name: 'Deployer', rate: 96.2, tasks: 178 },
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

export default function AgentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCrew, setSelectedCrew] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<AgentStatus | null>(null);

  // Fetch custom agents and crews from backend
  const { data: customAgents = [] } = useCustomAgents();
  const { data: customCrews = [] } = useCustomCrews();
  const deleteAgent = useDeleteAgent();
  const deleteCrew = useDeleteCrew();

  const filteredAgents = agents.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.agentId.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCrew = !selectedCrew || agent.crew === selectedCrew;
    const matchesStatus = !selectedStatus || agent.status === selectedStatus;
    return matchesSearch && matchesCrew && matchesStatus;
  });

  const statusCounts = agents.reduce((acc, agent) => {
    acc[agent.status] = (acc[agent.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const metrics: MetricData[] = [
    {
      id: 'total-agents',
      label: 'Total Agents',
      value: agents.length,
      icon: Bot,
      delta: { value: 12.5, direction: 'up' },
    },
    {
      id: 'active-agents',
      label: 'Active Now',
      value: statusCounts.running || 0,
      icon: Activity,
      delta: { value: 25, direction: 'up' },
    },
    {
      id: 'tasks-completed',
      label: 'Tasks Completed',
      value: agents.reduce((sum, a) => sum + a.metrics.tasksCompleted, 0),
      icon: Target,
      delta: { value: 18.2, direction: 'up' },
    },
    {
      id: 'avg-success',
      label: 'Avg Success Rate',
      value: `${(agents.reduce((sum, a) => sum + a.metrics.successRate, 0) / agents.length).toFixed(1)}%`,
      icon: TrendingUp,
      delta: { value: 2.1, direction: 'up' },
    },
  ];

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
          <h1 className="text-3xl font-bold text-text-primary">AI Agent Crews</h1>
          <p className="mt-1 text-text-secondary">
            Manage and monitor your AI engineering workforce
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="border-border-default text-text-secondary">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <AgentCreator />
          <CrewCreator />
        </div>
      </motion.div>

      {/* Metrics */}
      <motion.div variants={itemVariants}>
        <MetricPanel metrics={metrics} variant="compact" />
      </motion.div>

      {/* Charts Row */}
      <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-3">
        {/* Performance Chart */}
        <Card className="lg:col-span-2 border-border-default bg-bg-panel">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">Agent Activity (24h)</CardTitle>
            <CardDescription className="text-text-secondary">
              Tasks completed and token consumption over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={performanceData}>
                  <defs>
                    <linearGradient id="colorTasks" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--state-running)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="var(--state-running)" stopOpacity={0} />
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
                    labelStyle={{ color: 'var(--text-primary)' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="tasks"
                    stroke="var(--state-running)"
                    strokeWidth={2}
                    fill="url(#colorTasks)"
                    name="Tasks"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Success Rate by Role */}
        <Card className="border-border-default bg-bg-panel">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">Success by Role</CardTitle>
            <CardDescription className="text-text-secondary">
              Performance across agent types
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={successRateData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" horizontal={false} />
                  <XAxis type="number" domain={[85, 100]} stroke="var(--text-tertiary)" fontSize={12} />
                  <YAxis dataKey="name" type="category" stroke="var(--text-tertiary)" fontSize={11} width={80} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--bg-elevated)',
                      border: '1px solid var(--border-default)',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="rate" fill="var(--state-success)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Crews Overview */}
      <motion.div variants={itemVariants}>
        <Card className="border-border-default bg-bg-panel">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">Agent Crews</CardTitle>
            <CardDescription className="text-text-secondary">
              Teams organized by function and expertise
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {crews.map((crew) => (
                <button
                  key={crew.name}
                  onClick={() => setSelectedCrew(selectedCrew === crew.name ? null : crew.name)}
                  className={`p-4 rounded-xl border transition-all text-left ${
                    selectedCrew === crew.name
                      ? 'border-state-running bg-state-running-dim'
                      : 'border-border-default bg-bg-elevated hover:border-emphasis'
                  }`}
                >
                  <div
                    className="w-3 h-3 rounded-full mb-2"
                    style={{ backgroundColor: crew.color }}
                  />
                  <p className="text-sm font-medium text-text-primary">{crew.name}</p>
                  <p className="text-xs text-text-secondary">{crew.count} agents</p>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Custom Agents & Crews */}
      {(customAgents.length > 0 || customCrews.length > 0) && (
        <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-2">
          {/* Custom Agents */}
          {customAgents.length > 0 && (
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary flex items-center gap-2">
                  <Bot className="h-5 w-5 text-state-queued" />
                  Custom Agents
                </CardTitle>
                <CardDescription className="text-text-secondary">
                  Dynamically created agents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {customAgents.map((agent) => (
                    <div
                      key={agent.agent_id}
                      className="flex items-center justify-between p-3 rounded-lg border border-border-default bg-bg-elevated"
                    >
                      <div>
                        <p className="font-medium text-text-primary">{agent.name}</p>
                        <p className="text-xs text-text-secondary">{agent.role} • {agent.llm_model}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteAgent.mutate(agent.agent_id)}
                        disabled={deleteAgent.isPending}
                        className="text-state-error hover:text-state-error hover:bg-state-error-dim"
                      >
                        Delete
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Custom Crews */}
          {customCrews.length > 0 && (
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary flex items-center gap-2">
                  <Users className="h-5 w-5 text-state-queued" />
                  Custom Crews
                </CardTitle>
                <CardDescription className="text-text-secondary">
                  Dynamically created crews
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {customCrews.map((crew) => (
                    <div
                      key={crew.crew_id}
                      className="flex items-center justify-between p-3 rounded-lg border border-border-default bg-bg-elevated"
                    >
                      <div>
                        <p className="font-medium text-text-primary">{crew.name}</p>
                        <p className="text-xs text-text-secondary">{crew.agent_count} agents</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteCrew.mutate(crew.crew_id)}
                        disabled={deleteCrew.isPending}
                        className="text-state-error hover:text-state-error hover:bg-state-error-dim"
                      >
                        Delete
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}

      {/* Agents Grid */}
      <motion.div variants={itemVariants}>
        <Card className="border-border-default bg-bg-panel">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg text-text-primary">All Agents</CardTitle>
              <CardDescription className="text-text-secondary">
                {filteredAgents.length} agents matching filters
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
                <Input
                  placeholder="Search agents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 border-border-default bg-bg-input pl-10 text-text-primary"
                />
              </div>
              {/* Status Filter */}
              <div className="flex items-center gap-1">
                {(['running', 'success', 'idle', 'error', 'queued'] as AgentStatus[]).map((status) => (
                  <button
                    key={status}
                    onClick={() => setSelectedStatus(selectedStatus === status ? null : status)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      selectedStatus === status
                        ? 'bg-state-running-dim text-state-running'
                        : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                    <span className="ml-1.5 opacity-60">{statusCounts[status] || 0}</span>
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <AgentGrid columns={3}>
              {filteredAgents.map((agent) => (
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
      </motion.div>
    </motion.div>
  );
}
