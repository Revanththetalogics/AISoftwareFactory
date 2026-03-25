'use client';

import { useState, useMemo } from 'react';
import { DollarSign, Server, Database, Globe, Zap, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';

interface ServiceCost {
  id: string;
  name: string;
  icon: React.ElementType;
  baseCost: number;
  unit: string;
  description: string;
  tiers: {
    name: string;
    users: number;
    multiplier: number;
  }[];
}

const services: ServiceCost[] = [
  {
    id: 'compute',
    name: 'Compute (Vercel/Railway)',
    icon: Server,
    baseCost: 20,
    unit: '/month',
    description: 'Frontend hosting and serverless functions',
    tiers: [
      { name: 'Starter', users: 100, multiplier: 1 },
      { name: 'Pro', users: 1000, multiplier: 2.5 },
      { name: 'Scale', users: 10000, multiplier: 6 },
    ],
  },
  {
    id: 'database',
    name: 'Database (Supabase)',
    icon: Database,
    baseCost: 25,
    unit: '/month',
    description: 'PostgreSQL database and authentication',
    tiers: [
      { name: 'Free', users: 500, multiplier: 0 },
      { name: 'Pro', users: 100000, multiplier: 1 },
      { name: 'Team', users: 1000000, multiplier: 3 },
    ],
  },
  {
    id: 'cdn',
    name: 'CDN & Storage',
    icon: Globe,
    baseCost: 5,
    unit: '/month',
    description: 'Asset delivery and file storage',
    tiers: [
      { name: 'Basic', users: 1000, multiplier: 1 },
      { name: 'Standard', users: 10000, multiplier: 2 },
      { name: 'Premium', users: 100000, multiplier: 5 },
    ],
  },
  {
    id: 'ai',
    name: 'AI/LLM API',
    icon: Zap,
    baseCost: 0,
    unit: '/month',
    description: 'OpenAI/Anthropic API calls',
    tiers: [
      { name: 'Low', users: 100, multiplier: 50 },
      { name: 'Medium', users: 1000, multiplier: 200 },
      { name: 'High', users: 10000, multiplier: 800 },
    ],
  },
];

interface CostEstimatorProps {
  className?: string;
}

export function CostEstimator({ className }: CostEstimatorProps) {
  const [userCount, setUserCount] = useState(1000);

  const estimates = useMemo(() => {
    return services.map((service) => {
      const tier = service.tiers.find((t, i) => {
        const nextTier = service.tiers[i + 1];
        return userCount <= t.users || (nextTier && userCount < nextTier.users);
      }) || service.tiers[service.tiers.length - 1];

      const cost = service.baseCost * tier.multiplier + 
        (service.id === 'ai' ? tier.multiplier : 0);

      return {
        ...service,
        selectedTier: tier.name,
        estimatedCost: cost,
      };
    });
  }, [userCount]);

  const totalCost = estimates.reduce((sum, e) => sum + e.estimatedCost, 0);

  const getUserLabel = (count: number) => {
    if (count < 1000) return `${count} users`;
    if (count < 1000000) return `${(count / 1000).toFixed(1)}k users`;
    return `${(count / 1000000).toFixed(1)}M users`;
  };

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-state-success" />
              Cost Estimator
            </CardTitle>
            <p className="text-sm text-text-secondary">
              Estimate monthly infrastructure costs
            </p>
          </div>
          <Badge variant="outline" className="text-lg font-semibold">
            ${totalCost.toFixed(0)}/mo
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* User Count Slider */}
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Expected Users</span>
            <span className="font-medium text-text-primary">{getUserLabel(userCount)}</span>
          </div>
          <input
            type="range"
            value={userCount}
            onChange={(e) => setUserCount(Number(e.target.value))}
            min={100}
            max={100000}
            step={100}
            className="w-full h-2 bg-bg-base rounded-lg appearance-none cursor-pointer accent-state-queued"
          />
          <div className="flex justify-between text-xs text-text-tertiary">
            <span>100</span>
            <span>1k</span>
            <span>10k</span>
            <span>100k</span>
          </div>
        </div>

        {/* Cost Breakdown */}
        <div className="space-y-3">
          {estimates.map((service) => {
            const Icon = service.icon;
            return (
              <div
                key={service.id}
                className="flex items-center justify-between p-3 rounded-lg bg-bg-base/50"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-bg-panel">
                    <Icon className="h-5 w-5 text-text-secondary" />
                  </div>
                  <div>
                    <div className="font-medium text-text-primary">{service.name}</div>
                    <div className="text-xs text-text-secondary">{service.description}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-text-primary">
                    ${service.estimatedCost}
                    <span className="text-xs text-text-tertiary">/mo</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {service.selectedTier}
                  </Badge>
                </div>
              </div>
            );
          })}
        </div>

        {/* Total */}
        <div className="pt-4 border-t border-border-default">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <Info className="h-4 w-4" />
              <span>Estimated at {getUserLabel(userCount)} MAU</span>
            </div>
            <div className="text-right">
              <div className="text-sm text-text-secondary">Total Monthly Cost</div>
              <div className="text-2xl font-bold text-state-success">
                ${totalCost.toFixed(0)}
                <span className="text-sm font-normal text-text-secondary">/month</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scaling Note */}
        <div className="p-3 rounded-lg bg-state-queued-dim text-sm">
          <p className="text-text-secondary">
            <span className="font-medium text-text-primary">Scaling tip:</span> Costs scale 
            with usage. At 10k users, expect ~${(totalCost * 3).toFixed(0)}/mo. 
            Consider annual billing for 20% savings.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
