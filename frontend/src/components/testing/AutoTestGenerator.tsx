'use client';

import { useState } from 'react';
import { 
  TestTube, 
  Play, 
  CheckCircle2, 
  XCircle, 
  Clock,
  FileCode,
  Eye,
  RefreshCw,
  Loader2,
  ChevronDown,
  ChevronRight,
  Image as ImageIcon,
  AlertTriangle
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

interface TestFile {
  id: string;
  name: string;
  type: 'unit' | 'integration' | 'e2e' | 'visual';
  status: 'pending' | 'running' | 'passed' | 'failed';
  duration?: string;
  coverage?: number;
  content?: string;
}

interface VisualRegressionTest {
  id: string;
  name: string;
  baselineUrl: string;
  currentUrl: string;
  diffUrl?: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  diffPercentage?: number;
}

interface AutoTestGeneratorProps {
  projectId?: string;
  className?: string;
}

const mockTests: TestFile[] = [
  {
    id: '1',
    name: 'auth.test.ts',
    type: 'unit',
    status: 'passed',
    duration: '1.2s',
    coverage: 94,
    content: `describe('Auth', () => {
  it('should validate credentials', async () => {
    const result = await auth.validateCredentials('test@test.com', 'password');
    expect(result).toBeDefined();
  });
});`,
  },
  {
    id: '2',
    name: 'LoginForm.test.tsx',
    type: 'unit',
    status: 'passed',
    duration: '0.8s',
    coverage: 87,
  },
  {
    id: '3',
    name: 'api.integration.test.ts',
    type: 'integration',
    status: 'running',
    content: `describe('API Integration', () => {
  it('should create user', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'test@test.com' });
    expect(res.status).toBe(201);
  });
});`,
  },
  {
    id: '4',
    name: 'login.e2e.test.ts',
    type: 'e2e',
    status: 'pending',
  },
];

const mockVisualTests: VisualRegressionTest[] = [
  {
    id: '1',
    name: 'Login Page',
    baselineUrl: '/api/placeholder/400/300',
    currentUrl: '/api/placeholder/400/300',
    status: 'passed',
    diffPercentage: 0,
  },
  {
    id: '2',
    name: 'Dashboard',
    baselineUrl: '/api/placeholder/400/300',
    currentUrl: '/api/placeholder/400/300',
    status: 'failed',
    diffPercentage: 12.5,
    diffUrl: '/api/placeholder/400/300',
  },
];

const typeConfig = {
  unit: { color: 'text-blue-400', bgColor: 'bg-blue-400/10', label: 'Unit' },
  integration: { color: 'text-purple-400', bgColor: 'bg-purple-400/10', label: 'Integration' },
  e2e: { color: 'text-green-400', bgColor: 'bg-green-400/10', label: 'E2E' },
  visual: { color: 'text-pink-400', bgColor: 'bg-pink-400/10', label: 'Visual' },
};

const statusConfig = {
  pending: { icon: Clock, color: 'text-text-tertiary', bgColor: 'bg-bg-base', label: 'Pending' },
  running: { icon: Loader2, color: 'text-state-queued', bgColor: 'bg-state-queued-dim', label: 'Running' },
  passed: { icon: CheckCircle2, color: 'text-state-success', bgColor: 'bg-state-success-dim', label: 'Passed' },
  failed: { icon: XCircle, color: 'text-state-error', bgColor: 'bg-state-error-dim', label: 'Failed' },
};

interface TestFileCardProps {
  test: TestFile;
  isExpanded: boolean;
  onToggle: () => void;
}

function TestFileCard({ test, isExpanded, onToggle }: TestFileCardProps) {
  const type = typeConfig[test.type];
  const status = statusConfig[test.status];
  const StatusIcon = status.icon;

  return (
    <div className={cn('rounded-lg border overflow-hidden', status.bgColor, 'border-border-default/50')}>
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-3 hover:bg-bg-hover transition-colors"
      >
        <FileCode className={cn('h-4 w-4', type.color)} />
        
        <div className="flex-1 text-left">
          <div className="flex items-center gap-2">
            <span className="font-medium text-text-primary text-sm">{test.name}</span>
            <Badge variant="outline" className={cn('text-xs', type.color, type.bgColor)}>
              {type.label}
            </Badge>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {test.coverage && (
            <span className={cn(
              'text-xs',
              test.coverage >= 80 ? 'text-state-success' : 'text-state-warning'
            )}>
              {test.coverage}% cov
            </span>
          )}
          {test.duration && (
            <span className="text-xs text-text-tertiary">{test.duration}</span>
          )}
          <StatusIcon className={cn('h-4 w-4', status.color)} />
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-text-tertiary" />
          ) : (
            <ChevronRight className="h-4 w-4 text-text-tertiary" />
          )}
        </div>
      </button>

      {isExpanded && test.content && (
        <div className="border-t border-border-default">
          <pre className="p-3 overflow-x-auto text-xs bg-bg-base/50 font-mono">
            <code className="text-text-primary">{test.content}</code>
          </pre>
        </div>
      )}
    </div>
  );
}

interface VisualRegressionCardProps {
  test: VisualRegressionTest;
}

