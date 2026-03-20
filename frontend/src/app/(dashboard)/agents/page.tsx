'use client';

// Prevent static generation - this page requires authentication
export const dynamic = 'force-dynamic';

import { motion } from 'framer-motion';
import { Bot, Activity, Clock, Pause, Play, RefreshCw, Zap, Terminal } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useState, useEffect } from 'react';
import { AgentCard, AgentGrid } from '@/components/system/agent-card';
import { containerVariants, slideVariants } from '@/lib/motion-variants';
import type { AgentRole, AgentStatus } from '@/components/system/agent-card';

interface AgentData {
  id: string;
  name: string;
  role: AgentRole;
  description: string;
  status: AgentStatus;
  currentTask: string;
  progress: number;
  executionTime: string;
  logs: string[];
}

const agents: AgentData[] = [
  {
    id: '1',
    name: 'CEO Agent',
    role: 'executive',
    description: 'Strategic oversight and decision making',
    status: 'running',
    currentTask: 'Reviewing project roadmap',
    progress: 78,
    executionTime: '2h 15m',
    logs: ['Analyzing market requirements', 'Setting project priorities', 'Allocating resources'],
  },
  {
    id: '2',
    name: 'Product Manager',
    role: 'product',
    description: 'Requirements gathering and feature planning',
    status: 'running',
    currentTask: 'Writing user stories',
    progress: 65,
    executionTime: '1h 45m',
    logs: ['Interviewing stakeholders', 'Defining user personas', 'Creating product backlog'],
  },
  {
    id: '3',
    name: 'Backend Engineer',
    role: 'backend',
    description: 'API development and database design',
    status: 'running',
    currentTask: 'Building authentication API',
    progress: 82,
    executionTime: '3h 20m',
    logs: ['Designing database schema', 'Implementing JWT auth', 'Writing API tests'],
  },
  {
    id: '4',
    name: 'Frontend Engineer',
    role: 'frontend',
    description: 'UI/UX implementation and component development',
    status: 'idle',
    currentTask: 'Waiting for API specs',
    progress: 0,
    executionTime: '0m',
    logs: ['Reviewing design mockups', 'Setting up component library', 'Configuring Tailwind'],
  },
  {
    id: '5',
    name: 'UX Designer',
    role: 'design',
    description: 'User experience and interface design',
    status: 'running',
    currentTask: 'Creating wireframes',
    progress: 45,
    executionTime: '1h 30m',
    logs: ['Researching user needs', 'Sketching layouts', 'Defining color palette'],
  },
  {
    id: '6',
    name: 'DevOps Engineer',
    role: 'devops',
    description: 'Infrastructure and deployment automation',
    status: 'idle',
    currentTask: 'Monitoring CI/CD pipeline',
    progress: 100,
    executionTime: '45m',
    logs: ['Setting up Docker containers', 'Configuring GitHub Actions', 'Deploying to staging'],
  },
  {
    id: '7',
    name: 'QA Engineer',
    role: 'qa',
    description: 'Testing and quality verification',
    status: 'paused',
    currentTask: 'Waiting for code completion',
    progress: 30,
    executionTime: '1h 10m',
    logs: ['Writing test cases', 'Setting up test environment', 'Planning test strategy'],
  },
  {
    id: '8',
    name: 'Database Architect',
    role: 'database',
    description: 'Database design and optimization',
    status: 'running',
    currentTask: 'Optimizing query performance',
    progress: 60,
    executionTime: '2h 5m',
    logs: ['Designing entity relationships', 'Creating migration scripts', 'Indexing tables'],
  },
];

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<AgentData | null>(null);
  const [agentList, setAgentList] = useState(agentList);

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
      <motion.div variants={slideVariants} initial="hidden" animate="visible" className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">AI Agents</h1>
          <p className="mt-1 text-text-secondary">
            Monitor and manage your AI engineering team
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-border-default text-text-secondary hover:bg-bg-hover">
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
      <motion.div variants={slideVariants} initial="hidden" animate="visible" className="grid gap-4 md:grid-cols-4">
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-state-running-dim p-3">
              <Bot className="h-5 w-5 text-state-running" />
            </div>
            <div>
              <p className="text-2xl font-bold text-text-primary">{agentList.length}</p>
              <p className="text-xs text-text-tertiary">Total Agents</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-state-success-dim p-3">
              <Play className="h-5 w-5 text-state-success" />
            </div>
            <div>
              <p className="text-2xl font-bold text-state-success">{runningCount}</p>
              <p className="text-xs text-text-tertiary">Running</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-state-idle-dim p-3">
              <Clock className="h-5 w-5 text-state-idle" />
            </div>
            <div>
              <p className="text-2xl font-bold text-state-idle">{idleCount}</p>
              <p className="text-xs text-text-tertiary">Idle</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-state-warning-dim p-3">
              <Pause className="h-5 w-5 text-state-warning" />
            </div>
            <div>
              <p className="text-2xl font-bold text-state-warning">{pausedCount}</p>
              <p className="text-xs text-text-tertiary">Paused</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Agents Grid - Using new AgentCard component */}
      <motion.div variants={slideVariants} initial="hidden" animate="visible">
        <AgentGrid columns={4}>
          {agentList.map((agent) => (
            <AgentCard
              key={agent.id}
              agentId={agent.id}
              name={agent.name}
              role={agent.role}
              status={agent.status}
              currentTask={agent.currentTask}
              progress={agent.progress}
              metrics={{
                executionTime: agent.executionTime,
                tasksCompleted: agent.logs.length,
              }}
              onClick={() => setSelectedAgent(agent)}
              compact
            />
          ))}
        </AgentGrid>
      </motion.div>

      {/* Agent Detail Panel */}
      {selectedAgent && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid gap-6 lg:grid-cols-3"
        >
          <Card className="lg:col-span-2 border-border-default bg-bg-panel">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 p-3">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-xl text-text-primary">{selectedAgent.name}</CardTitle>
                  <p className="text-sm text-text-secondary">{selectedAgent.role}</p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="rounded-lg border border-border-default bg-bg-elevated p-4">
                  <p className="text-xs text-text-tertiary">Status</p>
                  <Badge variant="outline" className={`mt-1 ${
                    selectedAgent.status === 'running' ? 'bg-state-success-dim text-state-success border-state-success' :
                    selectedAgent.status === 'idle' ? 'bg-state-idle-dim text-state-idle border-state-idle' :
                    'bg-state-warning-dim text-state-warning border-state-warning'
                  }`}>
                    {selectedAgent.status.charAt(0).toUpperCase() + selectedAgent.status.slice(1)}
                  </Badge>
                </div>
                <div className="rounded-lg border border-border-default bg-bg-elevated p-4">
                  <p className="text-xs text-text-tertiary">Progress</p>
                  <p className="mt-1 font-medium text-text-primary">{Math.round(selectedAgent.progress)}%</p>
                </div>
                <div className="rounded-lg border border-border-default bg-bg-elevated p-4">
                  <p className="text-xs text-text-tertiary">Execution Time</p>
                  <p className="mt-1 font-medium text-text-primary">{selectedAgent.executionTime}</p>
                </div>
              </div>

              {selectedAgent.status === 'running' && (
                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm text-text-tertiary">Current Task Progress</span>
                    <span className="text-sm font-medium text-text-primary">
                      {Math.round(selectedAgent.progress)}%
                    </span>
                  </div>
                  <div className="h-3 w-full rounded-full bg-bg-base overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-violet-500 to-indigo-600 transition-all duration-300"
                      style={{ width: `${selectedAgent.progress}%` }}
                    />
                  </div>
                  <p className="mt-2 text-sm text-text-secondary">{selectedAgent.currentTask}</p>
                </div>
              )}

              <div className="flex gap-3">
                {selectedAgent.status === 'running' ? (
                  <Button variant="outline" className="flex-1 border-border-default text-text-secondary hover:bg-bg-hover">
                    <Pause className="mr-2 h-4 w-4" />
                    Pause Agent
                  </Button>
                ) : (
                  <Button className="flex-1 bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
                    <Play className="mr-2 h-4 w-4" />
                    Resume Agent
                  </Button>
                )}
                <Button variant="outline" className="border-border-default text-text-secondary hover:bg-bg-hover">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Restart
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border-default bg-bg-panel">
            <CardHeader>
              <CardTitle className="text-lg text-text-primary">Activity Log</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                <div className="space-y-3">
                  {selectedAgent.logs.map((log, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="mt-1 rounded-full bg-state-running-dim p-1">
                        <Terminal className="h-3 w-3 text-state-running" />
                      </div>
                      <div>
                        <p className="text-sm text-text-primary">{log}</p>
                        <p className="text-xs text-text-tertiary">{index * 5 + 2} min ago</p>
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
