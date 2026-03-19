'use client';

export const dynamic = 'force-dynamic';

import { motion } from 'framer-motion';
import {
  FlaskConical,
  CheckCircle2,
  AlertCircle,
  Clock,
  XCircle,
  Play,
  RefreshCw,
  FileText,
  Shield,
  Layout,
  Code2,
  Server,
  Zap,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useState } from 'react';

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

interface Simulation {
  id: string;
  name: string;
  type: string;
  description: string;
  status: 'passed' | 'failed' | 'running' | 'pending';
  progress: number;
  issues: number;
  warnings: number;
  duration: string;
  lastRun: string;
  icon: React.ElementType;
  color: string;
  details: {
    category: string;
    items: { name: string; status: 'pass' | 'fail' | 'warn'; message: string }[];
  }[];
}

const simulations: Simulation[] = [
  {
    id: '1',
    name: 'UX Flow Simulation',
    type: 'User Experience',
    description: 'Validates user journeys and interface interactions',
    status: 'passed',
    progress: 100,
    issues: 0,
    warnings: 2,
    duration: '3m 45s',
    lastRun: '10 min ago',
    icon: Layout,
    color: 'from-emerald-500 to-teal-600',
    details: [
      {
        category: 'Navigation Flow',
        items: [
          { name: 'Home to Dashboard', status: 'pass', message: 'Smooth transition' },
          { name: 'Settings Access', status: 'pass', message: 'Clear path' },
          { name: 'Logout Flow', status: 'warn', message: 'Could add confirmation' },
        ],
      },
      {
        category: 'Form Validation',
        items: [
          { name: 'Email Validation', status: 'pass', message: 'Proper regex' },
          { name: 'Password Strength', status: 'pass', message: 'Strong requirements' },
        ],
      },
    ],
  },
  {
    id: '2',
    name: 'Architecture Simulation',
    type: 'System Design',
    description: 'Tests scalability and system resilience',
    status: 'failed',
    progress: 100,
    issues: 3,
    warnings: 5,
    duration: '5m 20s',
    lastRun: '25 min ago',
    icon: Server,
    color: 'from-red-500 to-rose-600',
    details: [
      {
        category: 'Scalability',
        items: [
          { name: 'Database Connections', status: 'fail', message: 'Pool size too small' },
          { name: 'Load Balancing', status: 'pass', message: 'Properly configured' },
          { name: 'Caching Strategy', status: 'warn', message: 'Could be optimized' },
        ],
      },
      {
        category: 'Security',
        items: [
          { name: 'Authentication', status: 'pass', message: 'JWT properly implemented' },
          { name: 'Rate Limiting', status: 'fail', message: 'Missing on public endpoints' },
        ],
      },
    ],
  },
  {
    id: '3',
    name: 'API Contract Simulation',
    type: 'API Testing',
    description: 'Validates API endpoints and data contracts',
    status: 'running',
    progress: 67,
    issues: 0,
    warnings: 1,
    duration: '2m 15s',
    lastRun: 'Running now',
    icon: Code2,
    color: 'from-violet-500 to-purple-600',
    details: [
      {
        category: 'Endpoints',
        items: [
          { name: 'GET /api/users', status: 'pass', message: '200 OK' },
          { name: 'POST /api/auth', status: 'pass', message: '201 Created' },
          { name: 'PUT /api/profile', status: 'warn', message: 'Slow response' },
        ],
      },
    ],
  },
  {
    id: '4',
    name: 'Infrastructure Simulation',
    type: 'DevOps',
    description: 'Tests deployment and infrastructure setup',
    status: 'pending',
    progress: 0,
    issues: 0,
    warnings: 0,
    duration: '-',
    lastRun: 'Not run yet',
    icon: Shield,
    color: 'from-blue-500 to-cyan-600',
    details: [],
  },
  {
    id: '5',
    name: 'Performance Simulation',
    type: 'Performance',
    description: 'Load testing and performance benchmarks',
    status: 'passed',
    progress: 100,
    issues: 0,
    warnings: 1,
    duration: '8m 30s',
    lastRun: '1 hour ago',
    icon: Zap,
    color: 'from-amber-500 to-orange-600',
    details: [
      {
        category: 'Response Times',
        items: [
          { name: 'P50 Latency', status: 'pass', message: '45ms' },
          { name: 'P95 Latency', status: 'pass', message: '120ms' },
          { name: 'P99 Latency', status: 'warn', message: '350ms (target: 200ms)' },
        ],
      },
    ],
  },
  {
    id: '6',
    name: 'Security Simulation',
    type: 'Security',
    description: 'Vulnerability scanning and security checks',
    status: 'passed',
    progress: 100,
    issues: 0,
    warnings: 0,
    duration: '4m 10s',
    lastRun: '2 hours ago',
    icon: Shield,
    color: 'from-indigo-500 to-blue-600',
    details: [
      {
        category: 'Vulnerabilities',
        items: [
          { name: 'SQL Injection', status: 'pass', message: 'No issues found' },
          { name: 'XSS Protection', status: 'pass', message: 'Properly sanitized' },
          { name: 'CSRF Tokens', status: 'pass', message: 'Implemented correctly' },
        ],
      },
    ],
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'passed':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'failed':
      return 'bg-red-500/10 text-red-400 border-red-500/20';
    case 'running':
      return 'bg-violet-500/10 text-violet-400 border-violet-500/20';
    case 'pending':
      return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    default:
      return 'bg-slate-500/10 text-slate-400';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'passed':
      return <CheckCircle2 className="h-4 w-4" />;
    case 'failed':
      return <XCircle className="h-4 w-4" />;
    case 'running':
      return <RefreshCw className="h-4 w-4 animate-spin" />;
    case 'pending':
      return <Clock className="h-4 w-4" />;
    default:
      return <Clock className="h-4 w-4" />;
  }
};

