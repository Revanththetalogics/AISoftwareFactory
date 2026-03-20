'use client';

import { motion } from 'framer-motion';
import { LineChart, Activity, Cpu, MemoryStick, Network, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const metrics = [
  { name: 'CPU Usage', value: 45, max: 100, unit: '%', icon: Cpu },
  { name: 'Memory', value: 6.2, max: 16, unit: 'GB', icon: MemoryStick },
  { name: 'Network', value: 125, max: 1000, unit: 'Mbps', icon: Network },
  { name: 'Requests/min', value: 1250, max: 5000, unit: 'req', icon: Activity },
];

const alerts = [
  { id: '1', severity: 'warning', message: 'High memory usage on agent-001', time: '5 min ago' },
  { id: '2', severity: 'info', message: 'Deployment completed successfully', time: '15 min ago' },
];

export default function MonitoringPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Monitoring</h1>
          <p className="text-text-secondary">Real-time system metrics and alerts</p>
        </div>
        <Button className="bg-rose-500 hover:bg-rose-600">
          <LineChart className="mr-2 h-4 w-4" />
          View Metrics
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.name} className="border-border-default bg-bg-base/50">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-rose-500/10 p-3">
                  <metric.icon className="h-6 w-6 text-rose-400" />
                </div>
                <span className="text-2xl font-bold text-text-primary">
                  {metric.value}{metric.unit}
                </span>
              </div>
              <h3 className="mt-4 font-semibold text-text-primary">{metric.name}</h3>
              <div className="mt-2 h-2 rounded-full bg-bg-hover">
                <div
                  className="h-full rounded-full bg-rose-500"
                  style={{ width: `${(metric.value / metric.max) * 100}%` }}
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary">Recent Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center gap-3 p-4 rounded-lg bg-bg-hover/30"
              >
                <AlertTriangle className={`h-5 w-5 ${
                  alert.severity === 'warning' ? 'text-state-warning' : 'text-state-info'
                }`} />
                <div className="flex-1">
                  <p className="text-text-primary">{alert.message}</p>
                  <p className="text-sm text-text-tertiary">{alert.time}</p>
                </div>
                <Badge
                  variant="outline"
                  className={
                    alert.severity === 'warning'
                      ? 'bg-state-warning-dim text-state-warning'
                      : 'bg-state-info-dim text-state-info'
                  }
                >
                  {alert.severity}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
