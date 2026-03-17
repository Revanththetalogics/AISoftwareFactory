'use client';

import { motion } from 'framer-motion';
import {
  Rocket,
  Server,
  CheckCircle2,
  AlertCircle,
  Clock,
  GitBranch,
  Globe,
  Database,
  Shield,
  Terminal,
  Play,
  Pause,
  RefreshCw,
  ArrowRight,
  ExternalLink,
  Copy,
  Check,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
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

interface Environment {
  id: string;
  name: string;
  type: 'development' | 'staging' | 'production';
  status: 'running' | 'stopped' | 'deploying' | 'error';
  url: string;
  version: string;
  lastDeployed: string;
  health: 'healthy' | 'degraded' | 'unhealthy';
  metrics: {
    cpu: number;
    memory: number;
    requests: number;
    errors: number;
  };
  features: string[];
}

const environments: Environment[] = [
  {
    id: '1',
    name: 'Development',
    type: 'development',
    status: 'running',
    url: 'https://dev.myapp.theta.ai',
    version: 'v1.4.2-dev',
    lastDeployed: '2 hours ago',
    health: 'healthy',
    metrics: {
      cpu: 23,
      memory: 45,
      requests: 120,
      errors: 0,
    },
    features: ['Auto-deploy on push', 'Hot reload', 'Debug mode'],
  },
  {
    id: '2',
    name: 'Staging',
    type: 'staging',
    status: 'running',
    url: 'https://staging.myapp.theta.ai',
    version: 'v1.4.1',
    lastDeployed: '1 day ago',
    health: 'healthy',
    metrics: {
      cpu: 34,
      memory: 52,
      requests: 450,
      errors: 2,
    },
    features: ['Production-like', 'Integration tests', 'QA access'],
  },
  {
    id: '3',
    name: 'Production',
    type: 'production',
    status: 'running',
    url: 'https://myapp.theta.ai',
    version: 'v1.4.0',
    lastDeployed: '3 days ago',
    health: 'healthy',
    metrics: {
      cpu: 56,
      memory: 68,
      requests: 12500,
      errors: 12,
    },
    features: ['SSL enabled', 'CDN enabled', 'Auto-scaling'],
  },
];

const deploymentHistory = [
  {
    id: '1',
    version: 'v1.4.2-dev',
    environment: 'Development',
    status: 'success',
    timestamp: '2 hours ago',
    duration: '3m 45s',
    triggeredBy: 'AI Agent',
  },
  {
    id: '2',
    version: 'v1.4.1',
    environment: 'Staging',
    status: 'success',
    timestamp: '1 day ago',
    duration: '5m 20s',
    triggeredBy: 'AI Agent',
  },
  {
    id: '3',
    version: 'v1.4.0',
    environment: 'Production',
    status: 'success',
    timestamp: '3 days ago',
    duration: '4m 15s',
    triggeredBy: 'Manual',
  },
  {
    id: '4',
    version: 'v1.3.9',
    environment: 'Production',
    status: 'failed',
    timestamp: '5 days ago',
    duration: '2m 30s',
    triggeredBy: 'AI Agent',
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'running':
    case 'success':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'stopped':
      return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    case 'deploying':
      return 'bg-violet-500/10 text-violet-400 border-violet-500/20';
    case 'error':
    case 'failed':
      return 'bg-red-500/10 text-red-400 border-red-500/20';
    default:
      return 'bg-slate-500/10 text-slate-400';
  }
};

const getHealthIcon = (health: string) => {
  switch (health) {
    case 'healthy':
      return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    case 'degraded':
      return <AlertCircle className="h-4 w-4 text-amber-400" />;
    case 'unhealthy':
      return <AlertCircle className="h-4 w-4 text-red-400" />;
    default:
      return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
  }
};

export default function DeploymentPage() {
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
  const [showDeployDialog, setShowDeployDialog] = useState(false);

  const handleCopyUrl = (url: string) => {
    navigator.clipboard.writeText(url);
    setCopiedUrl(url);
    setTimeout(() => setCopiedUrl(null), 2000);
  };

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
          <h1 className="text-3xl font-bold text-slate-100">Deployment</h1>
          <p className="mt-1 text-slate-400">
            Manage your application environments and deployments
          </p>
        </div>
        <Dialog open={showDeployDialog} onOpenChange={setShowDeployDialog}>
          <DialogTrigger>
            <Button className="bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
              <Rocket className="mr-2 h-4 w-4" />
              Deploy to Production
            </Button>
          </DialogTrigger>
          <DialogContent className="border-slate-800 bg-slate-900">
            <DialogHeader>
              <DialogTitle className="text-xl text-slate-100">Deploy to Production</DialogTitle>
              <DialogDescription className="text-slate-400">
                This will deploy the current staging version to production. Please confirm.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-amber-400" />
                  <div>
                    <p className="font-medium text-amber-400">Warning</p>
                    <p className="text-sm text-amber-300/80">
                      This action will make your changes live. Ensure all tests have passed.
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1 border-slate-700 text-slate-300 hover:bg-slate-800"
                  onClick={() => setShowDeployDialog(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700"
                  onClick={() => setShowDeployDialog(false)}
                >
                  <Rocket className="mr-2 h-4 w-4" />
                  Confirm Deploy
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </motion.div>

      {/* Environments */}
      <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-3">
        {environments.map((env) => (
          <Card
            key={env.id}
            className="border-slate-800 bg-slate-900/50 backdrop-blur-sm"
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`rounded-lg p-2.5 ${
                      env.type === 'production'
                        ? 'bg-gradient-to-br from-violet-500 to-indigo-600'
                        : env.type === 'staging'
                        ? 'bg-gradient-to-br from-blue-500 to-cyan-600'
                        : 'bg-gradient-to-br from-slate-500 to-slate-600'
                    }`}
                  >
                    <Server className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg text-slate-100">{env.name}</CardTitle>
                    <p className="text-xs text-slate-500">{env.version}</p>
                  </div>
                </div>
                <Badge variant="outline" className={getStatusColor(env.status)}>
                  {env.status.charAt(0).toUpperCase() + env.status.slice(1)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-800/30 p-3">
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4 text-slate-500" />
                  <span className="text-sm text-slate-400">{env.url}</span>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-slate-400 hover:text-slate-200"
                  onClick={() => handleCopyUrl(env.url)}
                >
                  {copiedUrl === env.url ? (
                    <Check className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-slate-800 bg-slate-800/30 p-3">
                  <p className="text-xs text-slate-500">CPU Usage</p>
                  <div className="mt-1 flex items-center gap-2">
                    <Progress value={env.metrics.cpu} className="h-1.5 flex-1 bg-slate-800" />
                    <span className="text-sm font-medium text-slate-200">{env.metrics.cpu}%</span>
                  </div>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-800/30 p-3">
                  <p className="text-xs text-slate-500">Memory</p>
                  <div className="mt-1 flex items-center gap-2">
                    <Progress value={env.metrics.memory} className="h-1.5 flex-1 bg-slate-800" />
                    <span className="text-sm font-medium text-slate-200">{env.metrics.memory}%</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-slate-400">
                  <Clock className="h-4 w-4" />
                  <span>Deployed {env.lastDeployed}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  {getHealthIcon(env.health)}
                  <span className="capitalize text-slate-300">{env.health}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 border-slate-700 text-slate-300 hover:bg-slate-800"
                >
                  <ExternalLink className="mr-1.5 h-3.5 w-3.5" />
                  Open
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 border-slate-700 text-slate-300 hover:bg-slate-800"
                >
                  <Terminal className="mr-1.5 h-3.5 w-3.5" />
                  Logs
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Deployment History */}
      <motion.div variants={itemVariants}>
        <Card className="border-slate-800 bg-slate-900/50">
          <CardHeader>
            <CardTitle className="text-lg text-slate-100">Deployment History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {deploymentHistory.map((deployment) => (
                <div
                  key={deployment.id}
                  className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-800/30 p-4"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`rounded-lg p-2 ${
                        deployment.status === 'success'
                          ? 'bg-emerald-500/10'
                          : 'bg-red-500/10'
                      }`}
                    >
                      {deployment.status === 'success' ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-400" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-slate-200">
                        {deployment.version} → {deployment.environment}
                      </p>
                      <p className="text-sm text-slate-500">
                        {deployment.timestamp} • {deployment.duration} • {deployment.triggeredBy}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className={getStatusColor(deployment.status)}>
                    {deployment.status.charAt(0).toUpperCase() + deployment.status.slice(1)}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
