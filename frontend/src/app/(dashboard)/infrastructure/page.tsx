'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Cloud, Database, Globe, Container, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface ComponentHealth {
  status: string;
  message?: string;
}

interface HealthResponse {
  status: string;
  version: string;
  uptime_seconds: number;
  components: Record<string, ComponentHealth>;
}

const ICON_MAP: Record<string, React.ElementType> = {
  database: Database,
  redis: Cloud,
  ollama: Container,
  default: Globe,
};

export default function InfrastructurePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('aifactory_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE}/health`, { headers, credentials: 'include' });
      if (res.ok) setHealth(await res.json());
    } catch {
      // keep stale
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const components = health?.components
    ? Object.entries(health.components).map(([name, c]) => ({
        id: name,
        name: name.charAt(0).toUpperCase() + name.slice(1),
        status: c.status,
        message: c.message,
        icon: ICON_MAP[name.toLowerCase()] ?? ICON_MAP.default,
      }))
    : [];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Infrastructure</h1>
          <p className="text-text-secondary">Live status of all platform services</p>
        </div>
        <Button onClick={fetchData} disabled={loading} className="bg-state-running hover:bg-state-running/90">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Overall status banner */}
      {health && (
        <div className={`flex items-center gap-3 p-4 rounded-lg border ${
          health.status === 'healthy' ? 'bg-state-success-dim border-state-success/30' : 'bg-state-warning-dim border-state-warning/30'
        }`}>
          {health.status === 'healthy'
            ? <CheckCircle2 className="h-5 w-5 text-state-success" />
            : <AlertCircle className="h-5 w-5 text-state-warning" />}
          <span className="font-medium text-text-primary capitalize">{health.status}</span>
          <span className="text-text-secondary text-sm">— v{health.version}</span>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {components.map((c) => {
          const isHealthy = c.status === 'healthy' || c.status === 'connected';
          return (
            <Card key={c.id} className="border-border-default bg-bg-base/50">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="rounded-lg bg-state-running-dim p-3">
                    <c.icon className="h-6 w-6 text-state-running" />
                  </div>
                  <Badge
                    variant="secondary"
                    className={isHealthy ? 'bg-state-success-dim text-state-success' : 'bg-state-error-dim text-state-error'}
                  >
                    {c.status}
                  </Badge>
                </div>
                <h3 className="mt-4 font-semibold text-text-primary">{c.name}</h3>
                {c.message && <p className="text-xs text-text-tertiary mt-1 truncate">{c.message}</p>}
              </CardContent>
            </Card>
          );
        })}
        {components.length === 0 && loading && (
          <p className="text-text-secondary col-span-4 text-center py-8">Loading service status…</p>
        )}
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary">Docker Compose Services</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg bg-bg-code p-4 font-mono text-sm text-text-secondary overflow-auto">
            <pre>{`services: backend · frontend · nginx · postgres · redis · ollama
network:  ai-factory (bridge)
volumes:  backend_data · ollama_data · postgres_data · redis_data`}</pre>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
