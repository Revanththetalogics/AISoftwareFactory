'use client';

import { motion } from 'framer-motion';
import { Zap, Timer, Gauge, TrendingUp, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

const perfMetrics = {
  avgResponseTime: '124ms',
  throughput: '1,250 req/s',
  errorRate: '0.02%',
  cpuEfficiency: '78%',
};

const benchmarks = [
  { name: 'API Response', current: 124, target: 100, unit: 'ms' },
  { name: 'Database Query', current: 45, target: 50, unit: 'ms' },
  { name: 'Page Load', current: 1.2, target: 1.0, unit: 's' },
  { name: 'Test Execution', current: 45, target: 30, unit: 's' },
];

export default function PerformancePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Performance</h1>
          <p className="text-slate-400">Performance monitoring and optimization</p>
        </div>
        <Button className="bg-rose-500 hover:bg-rose-600">
          <Zap className="mr-2 h-4 w-4" />
          Run Benchmarks
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-rose-500/10 p-3 w-fit">
              <Timer className="h-6 w-6 text-rose-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">Avg Response</h3>
            <p className="text-2xl font-bold text-slate-200">{perfMetrics.avgResponseTime}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-emerald-500/10 p-3 w-fit">
              <Gauge className="h-6 w-6 text-emerald-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">Throughput</h3>
            <p className="text-2xl font-bold text-slate-200">{perfMetrics.throughput}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-amber-500/10 p-3 w-fit">
              <AlertCircle className="h-6 w-6 text-amber-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">Error Rate</h3>
            <p className="text-2xl font-bold text-emerald-400">{perfMetrics.errorRate}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-blue-500/10 p-3 w-fit">
              <TrendingUp className="h-6 w-6 text-blue-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">CPU Efficiency</h3>
            <p className="text-2xl font-bold text-slate-200">{perfMetrics.cpuEfficiency}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="text-slate-100">Performance Benchmarks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {benchmarks.map((bench) => (
              <div key={bench.name}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-200">{bench.name}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-slate-400">Target: {bench.target}{bench.unit}</span>
                    <Badge
                      variant={bench.current <= bench.target ? 'default' : 'secondary'}
                      className={
                        bench.current <= bench.target
                          ? 'bg-emerald-500/10 text-emerald-400'
                          : 'bg-amber-500/10 text-amber-400'
                      }
                    >
                      {bench.current}{bench.unit}
                    </Badge>
                  </div>
                </div>
                <Progress
                  value={(bench.current / bench.target) * 100}
                  className="h-2 bg-slate-800"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
