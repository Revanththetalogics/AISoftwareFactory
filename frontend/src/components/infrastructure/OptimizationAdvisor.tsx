'use client';

import { useState } from 'react';
import { 
  Lightbulb, 
  TrendingDown, 
  TrendingUp, 
  Zap, 
  Server, 
  Database,
  Globe,
  CheckCircle2,
  ArrowRight,
  Loader2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

interface Optimization {
  id: string;
  category: 'cost' | 'performance' | 'reliability';
  title: string;
  description: string;
  impact: {
    cost?: number;
    performance?: number;
  };
  effort: 'low' | 'medium' | 'high';
  autoFixable: boolean;
  icon: React.ElementType;
}

const optimizations: Optimization[] = [
  {
    id: '1',
    category: 'cost',
    title: 'Downsize Compute Resources',
    description: 'CPU avg: 23%, Memory avg: 31% - Current instance is over-provisioned',
    impact: { cost: 45 },
    effort: 'low',
    autoFixable: true,
    icon: Server,
  },
  {
    id: '2',
    category: 'performance',
    title: 'Add Redis Caching Layer',
    description: '147 repeated database queries detected in the last hour',
    impact: { performance: 40, cost: 15 },
    effort: 'medium',
    autoFixable: false,
    icon: Database,
  },
  {
    id: '3',
    category: 'cost',
    title: 'Enable CDN for Static Assets',
    description: '245MB of static assets served directly from origin',
    impact: { cost: 25, performance: 30 },
    effort: 'low',
    autoFixable: true,
    icon: Globe,
  },
  {
    id: '4',
    category: 'reliability',
    title: 'Add Database Connection Pooling',
    description: 'Connection spikes detected during peak hours',
    impact: { performance: 20 },
    effort: 'medium',
    autoFixable: false,
    icon: Database,
  },
  {
    id: '5',
    category: 'performance',
    title: 'Optimize API Response Times',
    description: '3 endpoints averaging >500ms response time',
    impact: { performance: 35 },
    effort: 'high',
    autoFixable: false,
    icon: Zap,
  },
];

const categoryConfig = {
  cost: { color: 'text-state-success', bgColor: 'bg-state-success-dim', label: 'Cost' },
  performance: { color: 'text-state-queued', bgColor: 'bg-state-queued-dim', label: 'Performance' },
  reliability: { color: 'text-state-warning', bgColor: 'bg-state-warning-dim', label: 'Reliability' },
};

const effortConfig = {
  low: { color: 'text-state-success', label: 'Low Effort' },
  medium: { color: 'text-state-warning', label: 'Medium Effort' },
  high: { color: 'text-state-error', label: 'High Effort' },
};

interface OptimizationCardProps {
  optimization: Optimization;
  onApply: () => void;
}

function OptimizationCard({ optimization, onApply }: OptimizationCardProps) {
  const [isApplying, setIsApplying] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const Icon = optimization.icon;
  const category = categoryConfig[optimization.category];
  const effort = effortConfig[optimization.effort];

  const handleApply = async () => {
    setIsApplying(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsApplying(false);
    setIsApplied(true);
    onApply();
  };

  return (
    <div className={cn(
      'rounded-lg border p-4 transition-all',
      isApplied ? 'bg-state-success-dim/30 border-state-success/30' : 'bg-bg-panel border-border-default/50 hover:border-border-hover'
    )}>
      <div className="flex items-start gap-3">
        <div className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-lg', category.bgColor)}>
          <Icon className={cn('h-5 w-5', category.color)} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-medium text-text-primary">{optimization.title}</h4>
            <Badge variant="outline" className={cn('text-xs', category.color)}>
              {category.label}
            </Badge>
            {optimization.autoFixable && (
              <Badge variant="outline" className="text-xs text-state-success bg-state-success-dim">
                Auto-fix
              </Badge>
            )}
          </div>
          
          <p className="text-sm text-text-secondary mt-1">{optimization.description}</p>
          
          {/* Impact */}
          <div className="flex items-center gap-4 mt-3">
            {optimization.impact.cost && (
              <div className="flex items-center gap-1 text-sm">
                <TrendingDown className="h-4 w-4 text-state-success" />
                <span className="text-state-success font-medium">-${optimization.impact.cost}/mo</span>
              </div>
            )}
            {optimization.impact.performance && (
              <div className="flex items-center gap-1 text-sm">
                <TrendingUp className="h-4 w-4 text-state-queued" />
                <span className="text-state-queued font-medium">+{optimization.impact.performance}% faster</span>
              </div>
            )}
            <span className={cn('text-xs', effort.color)}>{effort.label}</span>
          </div>
        </div>

        {/* Action Button */}
        <div className="shrink-0">
          {isApplied ? (
            <div className="flex items-center gap-1 text-state-success">
              <CheckCircle2 className="h-5 w-5" />
              <span className="text-sm">Applied</span>
            </div>
          ) : (
            <Button
              size="sm"
              onClick={handleApply}
              disabled={isApplying || !optimization.autoFixable}
              variant={optimization.autoFixable ? 'default' : 'outline'}
            >
              {isApplying ? (
                <>
                  <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                  Applying...
                </>
              ) : optimization.autoFixable ? (
                <>
                  Apply
                  <ArrowRight className="ml-2 h-3 w-3" />
                </>
              ) : (
                'View Guide'
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

interface OptimizationAdvisorProps {
  projectId?: string;
  className?: string;
}

export function OptimizationAdvisor({ projectId, className }: OptimizationAdvisorProps) {
  const [appliedCount, setAppliedCount] = useState(0);
  const [totalSavings, setTotalSavings] = useState(0);

  const handleApply = (optimization: Optimization) => {
    setAppliedCount(c => c + 1);
    if (optimization.impact.cost) {
      setTotalSavings(s => s + optimization.impact.cost!);
    }
    toast.success(`Applied: ${optimization.title}`);
  };

  const totalPotentialSavings = optimizations.reduce((sum, opt) => 
    sum + (opt.impact.cost || 0), 0
  );

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-state-warning" />
              Optimization Advisor
            </CardTitle>
            <p className="text-sm text-text-secondary">
              AI-powered recommendations to improve your application
            </p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-state-success">${totalSavings}</span>
            <p className="text-xs text-text-tertiary">saved/month</p>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mt-4 p-3 rounded-lg bg-bg-base/50">
          <div className="text-center">
            <div className="text-lg font-semibold text-text-primary">{optimizations.length}</div>
            <div className="text-xs text-text-secondary">Recommendations</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-state-success">${totalPotentialSavings}</div>
            <div className="text-xs text-text-secondary">Potential Savings</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-state-queued">{appliedCount}</div>
            <div className="text-xs text-text-secondary">Applied</div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {optimizations.map((optimization) => (
          <OptimizationCard
            key={optimization.id}
            optimization={optimization}
            onApply={() => handleApply(optimization)}
          />
        ))}
      </CardContent>
    </Card>
  );
}
