'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Folder, File, RefreshCw, GitBranch } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface Repository {
  name: string;
  path: string;
  branch?: string;
  last_commit?: string;
  files_count?: number;
}

export default function FilesPage() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('aifactory_token');
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE}/git/repositories`, { headers, credentials: 'include' });
      if (res.ok) {
        const body = await res.json();
        // Backend may return array directly or wrapped in APIResponse
        const data = Array.isArray(body) ? body : (body.data ?? body.repositories ?? []);
        setRepos(data);
      } else if (res.status === 404) {
        setError('No repositories found. Generate code to create project files.');
      } else {
        setError('Unable to load repositories from git service.');
      }
    } catch {
      setError('Git service unavailable.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">File Manager</h1>
          <p className="text-text-secondary">Browse generated project repositories</p>
        </div>
        <Button onClick={fetchData} disabled={loading} className="bg-state-success hover:bg-state-success/90">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            Repositories
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading && <p className="text-text-secondary text-sm">Loading repositories…</p>}
          {error && <p className="text-text-tertiary text-sm">{error}</p>}
          {!loading && !error && repos.length === 0 && (
            <p className="text-text-secondary text-sm">No repositories yet. Run a project workflow to generate code.</p>
          )}
          <div className="space-y-2">
            {repos.map((repo, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-bg-hover/30 hover:bg-bg-hover/50 transition-colors">
                <div className="flex items-center gap-3">
                  <Folder className="h-5 w-5 text-state-warning" />
                  <div>
                    <span className="font-medium text-text-primary">{repo.name}</span>
                    {repo.path && <p className="text-xs text-text-tertiary font-mono">{repo.path}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {repo.branch && (
                    <Badge variant="outline" className="text-xs font-mono bg-state-running-dim text-state-running">
                      {repo.branch}
                    </Badge>
                  )}
                  {repo.files_count !== undefined && (
                    <span className="text-xs text-text-tertiary flex items-center gap-1">
                      <File className="h-3 w-3" /> {repo.files_count} files
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
