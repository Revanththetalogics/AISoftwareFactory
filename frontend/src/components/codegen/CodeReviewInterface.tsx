'use client';

import { useState } from 'react';
import { 
  FileCode, 
  CheckCircle2, 
  XCircle, 
  MessageSquare, 
  RefreshCw,
  ChevronRight,
  ChevronDown,
  GitCommit,
  AlertCircle,
  Sparkles,
  Loader2,
  ThumbsUp,
  ThumbsDown,
  Send
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

interface CodeFile {
  id: string;
  path: string;
  language: string;
  content: string;
  status: 'pending' | 'approved' | 'changes_requested' | 'regenerating';
  feedback?: string;
  diff?: {
    added: number;
    removed: number;
  };
}

interface CodeReviewInterfaceProps {
  projectId?: string;
  className?: string;
}

// Mock generated code files
const mockGeneratedFiles: CodeFile[] = [
  {
    id: '1',
    path: 'src/app/api/auth/route.ts',
    language: 'typescript',
    content: `import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { email, password } = body;
    
    const user = await auth.validateCredentials(email, password);
    
    if (!user) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      );
    }
    
    const token = await auth.createToken(user);
    
    return NextResponse.json({ token, user });
  } catch (error) {
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    );
  }
}`,
    status: 'pending',
    diff: { added: 28, removed: 0 },
  },
  {
    id: '2',
    path: 'src/components/auth/LoginForm.tsx',
    language: 'typescript',
    content: `'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        throw new Error('Login failed');
      }

      router.push('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Loading...' : 'Login'}
      </button>
    </form>
  );
}`,
    status: 'pending',
    diff: { added: 62, removed: 0 },
  },
  {
    id: '3',
    path: 'src/lib/auth.ts',
    language: 'typescript',
    content: `import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { db } from './db';

export const auth = {
  async validateCredentials(email: string, password: string) {
    const user = await db.users.findUnique({ where: { email } });
    
    if (!user) return null;
    
    const valid = await bcrypt.compare(password, user.passwordHash);
    
    return valid ? user : null;
  },
  
  async createToken(user: { id: string; email: string }) {
    return jwt.sign(
      { sub: user.id, email: user.email },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );
  },
  
  async hashPassword(password: string) {
    return bcrypt.hash(password, 10);
  }
};`,
    status: 'pending',
    diff: { added: 32, removed: 0 },
  },
];

interface FileReviewCardProps {
  file: CodeFile;
  onApprove: () => void;
  onRequestChanges: (feedback: string) => void;
  onRegenerate: () => void;
}

function FileReviewCard({ file, onApprove, onRequestChanges, onRegenerate }: FileReviewCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);

  const statusConfig = {
    pending: { color: 'text-text-secondary', bgColor: 'bg-bg-panel', label: 'Pending Review' },
    approved: { color: 'text-state-success', bgColor: 'bg-state-success-dim', label: 'Approved' },
    changes_requested: { color: 'text-state-warning', bgColor: 'bg-state-warning-dim', label: 'Changes Requested' },
    regenerating: { color: 'text-state-queued', bgColor: 'bg-state-queued-dim', label: 'Regenerating...' },
  };

  const config = statusConfig[file.status];
  const languageColors: Record<string, string> = {
    typescript: 'text-blue-400',
    javascript: 'text-yellow-400',
    python: 'text-green-400',
    css: 'text-pink-400',
    html: 'text-orange-400',
  };

  return (
    <div className={cn('rounded-lg border overflow-hidden', config.bgColor, 'border-border-default/50')}>
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-3 p-4 hover:bg-bg-hover transition-colors"
      >
        <FileCode className={cn('h-5 w-5', languageColors[file.language] || 'text-text-secondary')} />
        
        <div className="flex-1 text-left">
          <div className="flex items-center gap-2">
            <span className="font-medium text-text-primary font-mono text-sm">{file.path}</span>
            <Badge variant="outline" className={cn('text-xs', config.color)}>
              {config.label}
            </Badge>
          </div>
          <div className="flex items-center gap-3 mt-1 text-xs text-text-tertiary">
            <span className={languageColors[file.language] || 'text-text-secondary'}>{file.language}</span>
            {file.diff && (
              <>
                <span className="text-state-success">+{file.diff.added}</span>
                <span className="text-state-error">-{file.diff.removed}</span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {file.status === 'pending' && (
            <>
              <Button
                size="sm"
                variant="ghost"
                className="text-state-success hover:text-state-success hover:bg-state-success-dim"
                onClick={(e) => {
                  e.stopPropagation();
                  onApprove();
                }}
              >
                <ThumbsUp className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="text-state-warning hover:text-state-warning hover:bg-state-warning-dim"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowFeedbackInput(true);
                }}
              >
                <ThumbsDown className="h-4 w-4" />
              </Button>
            </>
          )}
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-text-tertiary" />
          ) : (
            <ChevronRight className="h-4 w-4 text-text-tertiary" />
          )}
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-border-default">
          {/* Code Preview */}
          <div className="relative">
            <pre className="p-4 overflow-x-auto text-sm bg-bg-base/50 font-mono">
              <code className="text-text-primary">{file.content}</code>
            </pre>
          </div>

          {/* Feedback Section */}
          {showFeedbackInput && file.status === 'pending' && (
            <div className="p-4 border-t border-border-default bg-state-warning-dim/30">
              <label className="text-sm font-medium text-text-primary mb-2 block">
                What changes would you like?
              </label>
              <textarea
                value={feedback}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFeedback(e.target.value)}
                placeholder="e.g., Add input validation, improve error messages..."
                rows={3}
                className="w-full rounded-lg border border-border-default bg-bg-panel px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-warning"
              />
              <div className="flex justify-end gap-2 mt-3">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setShowFeedbackInput(false);
                    setFeedback('');
                  }}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    onRequestChanges(feedback);
                    setShowFeedbackInput(false);
                    setFeedback('');
                  }}
                  disabled={!feedback.trim()}
                  className="bg-state-warning text-white hover:bg-state-warning/90"
                >
                  <Send className="mr-2 h-3 w-3" />
                  Request Changes
                </Button>
              </div>
            </div>
          )}

          {/* Previous Feedback */}
          {file.feedback && (
            <div className="p-4 border-t border-border-default bg-state-warning-dim/20">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-state-warning mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-text-primary">Feedback</p>
                  <p className="text-sm text-text-secondary">{file.feedback}</p>
                  {file.status === 'changes_requested' && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-2"
                      onClick={onRegenerate}
                    >
                      <RefreshCw className="mr-2 h-3 w-3" />
                      Regenerate with Feedback
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Regenerating State */}
          {file.status === 'regenerating' && (
            <div className="p-4 border-t border-border-default bg-state-queued-dim/20">
              <div className="flex items-center gap-3">
                <Loader2 className="h-5 w-5 animate-spin text-state-queued" />
                <div>
                  <p className="text-sm font-medium text-text-primary">AI is regenerating...</p>
                  <p className="text-xs text-text-secondary">Incorporating your feedback</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function CodeReviewInterface({ projectId, className }: CodeReviewInterfaceProps) {
  const [files, setFiles] = useState<CodeFile[]>(mockGeneratedFiles);
  const [isCommitting, setIsCommitting] = useState(false);

  const approvedCount = files.filter(f => f.status === 'approved').length;
  const totalCount = files.length;
  const progress = (approvedCount / totalCount) * 100;

  const handleApprove = (fileId: string) => {
    setFiles(files.map(f => 
      f.id === fileId ? { ...f, status: 'approved' } : f
    ));
    toast.success('File approved');
  };

  const handleRequestChanges = (fileId: string, feedback: string) => {
    setFiles(files.map(f => 
      f.id === fileId ? { ...f, status: 'changes_requested', feedback } : f
    ));
    toast.success('Feedback submitted');
  };

  const handleRegenerate = async (fileId: string) => {
    setFiles(files.map(f => 
      f.id === fileId ? { ...f, status: 'regenerating' } : f
    ));

    // Simulate AI regeneration
    await new Promise(resolve => setTimeout(resolve, 3000));

    setFiles(files.map(f => 
      f.id === fileId ? { 
        ...f, 
        status: 'pending',
        content: f.content + '\n// Regenerated with improvements\n',
      } : f
    ));
    toast.success('File regenerated with your feedback');
  };

  const handleCommitAll = async () => {
    if (approvedCount < totalCount) {
      toast.error(`Approve all files before committing (${approvedCount}/${totalCount})`);
      return;
    }

    setIsCommitting(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    toast.success('All changes committed successfully');
    setIsCommitting(false);
  };

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-state-queued" />
              Code Review
            </CardTitle>
            <p className="text-sm text-text-secondary">
              Review and approve AI-generated code
            </p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-text-primary">{approvedCount}/{totalCount}</span>
            <p className="text-xs text-text-tertiary">Files approved</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="h-2 w-full rounded-full bg-bg-base overflow-hidden">
            <div 
              className="h-full rounded-full bg-gradient-to-r from-state-queued to-state-success transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {files.map((file) => (
          <FileReviewCard
            key={file.id}
            file={file}
            onApprove={() => handleApprove(file.id)}
            onRequestChanges={(feedback) => handleRequestChanges(file.id, feedback)}
            onRegenerate={() => handleRegenerate(file.id)}
          />
        ))}

        {/* Commit Button */}
        <div className="pt-4 border-t border-border-default">
          <Button
            className="w-full"
            disabled={approvedCount < totalCount || isCommitting}
            onClick={handleCommitAll}
          >
            {isCommitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Committing...
              </>
            ) : (
              <>
                <GitCommit className="mr-2 h-4 w-4" />
                Commit {approvedCount === totalCount ? 'All Changes' : `(${approvedCount}/${totalCount})`}
              </>
            )}
          </Button>
          {approvedCount < totalCount && (
            <p className="text-xs text-text-tertiary text-center mt-2">
              Approve all files before committing
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
