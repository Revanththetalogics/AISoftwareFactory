'use client';

import { useState } from 'react';
import { 
  Rocket, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  ArrowRight,
  GitBranch,
  Server,
  Globe,
  AlertTriangle
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

interface DeploymentEnvironment {
  id: string;
  name: string;
  status: 'empty' | 'deploying' | 'success' | 'failed' | 'rolling-back';
  version: string | null;
  url: string | null;
  lastDeployed: string | null;
  healthChecks: {
    name: string;
    status: 'passing' | 'failing' | 'unknown';
  }[];
  metrics: {
    cpu: number;
    memory: number;
    requests: number;
  };
}

interface DeploymentStage {
  id: string;
  name: string;
  icon: React.ElementType;
  environments: DeploymentEnvironment[];
}

const deploymentStages: DeploymentStage[] = [
  {
    id: 'development',
    name: 'Development',
    icon: GitBranch,
    environments: [
      {
        id: 'dev',
        name: 'Dev',
        status: 'success',
        version: 'v1.2.3-dev.45',
        url: 'https://dev-app.thetaai.dev',
        lastDeployed: '2024-01-15T10:30:00Z',
        healthChecks: [
          { name: 'API', status: 'passing' },
          { name: 'Database', status: 'passing' },
          { name: 'Cache', status: 'passing' },
        ],
        metrics: { cpu: 45, memory: 62, requests: 120 },
      },
    ],
  },
  {
    id: 'staging',
    name: 'Staging',
    icon: Server,
    environments: [
      {
        id: 'staging',
        name: 'Staging',
        status: 'success',
        version: 'v1.2.3-rc.2',
        url: 'https://staging-app.thetaai.dev',
        lastDeployed: '2024-01-15T08:15:00Z',
        healthChecks: [
          { name: 'API', status: 'passing' },
          { name: 'Database', status: 'passing' },
          { name: 'Cache', status: 'passing' },
        ],
        metrics: { cpu: 38, memory: 55, requests: 89 },
      },
    ],
  },
  {
    id: 'production',
    name: 'Production',
    icon: Globe,
    environments: [
      {
        id: 'prod-us',
        name: 'US East',
        status: 'success',
        version: 'v1.2.2',
        url: 'https://app.thetaai.com',
        lastDeployed: '2024-01-14T14:00:00Z',
        healthChecks: [
          { name: 'API', status: 'passing' },
          { name: 'Database', status: 'passing' },
          { name: 'CDN', status: 'passing' },
        ],
        metrics: { cpu: 52, memory: 68, requests: 2450 },
      },
      {
        id: 'prod-eu',
        name: 'EU West',
        status: 'success',
        version: 'v1.2.2',
        url: 'https://eu-app.thetaai.com',
        lastDeployed: '2024-01-14T14:05:00Z',
        healthChecks: [
          { name: 'API', status: 'passing' },
          { name: 'Database', status: 'passing' },
          { name: 'CDN', status: 'passing' },
        ],
        metrics: { cpu: 48, memory: 64, requests: 1890 },
      },
    ],
  },
];

interface EnvironmentCardProps {
  environment: DeploymentEnvironment;
  canPromote: boolean;
  onPromote: () => void;
  onRollback: () => void;
}

function EnvironmentCard({ environment, canPromote, onPromote, onRollback }: EnvironmentCardProps) {
  const statusConfig = {
    empty: { color: 'text-text-tertiary', bgColor: 'bg-bg-base', label: 'Empty' },
    deploying: { color: 'text-state-queued', bgColor: 'bg-state-queued-dim', label: 'Deploying' },
    success: { color: 'text-state-success', bgColor: 'bg-state-success-dim', label: 'Healthy' },
    failed: { color: 'text-state-error', bgColor: 'bg-state-error-dim', label: 'Failed' },
    'rolling-back': { color: 'text-state-warning', bgColor: 'bg-state-warning-dim', label: 'Rolling Back' },
  };

  const config = statusConfig[environment.status];

  return (
    <div className={cn('rounded-lg border p-4', config.bgColor, 'border-border-default/50')}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-medium text-text-primary">{environment.name}</h4>
          {environment.version && (
            <p className="text-xs text-text-secondary">{environment.version}</p>
          )}
        </div>
        <Badge variant="outline" className={cn('text-xs', config.color)}>
          {environment.status === 'deploying' && (
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
          )}
          {environment.status === 'success' && (
            <CheckCircle2 className="mr-1 h-3 w-3" />
          )}
          {environment.status === 'failed' && (
            <XCircle className="mr-1 h-3 w-3" />
          )}
          {config.label}
        </Badge>
      </div>

      {environment.url && (
        <a 
          href={environment.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-state-running hover:underline block mb-3"
        >
          {environment.url}
        </a>
      )}

      {/* Health Checks */}
      <div className="space-y-1 mb-3">
        {environment.healthChecks.map((check) => (
          <div key={check.name} className="flex items-center gap-2 text-xs">
            {check.status === 'passing' ? (
              <CheckCircle2 className="h-3 w-3 text-state-success" />
            ) : check.status === 'failing' ? (
              <XCircle className="h-3 w-3 text-state-error" />
            ) : (
              <Loader2 className="h-3 w-3 text-text-tertiary" />
            )}
            <span className={cn(
              check.status === 'passing' ? 'text-text-secondary' : 'text-text-tertiary'
            )}>
              {check.name}
            </span>
          </div>
        ))}
      </div>

      {/* Metrics */}
      {environment.status !== 'empty' && (
        <div className="grid grid-cols-3 gap-2 text-xs mb-3">
          <div className="text-center p-2 rounded bg-bg-panel">
            <div className="text-text-tertiary">CPU</div>
            <div className="font-medium text-text-primary">{environment.metrics.cpu}%</div>
          </div>
          <div className="text-center p-2 rounded bg-bg-panel">
            <div className="text-text-tertiary">Memory</div>
            <div className="font-medium text-text-primary">{environment.metrics.memory}%</div>
          </div>
          <div className="text-center p-2 rounded bg-bg-panel">
            <div className="text-text-tertiary">Req/s</div>
            <div className="font-medium text-text-primary">{environment.metrics.requests}</div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {canPromote && environment.status === 'success' && (
          <Button size="sm" className="flex-1" onClick={onPromote}>
            Promote
            <ArrowRight className="ml-1 h-3 w-3" />
          </Button>
        )}
        {environment.status === 'failed' && (
          <Button size="sm" variant="outline" className="flex-1" onClick={onRollback}>
            Rollback
          </Button>
        )}
      </div>
    </div>
  );
}

interface DeploymentPipelineProps {
  projectId?: string;
  className?: string;
}

export function DeploymentPipeline({ projectId, className }: DeploymentPipelineProps) {
  const [stages, setStages] = useState(deploymentStages);
  const [isPromoting, setIsPromoting] = useState(false);

  const handlePromote = async (fromStage: string, toStage: string) => {
    setIsPromoting(true);
    
    // Simulate promotion
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    toast.success(`Promoted from ${fromStage} to ${toStage}`);
    setIsPromoting(false);
  };

  const handleRollback = async (envId: string) => {
    toast.info(`Initiating rollback for ${envId}...`);
    // Implementation would call API
  };

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary">Deployment Pipeline</CardTitle>
            <p className="text-sm text-text-secondary">
              Multi-environment deployment and promotion
            </p>
          </div>
          <Button variant="outline" size="sm">
            <Rocket className="mr-2 h-4 w-4" />
            Deploy
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {stages.map((stage, stageIndex) => {
            const StageIcon = stage.icon;
            const isLastStage = stageIndex === stages.length - 1;
            
            return (
              <div key={stage.id} className="relative">
                {/* Stage Header */}
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-state-queued-dim">
                    <StageIcon className="h-4 w-4 text-state-queued" />
                  </div>
                  <h3 className="font-medium text-text-primary">{stage.name}</h3>
                  {!isLastStage && (
                    <ArrowRight className="h-4 w-4 text-text-tertiary ml-auto" />
                  )}
                </div>

                {/* Environments */}
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 pl-11">
                  {stage.environments.map((env) => (
                    <EnvironmentCard
                      key={env.id}
                      environment={env}
                      canPromote={!isLastStage && env.status === 'success'}
                      onPromote={() => {
                        const nextStage = stages[stageIndex + 1];
                        if (nextStage) {
                          handlePromote(stage.name, nextStage.name);
                        }
                      }}
                      onRollback={() => handleRollback(env.id)}
                    />
                  ))}
                </div>

                {/* Promotion Warning */}
                {stageIndex === stages.length - 2 && (
                  <div className="mt-3 pl-11 flex items-center gap-2 text-xs text-state-warning">
                    <AlertTriangle className="h-4 w-4" />
                    <span>Production deployment requires approval</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
