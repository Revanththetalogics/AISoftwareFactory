'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Activity, Cpu, MemoryStick, Network, AlertTriangle, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface DashboardMetrics {
  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_io: { bytes_sent: number; bytes_recv: number };
  };
  application: {
    active_users: number;
    requests_per_second: number;
    average_response_time_ms: number;
    error_percentage: number;
  };
  timestamp: string;
}

interface AlertEntry {
  alert_name: string;
  severity: string;
  triggered_at: string;
  resolved_at: string;
  duration_seconds: number;
}

function fmtBytes(bytes: number) {
  if (bytes > 1e9) return `${(bytes / 1e9).toFixed(1)} GB`;
  if (bytes > 1e6) return `${(bytes / 1e6).toFixed(1)} MB`;
  return `${(bytes / 1e3).toFixed(1)} KB`;
}

function timeSince(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export default function MonitoringPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [alerts, setAlerts] = useState<AlertEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('aifactory_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const [metricsRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE}/monitoring/metrics/dashboard`, { headers, credentials: 'include' }),
        fetch(`${API_BASE}/monitoring/alerts/history?hours=24`, { headers, credentials: 'include' }),
      ]);

      if (metricsRes.ok) {
        const body = await metricsRes.json();
        setMetrics(body.data ?? null);
      }
      if (alertsRes.ok) {
        const body = await alertsRes.json();
        setAlerts(body.data?.alerts ?? []);
      }
    } catch {
      // silently keep stale data
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 30_000);
    return () => clearInterval(id);
  }, []);

  const sys = metrics?.system;
  const metricCards = [
    { name: 'CPU Usage', value: sys ? `${sys.cpu_usage.toFixed(1)}%` : '—', pct: sys?.cpu_usage ?? 0, icon: Cpu },
    { name: 'Memory', value: sys ? `${sys.memory_usage.toFixed(1)}%` : '—', pct: sys?.memory_usage ?? 0, icon: MemoryStick },
    { name: 'Disk Usage', value: sys ? `${sys.disk_usage.toFixed(1)}%` : '—', pct: sys?.disk_usage ?? 0, icon: LineChart },
    { name: 'Network In', value: sys ? fmtBytes(sys.network_io.bytes_recv) : '—', pct: 0, icon: Network },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Monitoring</h1>
          <p className="text-text-secondary">Real-time system metrics and alerts</p>
        </div>
        <Button onClick={fetchData} disabled={loading} className="bg-state-running hover:bg-state-running/90">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metricCards.map((m) => (
          <Card key={m.name} className="border-border-default bg-bg-base/50">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-state-running-dim p-3">
                  <m.icon className="h-6 w-6 text-state-running" />
                </div>
                <span className="text-2xl font-bold text-text-primary">{m.value}</span>
              </div>
              <h3 className="mt-4 font-semibold text-text-primary">{m.name}</h3>
              {m.pct > 0 && (
                <div className="mt-2 h-2 rounded-full bg-bg-hover">
                  <div
                    className={`h-full rounded-full transition-all ${m.pct > 80 ? 'bg-state-error' : m.pct > 60 ? 'bg-state-warning' : 'bg-state-running'}`}
                    style={{ width: `${Math.min(m.pct, 100)}%` }}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary">Recent Alerts (last 24 h)</CardTitle>
        </CardHeader>
        <CardContent>
          {alerts.length === 0 ? (
            <p className="text-text-secondary text-sm">No alerts in the last 24 hours.</p>
          ) : (
            <div className="space-y-3">
              {alerts.map((alert, i) => (
                <div key={i} className="flex items-center gap-3 p-4 rounded-lg bg-bg-hover/30">
                  <AlertTriangle className={`h-5 w-5 ${alert.severity === 'warning' ? 'text-state-warning' : 'text-state-error'}`} />
                  <div className="flex-1">
                    <p className="text-text-primary">{alert.alert_name.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-text-tertiary">{timeSince(alert.triggered_at)}</p>
                  </div>
                  <Badge
                    variant="outline"
                    className={alert.severity === 'warning' ? 'bg-state-warning-dim text-state-warning' : 'bg-state-error-dim text-state-error'}
                  >
                    {alert.severity}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
