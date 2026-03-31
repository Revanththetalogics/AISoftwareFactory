'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Database, Table, Rows3, Activity, HardDrive, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface HealthData {
  system: { cpu_percent: number; memory_percent: number; disk_percent: number; uptime_seconds: number };
  application: { active_connections: number; request_rate: number; error_rate: number; cache_hit_ratio: number };
  timestamp: string;
}

const KNOWN_TABLES = [
  { name: 'users', description: 'Authentication & profiles' },
  { name: 'projects', description: 'Software development projects' },
  { name: 'workflows', description: 'Automated workflow processes' },
  { name: 'tasks', description: 'Unit-of-work items' },
  { name: 'agents', description: 'AI agent configurations' },
  { name: 'deployments', description: 'Application deployments' },
  { name: 'custom_crews', description: 'Dynamic agent crews' },
  { name: 'audit_logs', description: 'System audit trail' },
];

function fmtUptime(seconds: number) {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  if (d > 0) return `${d}d ${h}h`;
  return `${h}h`;
}

export default function DatabasePage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [dbOnline, setDbOnline] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('aifactory_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      // Use detailed health which returns real psutil metrics
      const res = await fetch(`${API_BASE}/monitoring/health/detailed`, { headers, credentials: 'include' });
      if (res.ok) {
        const body = await res.json();
        setHealth(body.data ?? null);
        setDbOnline(body.success ?? true);
      }

      // Verify DB is up via the /health/simple endpoint
      const healthRes = await fetch(`${API_BASE}/health/simple`, { headers, credentials: 'include' });
      setDbOnline(healthRes.ok);
    } catch {
      setDbOnline(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Database</h1>
          <p className="text-text-secondary">Schema overview and server health</p>
        </div>
        <Button onClick={fetchData} disabled={loading} className="bg-state-running hover:bg-state-running/90">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-running-dim p-3 w-fit">
              <Table className="h-6 w-6 text-state-running" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Tables</h3>
            <p className="text-2xl font-bold text-text-primary">{KNOWN_TABLES.length}</p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-running-dim p-3 w-fit">
              <HardDrive className="h-6 w-6 text-state-running" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Disk Used</h3>
            <p className="text-2xl font-bold text-text-primary">
              {health ? `${health.system.disk_percent.toFixed(1)}%` : '—'}
            </p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-running-dim p-3 w-fit">
              <Rows3 className="h-6 w-6 text-state-running" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Server Uptime</h3>
            <p className="text-2xl font-bold text-text-primary">
              {health ? fmtUptime(health.system.uptime_seconds) : '—'}
            </p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className={`rounded-lg p-3 w-fit ${dbOnline ? 'bg-state-success-dim' : 'bg-state-error-dim'}`}>
              <Activity className={`h-6 w-6 ${dbOnline ? 'text-state-success' : 'text-state-error'}`} />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Status</h3>
            <Badge
              variant="outline"
              className={dbOnline ? 'bg-state-success-dim text-state-success mt-1' : 'bg-state-error-dim text-state-error mt-1'}
            >
              {dbOnline === null ? 'Checking…' : dbOnline ? 'Online' : 'Offline'}
            </Badge>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary">Database Schema</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {KNOWN_TABLES.map((table) => (
              <div key={table.name} className="flex items-center justify-between p-4 rounded-lg bg-bg-hover/30">
                <div className="flex items-center gap-3">
                  <Database className="h-5 w-5 text-state-running" />
                  <div>
                    <span className="font-medium text-text-primary">{table.name}</span>
                    <p className="text-xs text-text-tertiary">{table.description}</p>
                  </div>
                </div>
                <Badge variant="outline" className="bg-state-success-dim text-state-success text-xs">active</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
