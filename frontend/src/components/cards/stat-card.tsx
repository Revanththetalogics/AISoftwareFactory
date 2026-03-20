'use client';

import { memo, type ReactNode } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { cardVariants, type CardVariants } from '@/lib/variants';

interface StatCardProps extends CardVariants {
  title: string;
  value: string | number;
  description?: string;
  icon?: ReactNode;
  trend?: {
    value: number;
    label: string;
    isPositive: boolean;
  };
  className?: string;
}

export const StatCard = memo(function StatCard({
  title,
  value,
  description,
  icon,
  trend,
  variant = 'default',
  className,
}: StatCardProps) {
  return (
    <Card className={cn(cardVariants({ variant }), className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-400">
          {title}
        </CardTitle>
        {icon && (
          <div className={cn(
            'rounded-lg p-2',
            trend?.isPositive ? 'bg-emerald-500/10' : 'bg-violet-500/10'
          )}>
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-slate-100">
          {value}
        </div>
        {description && (
          <p className="text-xs text-slate-500">{description}</p>
        )}
        {trend && (
          <div className="mt-2 flex items-center gap-2">
            <span className={cn(
              'text-xs font-medium',
              trend.isPositive ? 'text-emerald-400' : 'text-red-400'
            )}>
              {trend.isPositive ? '+' : '-'}{Math.abs(trend.value)}%
            </span>
            <span className="text-xs text-slate-500">{trend.label}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
});
