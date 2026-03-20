'use client';

import { motion } from 'framer-motion';
import { Brain, Search, Plus, FileText, Database } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const knowledgeBases = [
  { id: '1', name: 'Project Patterns', documents: 45, size: '2.3 MB', lastUpdated: '2 hours ago' },
  { id: '2', name: 'Code Standards', documents: 12, size: '890 KB', lastUpdated: '1 day ago' },
  { id: '3', name: 'API Documentation', documents: 28, size: '1.5 MB', lastUpdated: '3 days ago' },
];

export default function KnowledgePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Knowledge Base</h1>
          <p className="text-slate-400">RAG-powered knowledge management for AI agents</p>
        </div>
        <Button className="bg-violet-500 hover:bg-violet-600">
          <Plus className="mr-2 h-4 w-4" />
          Add Knowledge
        </Button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search knowledge base..."
            className="pl-10 bg-slate-900 border-slate-800"
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {knowledgeBases.map((kb) => (
          <Card key={kb.id} className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-indigo-500/10 p-3">
                  <Brain className="h-6 w-6 text-indigo-400" />
                </div>
                <Badge variant="secondary">RAG</Badge>
              </div>
              <h3 className="mt-4 font-semibold text-slate-100">{kb.name}</h3>
              <div className="mt-2 flex items-center gap-4 text-sm text-slate-400">
                <span className="flex items-center gap-1">
                  <FileText className="h-4 w-4" />
                  {kb.documents} docs
                </span>
                <span className="flex items-center gap-1">
                  <Database className="h-4 w-4" />
                  {kb.size}
                </span>
              </div>
              <p className="mt-2 text-xs text-slate-500">Updated {kb.lastUpdated}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
}
