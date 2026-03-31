'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Zap, Timer, Gauge, TrendingUp, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface EndpointStat {
  endpoint: string;
  method: string;
  avg_latency_ms: number;
  request_count: number;
  error_rate: number;
}

interface DashboardMetrics {
  system: { cpu_usage: number; memory_usage: number };
  application: { average_response_time_ms: number; requests_per_second: number; error_percentage: number };
}

export default function PerformancePage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [endpoints, setEndpoints] = useState<EndpointStat[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('aifactory_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const [dashRes, endpointsRes] = await Promise.all([
        fetch(`${API_BASE}/monitoring/metrics/dashboard`, { headers, credentials: 'include' }),
        fetch(`${API_BASE}/monitoring/performance/top-endpoints?limit=8`, { headers, credentials: 'include' }),
      ]);

      if (dashRes.ok) {
        const body = await dashRes.json();
        setMetrics(body.data ?? null);
      }
      if (endpointsRes.ok) {
        const body = await endpointsRes.json();
        setEndpoints(body.data?.endpoints ?? []);
      }
    } catch {
      // keep stale
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const app = metrics?.application;

  const statCards = [
    { label: 'Avg Response', value: app ? `${app.average_response_time_ms.toFixed(0)}ms` : '—', icon: Timer },
    { label: 'Requests/s', value: app ? `${app.requests_per_second.toFixed(1)}` : '—', icon: Gauge },
    { label: 'Error Rate', value: app ? `${app.error_percentage.toFixed(2)}%` : '—', icon: TrendingUp },
    { label: 'CPU', value: metrics ? `${metrics.system.cpu_usage.toFixed(1)}%` : '—', icon: Zap },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Performance</h1>
          <p className="text-text-secondary">Real-time API and system performance metrics</p>
        </div>
        <Button onClick={fetchData} disabled={loading} className="bg-state-running hover:bg-state-running/90">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((s) => (
          <Card key={s.label} className="border-border-default bg-bg-base/50">
            <CardContent className="p-6">
              <div className="rounded-lg bg-state-running-dim p-3 w-fit">
                <s.icon className="h-6 w-6 text-state-running" />
              </div>
              <h3 className="mt-4 font-semibold text-text-primary">{s.label}</h3>
              <p className="text-2xl font-bold text-text-primary">{s.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary">Top API Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          {endpoints.length === 0 && <p className="text-text-secondary text-sm">No endpoint data available.</p>}
          <div className="space-y-4">
            {endpoints.map((ep, i) => {
              const pct = Math.min((ep.avg_latency_ms / 300) * 100, 100);
              return (
                <div key={i} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs font-mono">{ep.method}</Badge>
                      <span className="text-text-primary font-mono text-xs">{ep.endpoint}</span>
                    </div>
                    <div className="flex items-center gap-4 text-text-secondary text-xs">
                      <span>{ep.avg_latency_ms.toFixed(1)}ms</span>
                      <span>{ep.request_count.toLocaleString()} req</span>
                      <span className={ep.error_rate > 0.05 ? 'text-state-error' : 'text-state-success'}>
                        {(ep.error_rate * 100).toFixed(1)}% err
                      </span>
                    </div>
                  </div>
                  <Progress value={pct} className="h-1.5" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
