'use client';

export const dynamic = 'force-dynamic';

import { Bot, FolderKanban, HeartPulse, Brain, Activity, CheckCircle2 } from 'lucide-react';
import { StatCard } from '@/components/cards/stat-card';
import { ActivityItem } from '@/components/cards/activity-item';
import { DashboardSkeleton } from '@/components/cards/skeletons';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles, Zap, ArrowRight, AlertCircle, Clock, Shield, Server } from 'lucide-react';
import { containerVariants, slideUpVariants } from '@/lib/variants';
import { motion } from 'framer-motion';

// Mock data
const systemStatus = {
  activeAgents: 4,
  runningProjects: 2,
  systemHealth: 'healthy',
  llmStatus: 'connected',
};

const agentActivities = [
  {
    id: '1',
    agent: 'Backend Engineer',
    action: 'building authentication API',
    status: 'running',
    timestamp: '2 min ago',
    icon: Bot,
  },
  {
    id: '2',
    agent: 'UX Designer',
    action: 'designing user flow',
    status: 'running',
    timestamp: '5 min ago',
    icon: Bot,
  },
  {
    id: '3',
    agent: 'QA Agent',
    action: 'running integration tests',
    status: 'running',
    timestamp: '12 min ago',
    icon: Bot,
  },
  {
    id: '4',
    agent: 'Product Manager',
    action: 'completed PRD review',
    status: 'completed',
    timestamp: '30 min ago',
    icon: CheckCircle2,
  },
  {
    id: '5',
    agent: 'DevOps Engineer',
    action: 'configured CI/CD pipeline',
    status: 'completed',
    timestamp: '1 hour ago',
    icon: CheckCircle2,
  },
];

const pipelineStages = [
  { name: 'Idea', status: 'completed', description: 'Product concept defined' },
  { name: 'Planning', status: 'completed', description: 'Requirements gathered' },
  { name: 'Design', status: 'in_progress', description: 'Architecture & UX in progress' },
  { name: 'Engineering', status: 'pending', description: 'Code generation pending' },
  { name: 'Testing', status: 'pending', description: 'QA & simulation pending' },
  { name: 'Deployment', status: 'pending', description: 'Production deployment pending' },
];

