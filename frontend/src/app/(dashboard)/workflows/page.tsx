'use client';

import { motion } from 'framer-motion';
import { Workflow, GitBranch, Play, Pause, Settings } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const workflows = [
  { id: '1', name: 'Software Development Lifecycle', status: 'active', stages: 6, runs: 12 },
  { id: '2', name: 'Code Review Pipeline', status: 'idle', stages: 4, runs: 45 },
  { id: '3', name: 'Deployment Automation', status: 'active', stages: 5, runs: 8 },
];

export default function WorkflowsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Workflows</h1>
          <p className="text-slate-400">Manage AI-powered development workflows</p>
        </div>
        <Button className="bg-violet-500 hover:bg-violet-600">
          <Workflow className="mr-2 h-4 w-4" />
          New Workflow
        </Button>
      </div>

      <div className="grid gap-4">
        {workflows.map((workflow) => (
          <Card key={workflow.id} className="border-slate-800 bg-slate-900/50">
            <CardContent className="flex items-center justify-between p-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-blue-500/10 p-3">
                  <GitBranch className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-100">{workflow.name}</h3>
                  <p className="text-sm text-slate-400">{workflow.stages} stages • {workflow.runs} runs</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={workflow.status === 'active' ? 'default' : 'secondary'}>
                  {workflow.status}
                </Badge>
                <Button variant="ghost" size="icon">
                  {workflow.status === 'active' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
                <Button variant="ghost" size="icon">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
}
