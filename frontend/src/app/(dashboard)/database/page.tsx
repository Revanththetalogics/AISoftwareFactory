'use client';

import { motion } from 'framer-motion';
import { Database, Table, Rows3, Activity, HardDrive } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

const dbStats = {
  tables: 12,
  records: 15420,
  size: '45.2 MB',
  connections: 8,
  uptime: '99.9%',
};

const tables = [
  { name: 'projects', records: 45, size: '2.1 MB' },
  { name: 'workflows', records: 128, size: '4.5 MB' },
  { name: 'agents', records: 24, size: '890 KB' },
  { name: 'users', records: 12, size: '256 KB' },
];

export default function DatabasePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Database</h1>
          <p className="text-slate-400">Manage database schema and monitor performance</p>
        </div>
        <Button className="bg-cyan-500 hover:bg-cyan-600">
          <Activity className="mr-2 h-4 w-4" />
          Run Migration
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-cyan-500/10 p-3 w-fit">
              <Table className="h-6 w-6 text-cyan-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">Tables</h3>
            <p className="text-2xl font-bold text-slate-200">{dbStats.tables}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-cyan-500/10 p-3 w-fit">
              <Rows3 className="h-6 w-6 text-cyan-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">Records</h3>
            <p className="text-2xl font-bold text-slate-200">{dbStats.records.toLocaleString()}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-cyan-500/10 p-3 w-fit">
              <HardDrive className="h-6 w-6 text-cyan-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">Size</h3>
            <p className="text-2xl font-bold text-slate-200">{dbStats.size}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-6">
            <div className="rounded-lg bg-cyan-500/10 p-3 w-fit">
              <Activity className="h-6 w-6 text-cyan-400" />
            </div>
            <h3 className="mt-4 font-semibold text-slate-100">Uptime</h3>
            <p className="text-2xl font-bold text-emerald-400">{dbStats.uptime}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="text-slate-100">Database Tables</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tables.map((table) => (
              <div
                key={table.name}
                className="flex items-center justify-between p-4 rounded-lg bg-slate-800/30"
              >
                <div className="flex items-center gap-3">
                  <Database className="h-5 w-5 text-cyan-400" />
                  <span className="font-medium text-slate-200">{table.name}</span>
                </div>
                <div className="flex items-center gap-6 text-sm text-slate-400">
                  <span>{table.records} records</span>
                  <span>{table.size}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
