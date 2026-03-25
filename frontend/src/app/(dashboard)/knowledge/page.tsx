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
          <h1 className="text-3xl font-bold text-text-primary">Knowledge Base</h1>
          <p className="text-text-secondary">RAG-powered knowledge management for AI agents</p>
        </div>
        <Button className="bg-state-queued hover:bg-state-queued">
          <Plus className="mr-2 h-4 w-4" />
          Add Knowledge
        </Button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary" />
          <Input
            placeholder="Search knowledge base..."
            className="pl-10 bg-bg-base border-border-default"
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {knowledgeBases.map((kb) => (
          <Card key={kb.id} className="border-border-default bg-bg-base/50">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-state-queued-dim p-3">
                  <Brain className="h-6 w-6 text-state-queued" />
                </div>
                <Badge variant="secondary">RAG</Badge>
              </div>
              <h3 className="mt-4 font-semibold text-text-primary">{kb.name}</h3>
              <div className="mt-2 flex items-center gap-4 text-sm text-text-secondary">
                <span className="flex items-center gap-1">
                  <FileText className="h-4 w-4" />
                  {kb.documents} docs
                </span>
                <span className="flex items-center gap-1">
                  <Database className="h-4 w-4" />
                  {kb.size}
                </span>
              </div>
              <p className="mt-2 text-xs text-text-tertiary">Updated {kb.lastUpdated}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
}
