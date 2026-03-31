'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Rocket,
  Globe,
  Server,
  Clock,
  GitCommit,
  GitBranch,
  Activity,
  Cpu,
  HardDrive,
  Network,
  RefreshCw,
  Pause,
  RotateCcw,
  Terminal,
  ChevronRight,
  Shield,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { type DeploymentEnvironment, type DeploymentStatus } from '@/components/system/deployment-status-card';
import { useDeployments } from '@/lib/hooks/useDeployments';
import { DeploymentCreateDialog } from '@/components/deployment/DeploymentCreateDialog';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Deployment data will be fetched from database
const mockDeployments = [
  {
    id: 'dep-001',
    environment: 'production' as DeploymentEnvironment,
    status: 'running' as DeploymentStatus,
    version: '2.4.1',
    commitHash: 'a1b2c3d',
    deployedAt: new Date('2024-01-18T14:30:00'),
    buildDuration: '12m 34s',
    healthChecks: [
      { name: 'API', status: 'passing' as const, lastCheck: new Date(), responseTime: 45 },
      { name: 'Database', status: 'passing' as const, lastCheck: new Date(), responseTime: 12 },
      { name: 'Cache', status: 'passing' as const, lastCheck: new Date(), responseTime: 8 },
      { name: 'Queue', status: 'passing' as const, lastCheck: new Date(), responseTime: 23 },
    ],
    metrics: {
      cpu: 42.5,
      memory: 68.2,
      requests: 1250,
      latency: 45,
      errorRate: 0.02,
    },
  },
  {
    id: 'dep-002',
    environment: 'staging' as DeploymentEnvironment,
    status: 'running' as DeploymentStatus,
    version: '2.5.0-beta',
    commitHash: 'e4f5g6h',
    deployedAt: new Date('2024-01-18T10:15:00'),
    buildDuration: '10m 12s',
    healthChecks: [
      { name: 'API', status: 'passing' as const, lastCheck: new Date(), responseTime: 52 },
      { name: 'Database', status: 'passing' as const, lastCheck: new Date(), responseTime: 15 },
      { name: 'Cache', status: 'passing' as const, lastCheck: new Date(), responseTime: 10 },
    ],
    metrics: {
      cpu: 35.8,
      memory: 54.3,
      requests: 320,
      latency: 52,
      errorRate: 0.05,
    },
  },
  {
    id: 'dep-003',
    environment: 'development' as DeploymentEnvironment,
    status: 'building' as DeploymentStatus,
    version: '2.5.0-dev',
    commitHash: 'i7j8k9l',
    buildDuration: 'In progress',
    healthChecks: [],
  },
];

// Mock deployment history
const deploymentHistory = [
  { version: 'v2.4.1', env: 'production', status: 'success', date: '2024-01-18', duration: '12m' },
  { version: 'v2.4.0', env: 'production', status: 'success', date: '2024-01-15', duration: '11m' },
  { version: 'v2.3.2', env: 'production', status: 'rollback', date: '2024-01-12', duration: '8m' },
  { version: 'v2.3.1', env: 'production', status: 'failed', date: '2024-01-10', duration: '15m' },
  { version: 'v2.3.0', env: 'production', status: 'success', date: '2024-01-08', duration: '10m' },
];

// Metrics data
const trafficData = [
  { time: '00:00', requests: 800, errors: 2 },
  { time: '04:00', requests: 450, errors: 1 },
  { time: '08:00', requests: 1200, errors: 3 },
  { time: '12:00', requests: 2100, errors: 5 },
  { time: '16:00', requests: 1850, errors: 4 },
  { time: '20:00', requests: 1400, errors: 3 },
  { time: '23:59', requests: 950, errors: 2 },
];

const resourceData = [
  { time: '00:00', cpu: 35, memory: 62 },
  { time: '04:00', cpu: 28, memory: 58 },
  { time: '08:00', cpu: 55, memory: 70 },
  { time: '12:00', cpu: 72, memory: 78 },
  { time: '16:00', cpu: 68, memory: 75 },
  { time: '20:00', cpu: 48, memory: 68 },
  { time: '23:59', cpu: 38, memory: 64 },
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
    case 'success':
      return 'text-state-success';
    case 'failed':
      return 'text-state-error';
    case 'rollback':
      return 'text-state-warning';
    default:
      return 'text-text-secondary';
  }
};

