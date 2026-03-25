'use client';

import { useState } from 'react';
import { 
  Monitor, 
  Smartphone, 
  Tablet,
  RefreshCw,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Eye,
  GitCommit
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

type DeviceType = 'desktop' | 'tablet' | 'mobile';

interface DeploymentPreviewProps {
  projectId?: string;
  deploymentUrl?: string;
  className?: string;
}

const deviceConfigs: Record<DeviceType, { width: number; height: number; label: string; icon: React.ElementType }> = {
  desktop: { width: 1200, height: 800, label: 'Desktop', icon: Monitor },
  tablet: { width: 768, height: 1024, label: 'Tablet', icon: Tablet },
  mobile: { width: 375, height: 812, label: 'Mobile', icon: Smartphone },
};

interface PreviewCheck {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  message?: string;
}

const mockChecks: PreviewCheck[] = [
  { id: '1', name: 'Build Successful', status: 'passed' },
  { id: '2', name: 'No Console Errors', status: 'passed' },
  { id: '3', name: 'Responsive Layout', status: 'passed' },
  { id: '4', name: 'API Connectivity', status: 'passed' },
  { id: '5', name: 'Performance Score', status: 'passed', message: '94/100' },
  { id: '6', name: 'SEO Check', status: 'running' },
];

export function DeploymentPreview({ 
  projectId, 
  deploymentUrl = 'https://preview-thetaai.vercel.app',
  className 
}: DeploymentPreviewProps) {
  const [activeDevice, setActiveDevice] = useState<DeviceType>('desktop');
  const [checks, setChecks] = useState<PreviewCheck[]>(mockChecks);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [scale, setScale] = useState(0.6);

  const device = deviceConfigs[activeDevice];
  const DeviceIcon = device.icon;

  const passedCount = checks.filter(c => c.status === 'passed').length;
  const totalCount = checks.length;
  const allPassed = passedCount === totalCount;

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setChecks(checks.map(c => ({ ...c, status: 'running' })));
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setChecks(checks.map(c => ({ ...c, status: 'passed' })));
    setIsRefreshing(false);
    toast.success('Preview refreshed');
  };

  const handlePromote = () => {
    toast.success('Deployment promoted to production');
  };

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary flex items-center gap-2">
              <Eye className="h-5 w-5 text-state-queued" />
              Deployment Preview
            </CardTitle>
            <p className="text-sm text-text-secondary">
              Preview and validate before production
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge 
              variant={allPassed ? 'default' : 'secondary'}
              className={allPassed ? 'bg-state-success' : ''}
            >
              {allPassed ? (
                <>
                  <CheckCircle2 className="mr-1 h-3 w-3" />
                  Ready
                </>
              ) : (
                <>
                  <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
                  Checking
                </>
              )}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Device Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1 p-1 rounded-lg bg-bg-base">
            {(Object.keys(deviceConfigs) as DeviceType[]).map((deviceType) => {
              const Icon = deviceConfigs[deviceType].icon;
              return (
                <button
                  key={deviceType}
                  onClick={() => setActiveDevice(deviceType)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors',
                    activeDevice === deviceType
                      ? 'bg-bg-panel text-text-primary'
                      : 'text-text-secondary hover:text-text-primary'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{deviceConfigs[deviceType].label}</span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setScale(s => Math.max(0.3, s - 0.1))}
            >
              -
            </Button>
            <span className="text-sm text-text-secondary w-12 text-center">
              {Math.round(scale * 100)}%
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setScale(s => Math.min(1, s + 0.1))}
            >
              +
            </Button>
          </div>
        </div>

        {/* Preview Frame */}
        <div className="relative rounded-lg border border-border-default bg-bg-base overflow-hidden">
          {/* Browser Chrome */}
          <div className="flex items-center gap-2 px-3 py-2 border-b border-border-default bg-bg-panel">
            <div className="flex items-center gap-1.5">
              <div className="h-3 w-3 rounded-full bg-state-error" />
              <div className="h-3 w-3 rounded-full bg-state-warning" />
              <div className="h-3 w-3 rounded-full bg-state-success" />
            </div>
            <div className="flex-1 mx-4">
              <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-bg-base text-xs text-text-secondary">
                <div className="w-4 h-4 rounded-full bg-state-success/20 flex items-center justify-center">
                  <div className="w-2 h-2 rounded-full bg-state-success" />
                </div>
                {deploymentUrl}
              </div>
            </div>
            <Button variant="ghost" size="sm" className="h-7 px-2">
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>

          {/* Preview Content */}
          <div className="relative overflow-auto" style={{ height: 400 }}>
            <div 
              className="origin-top-left transition-transform duration-200"
              style={{ 
                width: device.width, 
                height: device.height,
                transform: `scale(${scale})`,
              }}
            >
              {/* Placeholder for actual preview */}
              <div className="w-full h-full bg-bg-panel flex flex-col">
                {/* Mock Website Header */}
                <div className="h-16 border-b border-border-default flex items-center px-6">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-state-queued to-state-running" />
                  <div className="ml-4 flex-1">
                    <div className="h-4 w-24 rounded bg-bg-base" />
                  </div>
                  <div className="flex gap-3">
                    <div className="h-8 w-20 rounded bg-bg-base" />
                    <div className="h-8 w-20 rounded bg-state-queued" />
                  </div>
                </div>
                
                {/* Mock Hero Section */}
                <div className="flex-1 p-8 flex items-center justify-center">
                  <div className="text-center space-y-4">
                    <div className="h-12 w-64 mx-auto rounded-lg bg-bg-base" />
                    <div className="h-4 w-96 mx-auto rounded bg-bg-base" />
                    <div className="h-4 w-80 mx-auto rounded bg-bg-base" />
                    <div className="pt-4 flex gap-3 justify-center">
                      <div className="h-10 w-32 rounded bg-state-queued" />
                      <div className="h-10 w-32 rounded border border-border-default" />
                    </div>
                  </div>
                </div>

                {/* Mock Features */}
                <div className="p-8 grid grid-cols-3 gap-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="p-4 rounded-lg border border-border-default">
                      <div className="w-10 h-10 rounded-lg bg-bg-base mb-3" />
                      <div className="h-4 w-24 rounded bg-bg-base mb-2" />
                      <div className="h-3 w-full rounded bg-bg-base" />
                      <div className="h-3 w-2/3 rounded bg-bg-base mt-1" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Health Checks */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {checks.map((check) => (
            <div 
              key={check.id}
              className={cn(
                'flex items-center gap-2 p-2 rounded-lg text-sm',
                check.status === 'passed' ? 'bg-state-success-dim/30' :
                check.status === 'failed' ? 'bg-state-error-dim/30' :
                check.status === 'running' ? 'bg-state-queued-dim/30' :
                'bg-bg-base'
              )}
            >
              {check.status === 'passed' ? (
                <CheckCircle2 className="h-4 w-4 text-state-success shrink-0" />
              ) : check.status === 'failed' ? (
                <XCircle className="h-4 w-4 text-state-error shrink-0" />
              ) : check.status === 'running' ? (
                <RefreshCw className="h-4 w-4 text-state-queued animate-spin shrink-0" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-text-tertiary shrink-0" />
              )}
              <span className="text-text-secondary truncate">{check.name}</span>
              {check.message && (
                <span className="text-xs text-text-tertiary ml-auto">{check.message}</span>
              )}
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t border-border-default">
          <Button
            variant="outline"
            className="flex-1"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh Preview
              </>
            )}
          </Button>
          <Button
            className="flex-1"
            disabled={!allPassed}
            onClick={handlePromote}
          >
            <GitCommit className="mr-2 h-4 w-4" />
            Promote to Production
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
