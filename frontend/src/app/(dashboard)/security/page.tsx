'use client';

import { motion } from 'framer-motion';
import { ShieldCheck, Lock, Key, AlertOctagon, CheckCircle, FileWarning } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const securityStats = {
  vulnerabilities: 3,
  secrets: 0,
  compliance: '95%',
  lastScan: '2 hours ago',
};

const vulnerabilities = [
  { id: '1', severity: 'high', title: 'Outdated dependency in requirements.txt', file: 'backend/requirements.txt' },
  { id: '2', severity: 'medium', title: 'Missing rate limiting on API endpoint', file: 'backend/api/routes/auth.py' },
  { id: '3', severity: 'low', title: 'Debug mode enabled in production', file: 'backend/core/config.py' },
];

export default function SecurityPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Security</h1>
          <p className="text-text-secondary">Security scanning and vulnerability management</p>
        </div>
        <Button className="bg-rose-500 hover:bg-rose-600">
          <ShieldCheck className="mr-2 h-4 w-4" />
          Run Security Scan
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-rose-500/10 p-3 w-fit">
              <AlertOctagon className="h-6 w-6 text-rose-400" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Vulnerabilities</h3>
            <p className="text-2xl font-bold text-rose-400">{securityStats.vulnerabilities}</p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-success-dim p-3 w-fit">
              <Key className="h-6 w-6 text-state-success" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Secrets</h3>
            <p className="text-2xl font-bold text-state-success">{securityStats.secrets}</p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-info-dim p-3 w-fit">
              <CheckCircle className="h-6 w-6 text-state-info" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Compliance</h3>
            <p className="text-2xl font-bold text-state-info">{securityStats.compliance}</p>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-state-warning-dim p-3 w-fit">
              <Lock className="h-6 w-6 text-state-warning" />
            </div>
            <h3 className="mt-4 font-semibold text-text-primary">Last Scan</h3>
            <p className="text-lg font-bold text-text-primary">{securityStats.lastScan}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary">Detected Vulnerabilities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {vulnerabilities.map((vuln) => (
              <div
                key={vuln.id}
                className="flex items-center gap-3 p-4 rounded-lg bg-bg-hover/30"
              >
                <FileWarning className={`h-5 w-5 ${
                  vuln.severity === 'high' ? 'text-rose-400' :
                  vuln.severity === 'medium' ? 'text-state-warning' : 'text-state-info'
                }`} />
                <div className="flex-1">
                  <p className="text-text-primary">{vuln.title}</p>
                  <p className="text-sm text-text-tertiary">{vuln.file}</p>
                </div>
                <Badge
                  variant="outline"
                  className={
                    vuln.severity === 'high' ? 'bg-rose-500/10 text-rose-400' :
                    vuln.severity === 'medium' ? 'bg-state-warning-dim text-state-warning' :
                    'bg-state-info-dim text-state-info'
                  }
                >
                  {vuln.severity}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
