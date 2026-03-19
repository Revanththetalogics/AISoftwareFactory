'use client';

// Prevent static generation - this page requires authentication
export const dynamic = 'force-dynamic';

import { motion } from 'framer-motion';
import {
  Bot,
  Code2,
  Palette,
  Shield,
  Server,
  Activity,
  Clock,
  AlertCircle,
  Pause,
  Play,
  RefreshCw,
  Zap,
  Terminal,
  Layout,
  Database,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useState, useEffect } from 'react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.25, 0, 1] as const,
    },
  },
};

interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  status: 'running' | 'idle' | 'paused' | 'error';
  currentTask: string;
  progress: number;
  executionTime: string;
  icon: React.ElementType;
  color: string;
  logs: string[];
}

const agents: Agent[] = [
  {
    id: '1',
    name: 'CEO Agent',
    role: 'Chief Executive Officer',
    description: 'Strategic oversight and decision making',
    status: 'running',
    currentTask: 'Reviewing project roadmap',
    progress: 78,
    executionTime: '2h 15m',
    icon: Shield,
    color: 'from-amber-500 to-orange-600',
    logs: ['Analyzing market requirements', 'Setting project priorities', 'Allocating resources'],
  },
  {
    id: '2',
    name: 'Product Manager',
    role: 'Product Manager',
    description: 'Requirements gathering and feature planning',
    status: 'running',
    currentTask: 'Writing user stories',
    progress: 65,
    executionTime: '1h 45m',
    icon: Layout,
    color: 'from-blue-500 to-cyan-600',
    logs: ['Interviewing stakeholders', 'Defining user personas', 'Creating product backlog'],
  },
  {
    id: '3',
    name: 'Backend Engineer',
    role: 'Senior Backend Engineer',
    description: 'API development and database design',
    status: 'running',
    currentTask: 'Building authentication API',
    progress: 82,
    executionTime: '3h 20m',
    icon: Code2,
    color: 'from-violet-500 to-purple-600',
    logs: ['Designing database schema', 'Implementing JWT auth', 'Writing API tests'],
  },
  {
    id: '4',
    name: 'Frontend Engineer',
    role: 'Senior Frontend Engineer',
    description: 'UI/UX implementation and component development',
    status: 'idle',
    currentTask: 'Waiting for API specs',
    progress: 0,
    executionTime: '0m',
    icon: Palette,
    color: 'from-pink-500 to-rose-600',
    logs: ['Reviewing design mockups', 'Setting up component library', 'Configuring Tailwind'],
  },
  {
    id: '5',
    name: 'UX Designer',
    role: 'UX/UI Designer',
    description: 'User experience and interface design',
    status: 'running',
    currentTask: 'Creating wireframes',
    progress: 45,
    executionTime: '1h 30m',
    icon: Layout,
    color: 'from-emerald-500 to-teal-600',
    logs: ['Researching user needs', 'Sketching layouts', 'Defining color palette'],
  },
  {
    id: '6',
    name: 'DevOps Engineer',
    role: 'DevOps Engineer',
    description: 'Infrastructure and deployment automation',
    status: 'idle',
    currentTask: 'Monitoring CI/CD pipeline',
    progress: 100,
    executionTime: '45m',
    icon: Server,
    color: 'from-indigo-500 to-blue-600',
    logs: ['Setting up Docker containers', 'Configuring GitHub Actions', 'Deploying to staging'],
  },
  {
    id: '7',
    name: 'QA Engineer',
    role: 'Quality Assurance Engineer',
    description: 'Testing and quality verification',
    status: 'paused',
    currentTask: 'Waiting for code completion',
    progress: 30,
    executionTime: '1h 10m',
    icon: Shield,
    color: 'from-red-500 to-rose-600',
    logs: ['Writing test cases', 'Setting up test environment', 'Planning test strategy'],
  },
  {
    id: '8',
    name: 'Database Architect',
    role: 'Database Architect',
    description: 'Database design and optimization',
    status: 'running',
    currentTask: 'Optimizing query performance',
    progress: 60,
    executionTime: '2h 5m',
    icon: Database,
    color: 'from-cyan-500 to-blue-600',
    logs: ['Designing entity relationships', 'Creating migration scripts', 'Indexing tables'],
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'running':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'idle':
      return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    case 'paused':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'error':
      return 'bg-red-500/10 text-red-400 border-red-500/20';
    default:
      return 'bg-slate-500/10 text-slate-400';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'running':
      return <Activity className="h-3.5 w-3.5 animate-pulse" />;
    case 'idle':
      return <Clock className="h-3.5 w-3.5" />;
    case 'paused':
      return <Pause className="h-3.5 w-3.5" />;
    case 'error':
      return <AlertCircle className="h-3.5 w-3.5" />;
    default:
      return <Clock className="h-3.5 w-3.5" />;
  }
};

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [agentList, setAgentList] = useState(agents);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setAgentList((prev) =>
        prev.map((agent) => {
          if (agent.status === 'running' && agent.progress < 100) {
            return {
              ...agent,
              progress: Math.min(agent.progress + Math.random() * 2, 100),
            };
          }
          return agent;
        })
      );
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const runningCount = agentList.filter((a) => a.status === 'running').length;
  const idleCount = agentList.filter((a) => a.status === 'idle').length;
  const pausedCount = agentList.filter((a) => a.status === 'paused').length;

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
          <h1 className="text-3xl font-bold text-slate-100">AI Agents</h1>
          <p className="mt-1 text-slate-400">
            Monitor and manage your AI engineering team
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button className="bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
            <Zap className="mr-2 h-4 w-4" />
            Start All
          </Button>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-violet-500/10 p-3">
              <Bot className="h-5 w-5 text-violet-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-100">{agentList.length}</p>
              <p className="text-xs text-slate-500">Total Agents</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <Play className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-400">{runningCount}</p>
              <p className="text-xs text-slate-500">Running</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-slate-500/10 p-3">
              <Clock className="h-5 w-5 text-slate-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-400">{idleCount}</p>
              <p className="text-xs text-slate-500">Idle</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <Pause className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-400">{pausedCount}</p>
              <p className="text-xs text-slate-500">Paused</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Agents Grid */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {agentList.map((agent) => (
          <Card
            key={agent.id}
            className={`cursor-pointer border-slate-800 bg-slate-900/50 backdrop-blur-sm transition-all hover:border-slate-700 hover:bg-slate-800/50 ${
              selectedAgent?.id === agent.id ? 'ring-2 ring-violet-500/50' : ''
            }`}
            onClick={() => setSelectedAgent(agent)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className={`rounded-lg bg-gradient-to-br ${agent.color} p-2.5`}>
                  <agent.icon className="h-5 w-5 text-white" />
                </div>
                <Badge variant="outline" className={getStatusColor(agent.status)}>
                  <span className="mr-1.5">{getStatusIcon(agent.status)}</span>
                  {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <h3 className="font-semibold text-slate-100">{agent.name}</h3>
                <p className="text-xs text-slate-500">{agent.role}</p>
              </div>
              <p className="text-sm text-slate-400 line-clamp-2">{agent.description}</p>

              {agent.status === 'running' && (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-500">{agent.currentTask}</span>
                    <span className="text-slate-300">{Math.round(agent.progress)}%</span>
                  </div>
                  <Progress value={agent.progress} className="h-1.5 bg-slate-800" />
                </div>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{agent.executionTime}</span>
                </div>
                {agent.status === 'running' && (
                  <div className="flex items-center gap-1">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400"></span>
                    <span className="text-xs text-emerald-400">Active</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Agent Detail Panel */}
      {selectedAgent && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid gap-6 lg:grid-cols-3"
        >
          <Card className="lg:col-span-2 border-slate-800 bg-slate-900/50">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className={`rounded-xl bg-gradient-to-br ${selectedAgent.color} p-3`}>
                  <selectedAgent.icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-xl text-slate-100">{selectedAgent.name}</CardTitle>
                  <p className="text-sm text-slate-400">{selectedAgent.role}</p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-4">
                  <p className="text-xs text-slate-500">Status</p>
                  <Badge variant="outline" className={`mt-1 ${getStatusColor(selectedAgent.status)}`}>
                    {selectedAgent.status.charAt(0).toUpperCase() + selectedAgent.status.slice(1)}
                  </Badge>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-4">
                  <p className="text-xs text-slate-500">Progress</p>
                  <p className="mt-1 font-medium text-slate-200">{Math.round(selectedAgent.progress)}%</p>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-4">
                  <p className="text-xs text-slate-500">Execution Time</p>
                  <p className="mt-1 font-medium text-slate-200">{selectedAgent.executionTime}</p>
                </div>
              </div>

              {selectedAgent.status === 'running' && (
                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm text-slate-500">Current Task Progress</span>
                    <span className="text-sm font-medium text-slate-200">
                      {Math.round(selectedAgent.progress)}%
                    </span>
                  </div>
                  <Progress value={selectedAgent.progress} className="h-3 bg-slate-800" />
                  <p className="mt-2 text-sm text-slate-400">{selectedAgent.currentTask}</p>
                </div>
              )}

              <div className="flex gap-3">
                {selectedAgent.status === 'running' ? (
                  <Button variant="outline" className="flex-1 border-slate-700 text-slate-300 hover:bg-slate-800">
                    <Pause className="mr-2 h-4 w-4" />
                    Pause Agent
                  </Button>
                ) : (
                  <Button className="flex-1 bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
                    <Play className="mr-2 h-4 w-4" />
                    Resume Agent
                  </Button>
                )}
                <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Restart
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="text-lg text-slate-100">Activity Log</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                <div className="space-y-3">
                  {selectedAgent.logs.map((log, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="mt-1 rounded-full bg-violet-500/10 p-1">
                        <Terminal className="h-3 w-3 text-violet-400" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-300">{log}</p>
                        <p className="text-xs text-slate-500">{index * 5 + 2} min ago</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
}
