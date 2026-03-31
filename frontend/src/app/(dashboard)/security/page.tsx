'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Lock, Key, AlertOctagon, CheckCircle, FileWarning, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface Bug {
  id: string;
  description: string;
  severity: string;
  category?: string;
  file_path?: string;
  confidence?: number;
}

interface DetectBugsResponse {
  bugs_found: number;
  by_severity: Record<string, number>;
  bugs: Bug[];
}

export default function SecurityPage() {
  const [scanResult, setScanResult] = useState<DetectBugsResponse | null>(null);
  const [scanning, setScanning] = useState(false);
  const [lastScan, setLastScan] = useState<string | null>(null);

  const runScan = async () => {
    setScanning(true);
    try {
      const token = localStorage.getItem('aifactory_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE}/testing/detect-bugs`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
          directory: 'backend',
          use_static_analysis: true,
          use_llm_review: false,
          min_confidence: 0.6,
        }),
      });

      if (res.ok) {
        const data: DetectBugsResponse = await res.json();
        setScanResult(data);
        setLastScan(new Date().toLocaleTimeString());
      }
    } catch {
      // keep previous result
    } finally {
      setScanning(false);
    }
  };

  useEffect(() => { runScan(); }, []);

  const bySeverity = scanResult?.by_severity ?? {};
  const stats = {
    high: (bySeverity.high ?? 0) + (bySeverity.critical ?? 0),
    medium: bySeverity.medium ?? 0,
    low: bySeverity.low ?? 0,
    total: scanResult?.bugs_found ?? 0,
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Security</h1>
          <p className="text-text-secondary">
            Security scanning and vulnerability management
            {lastScan && <span className="ml-2 text-xs text-text-tertiary">Last scan: {lastScan}</span>}
          </p>
        </div>
        <Button onClick={runScan} disabled={scanning} className="bg-state-error hover:bg-state-error/90">
          <RefreshCw className={`mr-2 h-4 w-4 ${scanning ? 'animate-spin' : ''}`} />
          {scanning ? 'Scanning…' : 'Run Security Scan'}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-error-dim p-3 w-fit">
              <AlertOctagon className="h-6 w-6 text-state-error" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">High / Critical</h3>
            <p className="text-2xl font-bold text-state-error">{stats.high}</p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-warning-dim p-3 w-fit">
              <FileWarning className="h-6 w-6 text-state-warning" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Medium</h3>
            <p className="text-2xl font-bold text-state-warning">{stats.medium}</p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-success-dim p-3 w-fit">
              <Key className="h-6 w-6 text-state-success" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Low</h3>
            <p className="text-2xl font-bold text-state-success">{stats.low}</p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-running-dim p-3 w-fit">
              <Lock className="h-6 w-6 text-state-running" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Total Found</h3>
            <p className="text-2xl font-bold text-text-primary">{stats.total}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary flex items-center gap-2">
            <ShieldCheck className="h-5 w-5" />
            Detected Issues
          </CardTitle>
        </CardHeader>
        <CardContent>
          {scanning && <p className="text-text-secondary text-sm">Running scan…</p>}
          {!scanning && (!scanResult || scanResult.bugs_found === 0) && (
            <p className="flex items-center gap-2 text-state-success">
              <CheckCircle className="h-4 w-4" /> No issues detected.
            </p>
          )}
          <div className="space-y-3">
            {(scanResult?.bugs ?? []).map((bug, i) => (
              <div key={i} className="flex items-start gap-3 p-4 rounded-lg bg-bg-hover/30">
                <FileWarning className={`h-5 w-5 mt-0.5 flex-shrink-0 ${
                  bug.severity === 'high' || bug.severity === 'critical' ? 'text-state-error'
                    : bug.severity === 'medium' ? 'text-state-warning'
                    : 'text-state-running'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-text-primary text-sm">{bug.description}</p>
                  {bug.file_path && <p className="text-xs text-text-tertiary truncate">{bug.file_path}</p>}
                </div>
                <Badge
                  variant="outline"
                  className={
                    bug.severity === 'high' || bug.severity === 'critical'
                      ? 'bg-state-error-dim text-state-error'
                      : bug.severity === 'medium'
                      ? 'bg-state-warning-dim text-state-warning'
                      : 'bg-state-running-dim text-state-running'
                  }
                >
                  {bug.severity}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
