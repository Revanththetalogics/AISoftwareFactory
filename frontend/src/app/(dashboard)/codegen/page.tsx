'use client';

import { motion } from 'framer-motion';
import { Play, Download, Copy, Languages, ChevronDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

import { useState } from 'react';
import { api } from '@/lib/api/client';

interface GeneratedCode {
  generation_id: string;
  code: string;
  language: string;
  quality_score: number | null;
  warnings: string[];
  execution_time_ms: number;
}

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
];

const FRAMEWORKS: Record<string, Array<{value: string, label: string}>> = {
  python: [
    { value: 'fastapi', label: 'FastAPI' },
    { value: 'django', label: 'Django' },
    { value: 'flask', label: 'Flask' },
  ],
  javascript: [
    { value: 'react', label: 'React' },
    { value: 'express', label: 'Express' },
    { value: 'vue', label: 'Vue.js' },
  ],
  typescript: [
    { value: 'nextjs', label: 'Next.js' },
    { value: 'nestjs', label: 'NestJS' },
    { value: 'angular', label: 'Angular' },
  ],
};

export default function CodeGenPage() {
  const [prompt, setPrompt] = useState('');
  const [language, setLanguage] = useState('python');
  const [framework, setFramework] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showFrameworkDropdown, setShowFrameworkDropdown] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setGenerating(true);
    setError(null);
    
    try {
      const response = await api.generateCode({
        prompt,
        language,
        framework: framework || undefined
      });
      
      setGeneratedCode(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate code');
      console.error('Code generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = async () => {
    if (generatedCode?.code) {
      try {
        await navigator.clipboard.writeText(generatedCode.code);
        // Show success feedback
      } catch (err) {
        console.error('Failed to copy to clipboard:', err);
      }
    }
  };

  const downloadCode = () => {
    if (generatedCode?.code) {
      const blob = new Blob([generatedCode.code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `generated_code.${getFileExtension(language)}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const getFileExtension = (lang: string): string => {
    const extensions: Record<string, string> = {
      'python': 'py',
      'javascript': 'js',
      'typescript': 'ts',
      'java': 'java',
      'go': 'go',
      'rust': 'rs'
    };
    return extensions[lang] || 'txt';
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
        {/* Input Section */}
        <Card className="border-border-default bg-bg-base/50">
          <CardHeader>
            <CardTitle className="text-text-primary">Input</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="language">Language</Label>
              <div className="relative">
                <select
                  id="language"
                  value={language}
                  onChange={(e) => {
                    setLanguage(e.target.value);
                    setFramework(''); // Reset framework when language changes
                  }}
                  className="w-full rounded-md border border-border-default bg-bg-base px-3 py-2 text-text-primary focus:outline-none focus:ring-2 focus:ring-state-success"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="framework">Framework (Optional)</Label>
              <div className="relative">
                <button
                  type="button"
                  className="w-full rounded-md border border-border-default bg-bg-base px-3 py-2 text-left text-text-primary focus:outline-none focus:ring-2 focus:ring-state-success flex items-center justify-between"
                  onClick={() => setShowFrameworkDropdown(!showFrameworkDropdown)}
                >
                  <span>
                    {framework 
                      ? FRAMEWORKS[language]?.find(f => f.value === framework)?.label || 'Select framework'
                      : 'Select framework'
                    }
                  </span>
                  <ChevronDown className="h-4 w-4" />
                </button>
                
                {showFrameworkDropdown && (
                  <div className="absolute z-10 mt-1 w-full rounded-md border border-border-default bg-bg-base shadow-lg">
                    <div className="py-1">
                      {FRAMEWORKS[language]?.map((fw) => (
                        <button
                          key={fw.value}
                          type="button"
                          className="block w-full px-4 py-2 text-left text-sm text-text-primary hover:bg-bg-hover"
                          onClick={() => {
                            setFramework(fw.value);
                            setShowFrameworkDropdown(false);
                          }}
                        >
                          {fw.label}
                        </button>
                      ))}
                      <button
                        type="button"
                        className="block w-full px-4 py-2 text-left text-sm text-text-primary hover:bg-bg-hover border-t border-border-default"
                        onClick={() => {
                          setFramework('');
                          setShowFrameworkDropdown(false);
                        }}
                      >
                        None
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <textarea
              placeholder={`Describe what you want to build in ${language}...`}
              value={prompt}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
              className="min-h-[200px] w-full rounded-md border border-border-default bg-bg-code px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-success"
            />
            
            {error && (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <Button 
              onClick={handleGenerate}
              disabled={generating || !prompt.trim()}
              className="w-full bg-state-success hover:bg-state-success"
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

        {/* Output Section */}
        <Card className="border-border-default bg-bg-base/50">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-text-primary">Output</CardTitle>
            <div className="flex gap-2">
              <Button 
                variant="ghost" 
                size="icon"
                onClick={copyToClipboard}
                disabled={!generatedCode?.code}
                title="Copy to clipboard"
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button 
                variant="ghost" 
                size="icon"
                onClick={downloadCode}
                disabled={!generatedCode?.code}
                title="Download code"
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {generatedCode ? (
              <div className="space-y-4">
                <div className="flex items-center gap-4 text-sm text-text-secondary">
                  <div className="flex items-center gap-1">
                    <Languages className="h-4 w-4" />
                    {generatedCode.language}
                  </div>
                  {generatedCode.quality_score && (
                    <div>
                      Quality: {(generatedCode.quality_score * 100).toFixed(0)}%
                    </div>
                  )}
                  <div>
                    Time: {generatedCode.execution_time_ms.toFixed(0)}ms
                  </div>
                </div>
                
                {generatedCode.warnings.length > 0 && (
                  <div className="rounded-md bg-yellow-50 p-3 text-sm text-yellow-700">
                    <strong>Warnings:</strong>
                    <ul className="mt-1 list-disc pl-4">
                      {generatedCode.warnings.map((warning, index) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <pre className="min-h-[200px] max-h-[400px] overflow-auto rounded-lg bg-bg-code p-4 text-sm text-text-primary">
                  <code>{generatedCode.code}</code>
                </pre>
              </div>
            ) : generating ? (
              <div className="flex items-center justify-center h-[200px]">
                <div className="flex flex-col items-center gap-2">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-state-success border-t-transparent" />
                  <p className="text-text-secondary">Generating code...</p>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-[200px] text-text-secondary">
                Describe what you want to build and click &quot;Generate Code&quot;
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
