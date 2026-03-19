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
          <h1 className="text-3xl font-bold text-slate-100">Monitoring</h1>
          <p className="text-slate-400">Real-time system metrics and alerts</p>
        </div>
        <Button className="bg-rose-500 hover:bg-rose-600">
          <LineChart className="mr-2 h-4 w-4" />
          View Metrics
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.name} className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-rose-500/10 p-3">
                  <metric.icon className="h-6 w-6 text-rose-400" />
                </div>
                <span className="text-2xl font-bold text-slate-200">
                  {metric.value}{metric.unit}
                </span>
              </div>
              <h3 className="mt-4 font-semibold text-slate-100">{metric.name}</h3>
              <div className="mt-2 h-2 rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-rose-500"
                  style={{ width: `${(metric.value / metric.max) * 100}%` }}
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-slate-800 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="text-slate-100">Recent Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center gap-3 p-4 rounded-lg bg-slate-800/30"
              >
                <AlertTriangle className={`h-5 w-5 ${
                  alert.severity === 'warning' ? 'text-amber-400' : 'text-blue-400'
                }`} />
                <div className="flex-1">
                  <p className="text-slate-200">{alert.message}</p>
                  <p className="text-sm text-slate-500">{alert.time}</p>
                </div>
                <Badge
                  variant="secondary"
                  className={
                    alert.severity === 'warning'
                      ? 'bg-amber-500/10 text-amber-400'
                      : 'bg-blue-500/10 text-blue-400'
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