export default function DeploymentPage() {
  // Fetch real deployments from database
  const { data: dbDeployments, isLoading, error } = useDeployments();
  
  const [selectedEnvironment, setSelectedEnvironment] = useState<DeploymentEnvironment | 'all'>('all');

  // Use real deployments if available, otherwise use mock for display
  const deployments = dbDeployments || mockDeployments;
  
  const filteredDeployments = deployments.filter((dep: any) => dep.environment === selectedEnvironment);

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
          <h1 className="text-2xl font-bold text-text-primary">Deployments</h1>
          <p className="text-text-secondary">
            {isLoading ? 'Loading deployments...' : `${deployments.length} deployments tracked`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="border-border-default text-text-secondary">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <DeploymentCreateDialog />
        </div>
      </motion.div>

      {/* Environment Cards */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-3">
        {deployments.map((deployment) => (
          <button
            key={deployment.id}
            onClick={() => setSelectedEnv(deployment.environment)}
            className={`text-left p-4 rounded-xl border transition-all ${
              selectedEnv === deployment.environment
                ? 'border-state-running bg-state-running-dim'
                : 'border-border-default bg-bg-panel hover:border-emphasis'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                {deployment.environment === 'production' && <Globe className="h-5 w-5 text-state-error" />}
                {deployment.environment === 'staging' && <Server className="h-5 w-5 text-state-warning" />}
                {deployment.environment === 'development' && <Terminal className="h-5 w-5 text-state-running" />}
                <span className="font-semibold text-text-primary capitalize">{deployment.environment}</span>
              </div>
              <Badge
                variant="outline"
                className={
                  deployment.status === 'running'
                    ? 'bg-state-success-dim text-state-success'
                    : deployment.status === 'building'
                    ? 'bg-state-running-dim text-state-running'
                    : 'bg-state-error-dim text-state-error'
                }
              >
                {deployment.status === 'running' && <span className="w-1.5 h-1.5 rounded-full bg-state-success animate-pulse mr-1" />}
                {deployment.status}
              </Badge>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-secondary">Version</span>
                <span className="font-mono text-text-primary">{deployment.version}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-secondary">Commit</span>
                <span className="font-mono text-text-code">{deployment.commitHash}</span>
              </div>
              {deployment.deployedAt && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">Deployed</span>
                  <span className="text-text-primary">
                    {deployment.deployedAt.toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </button>
        ))}
      </motion.div>

      {/* Selected Environment Details */}
      {activeDeployment && (
        <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-3">
          {/* Main Status Card */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-border-default bg-bg-panel">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg text-text-primary capitalize">
                    {activeDeployment.environment} Environment
                  </CardTitle>
                  <CardDescription className="text-text-secondary">
                    Current deployment status and metrics
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" className="border-border-default">
                    <Pause className="mr-2 h-4 w-4" />
                    Pause
                  </Button>
                  <Button variant="outline" size="sm" className="border-border-default">
                    <RotateCcw className="mr-2 h-4 w-4" />
                    Rollback
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Version Info */}
                <div className="flex items-center gap-6 p-4 rounded-lg bg-bg-elevated border border-border-subtle">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-state-running-dim">
                      <GitCommit className="h-5 w-5 text-state-running" />
                    </div>
                    <div>
                      <p className="text-xs text-text-secondary">Version</p>
                      <p className="font-mono font-medium text-text-primary">{activeDeployment.version}</p>
                    </div>
                  </div>
                  <div className="h-8 w-px bg-border-subtle" />
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-state-running-dim">
                      <GitBranch className="h-5 w-5 text-state-running" />
                    </div>
                    <div>
                      <p className="text-xs text-text-secondary">Commit</p>
                      <p className="font-mono font-medium text-text-code">{activeDeployment.commitHash}</p>
                    </div>
                  </div>
                  <div className="h-8 w-px bg-border-subtle" />
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-state-running-dim">
                      <Clock className="h-5 w-5 text-state-running" />
                    </div>
                    <div>
                      <p className="text-xs text-text-secondary">Build Time</p>
                      <p className="font-mono font-medium text-text-primary">{activeDeployment.buildDuration}</p>
                    </div>
                  </div>
                </div>

                {/* Health Checks */}
                {activeDeployment.healthChecks.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-text-secondary mb-3">Health Checks</h4>
                    <div className="grid grid-cols-4 gap-3">
                      {activeDeployment.healthChecks.map((check) => (
                        <div
                          key={check.name}
                          className="p-3 rounded-lg border border-border-subtle bg-bg-elevated"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <div
                              className={`w-2 h-2 rounded-full ${
                                check.status === 'passing' ? 'bg-state-success' : 'bg-state-error'
                              }`}
                            />
                            <span className="text-sm font-medium text-text-primary">{check.name}</span>
                          </div>
                          <p className="text-xs text-text-secondary">
                            {check.responseTime}ms response
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metrics */}
                {activeDeployment.metrics && (
                  <div>
                    <h4 className="text-sm font-medium text-text-secondary mb-3">Resource Metrics</h4>
                    <div className="grid grid-cols-4 gap-4">
                      <div className="p-4 rounded-lg border border-border-subtle bg-bg-elevated">
                        <div className="flex items-center gap-2 mb-2">
                          <Cpu className="h-4 w-4 text-text-secondary" />
                          <span className="text-xs text-text-secondary">CPU</span>
                        </div>
                        <p className={`text-xl font-bold font-mono ${
                          activeDeployment.metrics.cpu > 80 ? 'text-state-error' : 
                          activeDeployment.metrics.cpu > 60 ? 'text-state-warning' : 'text-state-success'
                        }`}>
                          {activeDeployment.metrics.cpu}%
                        </p>
                      </div>
                      <div className="p-4 rounded-lg border border-border-subtle bg-bg-elevated">
                        <div className="flex items-center gap-2 mb-2">
                          <HardDrive className="h-4 w-4 text-text-secondary" />
                          <span className="text-xs text-text-secondary">Memory</span>
                        </div>
                        <p className={`text-xl font-bold font-mono ${
                          activeDeployment.metrics.memory > 80 ? 'text-state-error' : 
                          activeDeployment.metrics.memory > 60 ? 'text-state-warning' : 'text-state-success'
                        }`}>
                          {activeDeployment.metrics.memory}%
                        </p>
                      </div>
                      <div className="p-4 rounded-lg border border-border-subtle bg-bg-elevated">
                        <div className="flex items-center gap-2 mb-2">
                          <Network className="h-4 w-4 text-text-secondary" />
                          <span className="text-xs text-text-secondary">Requests</span>
                        </div>
                        <p className="text-xl font-bold font-mono text-text-primary">
                          {activeDeployment.metrics.requests}/s
                        </p>
                      </div>
                      <div className="p-4 rounded-lg border border-border-subtle bg-bg-elevated">
                        <div className="flex items-center gap-2 mb-2">
                          <Activity className="h-4 w-4 text-text-secondary" />
                          <span className="text-xs text-text-secondary">Latency</span>
                        </div>
                        <p className={`text-xl font-bold font-mono ${
                          activeDeployment.metrics.latency > 200 ? 'text-state-error' : 
                          activeDeployment.metrics.latency > 100 ? 'text-state-warning' : 'text-state-success'
                        }`}>
                          {activeDeployment.metrics.latency}ms
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Traffic Chart */}
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">Traffic Overview</CardTitle>
                <CardDescription className="text-text-secondary">
                  Request volume and error rate (24h)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trafficData}>
                      <defs>
                        <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
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
                      />
                      <Area
                        type="monotone"
                        dataKey="requests"
                        stroke="var(--state-running)"
                        strokeWidth={2}
                        fill="url(#colorRequests)"
                        name="Requests"
                      />
                      <Area
                        type="monotone"
                        dataKey="errors"
                        stroke="var(--state-error)"
                        strokeWidth={2}
                        fill="transparent"
                        name="Errors"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start border-border-default text-text-secondary">
                  <Shield className="mr-2 h-4 w-4" />
                  View Logs
                  <ChevronRight className="ml-auto h-4 w-4" />
                </Button>
                <Button variant="outline" className="w-full justify-start border-border-default text-text-secondary">
                  <Activity className="mr-2 h-4 w-4" />
                  Monitoring
                  <ChevronRight className="ml-auto h-4 w-4" />
                </Button>
                <Button variant="outline" className="w-full justify-start border-border-default text-text-secondary">
                  <GitBranch className="mr-2 h-4 w-4" />
                  View Source
                  <ChevronRight className="ml-auto h-4 w-4" />
                </Button>
              </CardContent>
            </Card>

            {/* Deployment History */}
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">Recent Deployments</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {deploymentHistory.map((dep, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-lg border border-border-subtle bg-bg-elevated"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            dep.status === 'success'
                              ? 'bg-state-success'
                              : dep.status === 'failed'
                              ? 'bg-state-error'
                              : 'bg-state-warning'
                          }`}
                        />
                        <div>
                          <p className="font-medium text-text-primary text-sm">{dep.version}</p>
                          <p className="text-xs text-text-secondary">
                            {dep.date} • {dep.duration}
                          </p>
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className={`text-xs ${getStatusColor(dep.status)}`}
                      >
                        {dep.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Resource Usage */}
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">Resource Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[150px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={resourceData}>
                      <defs>
                        <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="var(--state-running)" stopOpacity={0.3} />
                          <stop offset="100%" stopColor="var(--state-running)" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                      <XAxis dataKey="time" stroke="var(--text-tertiary)" fontSize={10} />
                      <YAxis stroke="var(--text-tertiary)" fontSize={10} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'var(--bg-elevated)',
                          border: '1px solid var(--border-default)',
                          borderRadius: '8px',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="cpu"
                        stroke="var(--state-running)"
                        strokeWidth={2}
                        fill="url(#colorCpu)"
                        name="CPU %"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
