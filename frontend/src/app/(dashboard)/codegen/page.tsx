'use client';

import { motion } from 'framer-motion';
import { Play, Download, Copy, Check } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

import { useState } from 'react';

export default function CodeGenPage() {
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);

  const handleGenerate = () => {
    setGenerating(true);
    setTimeout(() => setGenerating(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Code Generator</h1>
          <p className="text-text-secondary">AI-powered code generation with validation</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border-default bg-bg-base/50">
          <CardHeader>
            <CardTitle className="text-text-primary">Input</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              placeholder="Describe what you want to build..."
              value={prompt}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
              className="min-h-[200px] w-full rounded-md border border-border-default bg-slate-950 px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <Button 
              onClick={handleGenerate}
              disabled={generating || !prompt}
              className="w-full bg-emerald-500 hover:bg-emerald-600"
            >
              {generating ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Generating...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Generate Code
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card className="border-border-default bg-bg-base/50">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-text-primary">Output</CardTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="icon">
                <Copy className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="min-h-[200px] rounded-lg bg-slate-950 p-4 font-mono text-sm text-text-secondary">
              {generating ? (
                <div className="flex items-center justify-center h-full">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent" />
                </div>
              ) : (
                '// Generated code will appear here...'
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