function VisualRegressionCard({ test }: VisualRegressionCardProps) {
  const status = statusConfig[test.status];
  const StatusIcon = status.icon;

  return (
    <div className={cn('rounded-lg border p-4', status.bgColor, 'border-border-default/50')}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Eye className="h-4 w-4 text-pink-400" />
          <span className="font-medium text-text-primary">{test.name}</span>
        </div>
        <Badge variant="outline" className={cn('text-xs', status.color)}>
          <StatusIcon className="mr-1 h-3 w-3" />
          {status.label}
        </Badge>
      </div>

      {/* Image Comparison */}
      <div className="grid grid-cols-3 gap-2">
        <div className="space-y-1">
          <p className="text-xs text-text-tertiary text-center">Baseline</p>
          <div className="aspect-video rounded bg-bg-base flex items-center justify-center">
            <ImageIcon className="h-8 w-8 text-text-tertiary" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-xs text-text-tertiary text-center">Current</p>
          <div className="aspect-video rounded bg-bg-base flex items-center justify-center">
            <ImageIcon className="h-8 w-8 text-text-tertiary" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-xs text-text-tertiary text-center">Diff</p>
          <div className={cn(
            'aspect-video rounded flex items-center justify-center',
            test.diffPercentage && test.diffPercentage > 0 
              ? 'bg-state-error/20' 
              : 'bg-bg-base'
          )}>
            {test.diffPercentage && test.diffPercentage > 0 ? (
              <span className="text-state-error font-bold">{test.diffPercentage}%</span>
            ) : (
              <CheckCircle2 className="h-8 w-8 text-state-success" />
            )}
          </div>
        </div>
      </div>

      {test.status === 'failed' && (
        <div className="mt-3 flex gap-2">
          <Button size="sm" variant="outline" className="flex-1">
            <AlertTriangle className="mr-2 h-3 w-3" />
            Accept Changes
          </Button>
          <Button size="sm" variant="outline" className="flex-1">
            <RefreshCw className="mr-2 h-3 w-3" />
            Reject & Fix
          </Button>
        </div>
      )}
    </div>
  );
}

export function AutoTestGenerator({ projectId, className }: AutoTestGeneratorProps) {
  const [tests, setTests] = useState<TestFile[]>(mockTests);
  const [visualTests, setVisualTests] = useState<VisualRegressionTest[]>(mockVisualTests);
  const [expandedTest, setExpandedTest] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const passedCount = tests.filter(t => t.status === 'passed').length;
  const totalCount = tests.length;
  const coverage = Math.round(tests.reduce((sum, t) => sum + (t.coverage || 0), 0) / tests.length);

  const handleGenerate = async () => {
    setIsGenerating(true);
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const newTest: TestFile = {
      id: String(tests.length + 1),
      name: 'user-profile.test.ts',
      type: 'unit',
      status: 'pending',
      coverage: 92,
      content: `describe('UserProfile', () => {
  it('should update profile', async () => {
    const result = await updateProfile({ name: 'John' });
    expect(result.success).toBe(true);
  });
});`,
    };
    
    setTests([...tests, newTest]);
    setIsGenerating(false);
    toast.success('Generated new test with AI');
  };

  const handleRunAll = async () => {
    setIsRunning(true);
    
    // Update all pending/running tests
    setTests(tests.map(t => t.status === 'pending' ? { ...t, status: 'running' } : t));
    
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    setTests(tests.map(t => ({ 
      ...t, 
      status: Math.random() > 0.2 ? 'passed' : 'failed',
      duration: `${(Math.random() * 2 + 0.5).toFixed(1)}s`,
    })));
    
    setIsRunning(false);
    toast.success('All tests completed');
  };

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary flex items-center gap-2">
              <TestTube className="h-5 w-5 text-state-success" />
              AI Test Generator
            </CardTitle>
            <p className="text-sm text-text-secondary">
              Auto-generated tests with visual regression
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <span className="text-2xl font-bold text-text-primary">{coverage}%</span>
              <p className="text-xs text-text-tertiary">Coverage</p>
            </div>
            <div className="text-right">
              <span className={cn(
                'text-2xl font-bold',
                passedCount === totalCount ? 'text-state-success' : 'text-state-warning'
              )}>
                {passedCount}/{totalCount}
              </span>
              <p className="text-xs text-text-tertiary">Passed</p>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleGenerate}
            disabled={isGenerating}
            className="flex-1"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Generate Tests
              </>
            )}
          </Button>
          <Button
            onClick={handleRunAll}
            disabled={isRunning}
            className="flex-1"
          >
            {isRunning ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Run All Tests
              </>
            )}
          </Button>
        </div>

        {/* Test Files */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-text-primary">Generated Tests</h4>
          {tests.map((test) => (
            <TestFileCard
              key={test.id}
              test={test}
              isExpanded={expandedTest === test.id}
              onToggle={() => setExpandedTest(expandedTest === test.id ? null : test.id)}
            />
          ))}
        </div>

        {/* Visual Regression Tests */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-text-primary flex items-center gap-2">
            <Eye className="h-4 w-4 text-pink-400" />
            Visual Regression
          </h4>
          <div className="grid gap-3 sm:grid-cols-2">
            {visualTests.map((test) => (
              <VisualRegressionCard key={test.id} test={test} />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
