'use client';

import { motion } from 'framer-motion';
import { Eye, Camera, GitCompare, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const visualTests = [
  { id: '1', name: 'Homepage', status: 'passed', diff: '0%', viewport: '1920x1080' },
  { id: '2', name: 'Login Page', status: 'failed', diff: '12.5%', viewport: '1920x1080' },
  { id: '3', name: 'Dashboard', status: 'passed', diff: '0%', viewport: '1440x900' },
];

export default function VisualTestingPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Visual Regression</h1>
          <p className="text-slate-400">AI-powered visual testing and comparison</p>
        </div>
        <Button className="bg-amber-500 hover:bg-amber-600">
          <Camera className="mr-2 h-4 w-4" />
          Run Visual Tests
        </Button>
      </div>

      <div className="grid gap-4">
        {visualTests.map((test) => (
          <Card key={test.id} className="border-slate-800 bg-slate-900/50">
            <CardContent className="flex items-center justify-between p-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-amber-500/10 p-3">
                  <Eye className="h-6 w-6 text-amber-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-100">{test.name}</h3>
                  <p className="text-sm text-slate-400">{test.viewport}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Badge
                  variant={test.status === 'passed' ? 'default' : 'destructive'}
                  className={
                    test.status === 'passed'
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : 'bg-red-500/10 text-red-400'
                  }
                >
                  {test.status === 'passed' ? (
                    <CheckCircle className="mr-1 h-3 w-3" />
                  ) : (
                    <AlertCircle className="mr-1 h-3 w-3" />
                  )}
                  {test.status}
                </Badge>
                {test.diff !== '0%' && (
                  <span className="text-sm text-red-400">{test.diff} diff</span>
                )}
                <Button variant="ghost" size="sm">
                  <GitCompare className="mr-1 h-4 w-4" />
                  Compare
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
}