const getItemStatusIcon = (status: string) => {
  switch (status) {
    case 'pass':
      return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    case 'fail':
      return <XCircle className="h-4 w-4 text-red-400" />;
    case 'warn':
      return <AlertCircle className="h-4 w-4 text-amber-400" />;
    default:
      return null;
  }
};

export default function SimulationsPage() {
  const [selectedSimulation, setSelectedSimulation] = useState<Simulation | null>(null);

  const passedCount = simulations.filter((s) => s.status === 'passed').length;
  const failedCount = simulations.filter((s) => s.status === 'failed').length;
  const runningCount = simulations.filter((s) => s.status === 'running').length;

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
          <h1 className="text-3xl font-bold text-slate-100">Simulations</h1>
          <p className="mt-1 text-slate-400">
            Automated testing and validation results
          </p>
        </div>
        <Button className="bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
          <Play className="mr-2 h-4 w-4" />
          Run All Simulations
        </Button>
      </motion.div>

      {/* Stats */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-violet-500/10 p-3">
              <FlaskConical className="h-5 w-5 text-violet-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-100">{simulations.length}</p>
              <p className="text-xs text-slate-500">Total Simulations</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-400">{passedCount}</p>
              <p className="text-xs text-slate-500">Passed</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-red-500/10 p-3">
              <XCircle className="h-5 w-5 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-red-400">{failedCount}</p>
              <p className="text-xs text-slate-500">Failed</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="rounded-lg bg-violet-500/10 p-3">
              <RefreshCw className="h-5 w-5 text-violet-400 animate-spin" />
            </div>
            <div>
              <p className="text-2xl font-bold text-violet-400">{runningCount}</p>
              <p className="text-xs text-slate-500">Running</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Simulations List */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <div className="grid gap-4">
            {simulations.map((sim) => (
              <Card
                key={sim.id}
                className={`cursor-pointer border-slate-800 bg-slate-900/50 backdrop-blur-sm transition-all hover:border-slate-700 hover:bg-slate-800/50 ${
                  selectedSimulation?.id === sim.id ? 'ring-2 ring-violet-500/50' : ''
                }`}
                onClick={() => setSelectedSimulation(sim)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className={`rounded-xl bg-gradient-to-br ${sim.color} p-3`}>
                      <sim.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-slate-100">{sim.name}</h3>
                          <p className="text-sm text-slate-500">{sim.type}</p>
                        </div>
                        <Badge variant="outline" className={getStatusColor(sim.status)}>
                          <span className="mr-1.5">{getStatusIcon(sim.status)}</span>
                          {sim.status.charAt(0).toUpperCase() + sim.status.slice(1)}
                        </Badge>
                      </div>
                      <p className="mt-2 text-sm text-slate-400">{sim.description}</p>

                      {sim.status === 'running' && (
                        <div className="mt-4 space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-slate-500">Progress</span>
                            <span className="text-slate-300">{sim.progress}%</span>
                          </div>
                          <Progress value={sim.progress} className="h-2 bg-slate-800" />
                        </div>
                      )}

                      <div className="mt-4 flex items-center gap-6 text-sm">
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-slate-500" />
                          <span className="text-slate-400">{sim.duration}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-slate-500" />
                          <span className="text-slate-400">{sim.lastRun}</span>
                        </div>
                        {sim.issues > 0 && (
                          <div className="flex items-center gap-2 text-red-400">
                            <AlertCircle className="h-4 w-4" />
                            <span>{sim.issues} issues</span>
                          </div>
                        )}
                        {sim.warnings > 0 && (
                          <div className="flex items-center gap-2 text-amber-400">
                            <AlertCircle className="h-4 w-4" />
                            <span>{sim.warnings} warnings</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>

        {/* Simulation Details */}
        <motion.div variants={itemVariants}>
          {selectedSimulation ? (
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className={`rounded-xl bg-gradient-to-br ${selectedSimulation.color} p-2`}>
                    <selectedSimulation.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg text-slate-100">{selectedSimulation.name}</CardTitle>
                    <p className="text-xs text-slate-500">{selectedSimulation.type}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[500px]">
                  <div className="space-y-6">
                    {selectedSimulation.details.length > 0 ? (
                      selectedSimulation.details.map((category, idx) => (
                        <div key={idx}>
                          <h4 className="mb-3 text-sm font-medium text-slate-300">
                            {category.category}
                          </h4>
                          <div className="space-y-2">
                            {category.items.map((item, itemIdx) => (
                              <div
                                key={itemIdx}
                                className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-800/30 p-3"
                              >
                                {getItemStatusIcon(item.status)}
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-slate-200">{item.name}</p>
                                  <p className="text-xs text-slate-500">{item.message}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="flex flex-col items-center justify-center py-12 text-center">
                        <Clock className="h-12 w-12 text-slate-600" />
                        <p className="mt-4 text-slate-400">Simulation not run yet</p>
                        <Button className="mt-4 bg-gradient-to-r from-violet-500 to-indigo-600">
                          <Play className="mr-2 h-4 w-4" />
                          Run Now
                        </Button>
                      </div>
                    )}
                  </div>
                </ScrollArea>

                {selectedSimulation.details.length > 0 && (
                  <div className="mt-6 flex gap-3">
                    <Button className="flex-1 bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Re-run
                    </Button>
                    <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                      <FileText className="mr-2 h-4 w-4" />
                      Export Report
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card className="border-slate-800 bg-slate-900/50">
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <FlaskConical className="h-16 w-16 text-slate-600" />
                <h3 className="mt-4 text-lg font-medium text-slate-300">Select a Simulation</h3>
                <p className="mt-2 text-sm text-slate-500">
                  Click on a simulation to view detailed results
                </p>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}