const simulations = [
  {
    id: '1',
    name: 'UX Simulation',
    status: 'approved',
    issues: 0,
    description: 'User flow and interface validation',
  },
  {
    id: '2',
    name: 'Architecture Simulation',
    status: 'needs_improvement',
    issues: 2,
    description: 'System design and scalability check',
  },
  {
    id: '3',
    name: 'API Simulation',
    status: 'pending',
    issues: 0,
    description: 'Endpoint testing and validation',
  },
  {
    id: '4',
    name: 'Infrastructure Simulation',
    status: 'pending',
    issues: 0,
    description: 'Deployment and scaling validation',
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
      <motion.div variants={slideUpVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Dashboard</h1>
          <p className="mt-1 text-slate-400">
            Welcome back! Here&apos;s what&apos;s happening with your AI Software Factory.
          </p>
        </div>
        <Button className="bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
          <Sparkles className="mr-2 h-4 w-4" />
          New Project
        </Button>
      </motion.div>

      {/* System Status Cards */}
      <motion.div variants={slideUpVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Active Agents"
          value={systemStatus.activeAgents}
          description="AI agents working now"
          icon={<Bot className="h-4 w-4 text-violet-400" />}
        />
        <StatCard
          title="Running Projects"
          value={systemStatus.runningProjects}
          description="Projects in progress"
          icon={<FolderKanban className="h-4 w-4 text-blue-400" />}
        />
        <StatCard
          title="System Health"
          value="Healthy"
          description="All systems operational"
          icon={
            <div className="relative flex h-4 w-4">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-4 w-4 rounded-full bg-emerald-400"></span>
            </div>
          }
        />
        <StatCard
          title="LLM Status"
          value="Connected"
          description="Ollama provider active"
          icon={<Brain className="h-4 w-4 text-indigo-400" />}
        />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Agent Activity Feed */}
        <motion.div variants={slideUpVariants} className="lg:col-span-2">
          <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg text-slate-100">Agent Activity</CardTitle>
                <p className="text-sm text-slate-400">
                  Real-time updates from your AI engineering team
                </p>
              </div>
              <Badge variant="secondary" className="bg-violet-500/10 text-violet-400">
                <Activity className="mr-1 h-3 w-3" />
                Live
              </Badge>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[320px] pr-4">
                <div className="space-y-4">
                  {agentActivities.map((activity) => (
                    <ActivityItem
                      key={activity.id}
                      icon={<activity.icon className="h-4 w-4" />}
                      title={activity.agent}
                      description={activity.action}
                      timestamp={activity.timestamp}
                      status={activity.status === 'running' ? 'running' : 'completed'}
                    />
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </motion.div>

        {/* Project Pipeline */}
        <motion.div variants={slideUpVariants}>
          <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-lg text-slate-100">Project Pipeline</CardTitle>
              <p className="text-sm text-slate-400">
                Current stage in the development lifecycle
              </p>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <div className="absolute left-3 top-0 bottom-0 w-px bg-slate-800"></div>
                <div className="space-y-4">
                  {pipelineStages.map((stage) => (
                    <div key={stage.name} className="relative flex gap-4">
                      <div
                        className={`relative z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 ${
                          stage.status === 'completed'
                            ? 'border-emerald-500 bg-emerald-500'
                            : stage.status === 'in_progress'
                              ? 'border-violet-500 bg-violet-500'
                              : 'border-slate-700 bg-slate-800'
                        }`}
                      >
                        {stage.status === 'completed' && (
                          <CheckCircle2 className="h-3.5 w-3.5 text-white" />
                        )}
                        {stage.status === 'in_progress' && (
                          <div className="h-2 w-2 rounded-full bg-white animate-pulse"></div>
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <p
                          className={`font-medium ${
                            stage.status === 'completed'
                              ? 'text-emerald-400'
                              : stage.status === 'in_progress'
                                ? 'text-violet-400'
                                : 'text-slate-500'
                          }`}
                        >
                          {stage.name}
                        </p>
                        <p className="text-xs text-slate-500">{stage.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Section: Simulations & Projects */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Simulation Results */}
        <motion.div variants={slideUpVariants}>
          <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg text-slate-100">Simulation Results</CardTitle>
                <p className="text-sm text-slate-400">
                  Automated testing and validation
                </p>
              </div>
              <Button variant="ghost" size="sm" className="text-violet-400 hover:text-violet-300">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-2">
                {simulations.map((sim) => (
                  <div
                    key={sim.id}
                    className="rounded-xl border border-slate-800 bg-slate-800/30 p-4 transition-all hover:border-slate-700 hover:bg-slate-800/50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="rounded-lg bg-slate-700/50 p-2">
                        {sim.status === 'approved' ? (
                          <Shield className="h-4 w-4 text-emerald-400" />
                        ) : sim.status === 'needs_improvement' ? (
                          <AlertCircle className="h-4 w-4 text-amber-400" />
                        ) : (
                          <Clock className="h-4 w-4 text-slate-400" />
                        )}
                      </div>
                      <Badge
                        variant="secondary"
                        className={
                          sim.status === 'approved'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : sim.status === 'needs_improvement'
                              ? 'bg-amber-500/10 text-amber-400'
                              : 'bg-slate-500/10 text-slate-400'
                        }
                      >
                        {sim.status === 'needs_improvement'
                          ? 'Needs Work'
                          : sim.status.charAt(0).toUpperCase() + sim.status.slice(1)}
                      </Badge>
                    </div>
                    <h4 className="mt-3 font-medium text-slate-200">{sim.name}</h4>
                    <p className="text-xs text-slate-500">{sim.description}</p>
                    {sim.issues > 0 && (
                      <p className="mt-2 text-xs text-amber-400">{sim.issues} issues found</p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Projects */}
        <motion.div variants={slideUpVariants}>
          <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg text-slate-100">Recent Projects</CardTitle>
                <p className="text-sm text-slate-400">
                  Your active software projects
                </p>
              </div>
              <Button variant="ghost" size="sm" className="text-violet-400 hover:text-violet-300">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentProjects.map((project) => (
                  <div
                    key={project.id}
                    className="rounded-xl border border-slate-800 bg-slate-800/30 p-4 transition-all hover:border-slate-700 hover:bg-slate-800/50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20">
                          <Zap className="h-5 w-5 text-violet-400" />
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-200">{project.name}</h4>
                          <div className="flex items-center gap-2 text-xs text-slate-500">
                            <span className="flex items-center gap-1">
                              <Server className="h-3 w-3" />
                              {project.stage}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <Bot className="h-3 w-3" />
                              {project.agents} agents
                            </span>
                          </div>
                        </div>
                      </div>
                      <Badge
                        variant="secondary"
                        className="bg-emerald-500/10 text-emerald-400"
                      >
                        Active
                      </Badge>
                    </div>
                    <div className="mt-4">
                      <div className="mb-2 flex items-center justify-between text-xs">
                        <span className="text-slate-500">Progress</span>
                        <span className="text-slate-300">{project.progress}%</span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-slate-800">
                        <div
                          className="h-2 rounded-full bg-violet-400 transition-all duration-300"
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
