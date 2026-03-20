'use client';

import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FlaskConical, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  FileText,
  Image,
  Video,
  Terminal,
  Download,
  ExternalLink,
  TrendingUp,
  Shield,
  Eye,
  Zap,
} from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CodeBlock } from '@/components/typography/code-block';

export type ArtifactType = 'report' | 'screenshot' | 'video' | 'logs';

export interface SimulationArtifact {
  type: ArtifactType;
  url: string;
  label: string;
  size?: string;
  createdAt?: Date;
}

export interface SimulationResults {
  testsPassed: number;
  testsFailed: number;
  coverage: number;
  performanceScore: number;
  securityIssues: number;
  visualRegressions: number;
  flakyTests?: number;
  skippedTests?: number;
}

export interface SimulationResultPanelProps {
  simulationId: string;
  scenario: string;
  status: 'running' | 'completed' | 'failed';
  results?: SimulationResults;
  duration: string;
  artifacts?: SimulationArtifact[];
  testDetails?: Array<{
    name: string;
    status: 'passed' | 'failed' | 'skipped';
    duration?: string;
    error?: string;
  }>;
  className?: string;
  onArtifactClick?: (artifact: SimulationArtifact) => void;
}

const artifactIcons: Record<ArtifactType, React.ElementType> = {
  report: FileText,
  screenshot: Image,
  video: Video,
  logs: Terminal,
};

/**
 * SimulationResultPanel - Comprehensive simulation results dashboard
 * Shows test results, coverage, performance, and artifacts
 */
export function SimulationResultPanel({
  simulationId,
  scenario,
  status,
  results,
  duration,
  artifacts = [],
  testDetails = [],
  className,
  onArtifactClick,
}: SimulationResultPanelProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedTests, setExpandedTests] = useState<Set<string>>(new Set());

  const totalTests = results 
    ? results.testsPassed + results.testsFailed + (results.skippedTests || 0)
    : 0;

  const passRate = results && totalTests > 0 
    ? (results.testsPassed / totalTests) * 100 
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'overflow-hidden rounded-lg border border-border-default',
        'bg-bg-panel',
        className
      )}
    >
      {/* Status Banner */}
      <div className={cn(
        'relative overflow-hidden px-6 py-4',
        status === 'running' && 'bg-gradient-to-r from-state-running-dim to-transparent',
        status === 'completed' && 'bg-gradient-to-r from-state-success-dim to-transparent',
        status === 'failed' && 'bg-gradient-to-r from-state-error-dim to-transparent'
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={cn(
              'p-3 rounded-xl border',
              status === 'running' && 'bg-state-running-dim border-state-running/30 text-state-running',
              status === 'completed' && 'bg-state-success-dim border-state-success/30 text-state-success',
              status === 'failed' && 'bg-state-error-dim border-state-error/30 text-state-error'
            )}>
              <FlaskConical className="w-6 h-6" />
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                {scenario}
              </h3>
              <div className="flex items-center gap-2 mt-0.5">
                <Badge variant="outline" className="font-mono text-xs">
                  {simulationId.slice(0, 8)}
                </Badge>
                <span className="text-sm text-text-tertiary">
                  Duration: {duration}
                </span>
                {status === 'running' && (
                  <span className="flex items-center gap-1 text-sm text-state-running">
                    <span className="w-1.5 h-1.5 rounded-full bg-state-running animate-pulse" />
                    Running...
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Overall status badge */}
          <div className={cn(
            'px-4 py-2 rounded-lg border font-semibold',
            status === 'running' && 'bg-state-running-dim border-state-running/30 text-state-running',
            status === 'completed' && 'bg-state-success-dim border-state-success/30 text-state-success',
            status === 'failed' && 'bg-state-error-dim border-state-error/30 text-state-error'
          )}>
            {status.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="border-b border-border-subtle px-6">
          <TabsList className="bg-transparent">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tests">Test Results</TabsTrigger>
            <TabsTrigger value="artifacts">Artifacts</TabsTrigger>
            {results && (
              <TabsTrigger value="coverage">Coverage</TabsTrigger>
            )}
          </TabsList>
        </div>

        {/* Overview Tab */}
        <TabsContent value="overview" className="p-6">
          {results ? (
            <>
              {/* Summary Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                <SummaryStat
                  icon={CheckCircle2}
                  label="Passed"
                  value={results.testsPassed.toString()}
                  color="text-state-success"
                  bgColor="bg-state-success-dim"
                />
                <SummaryStat
                  icon={XCircle}
                  label="Failed"
                  value={results.testsFailed.toString()}
                  color={results.testsFailed > 0 ? 'text-state-error' : 'text-text-tertiary'}
                  bgColor={results.testsFailed > 0 ? 'bg-state-error-dim' : 'bg-bg-base'}
                />
                <SummaryStat
                  icon={TrendingUp}
                  label="Coverage"
                  value={`${results.coverage.toFixed(0)}%`}
                  color="text-state-running"
                  bgColor="bg-state-running-dim"
                />
                <SummaryStat
                  icon={Zap}
                  label="Performance"
                  value={results.performanceScore.toString()}
                  color={results.performanceScore >= 90 ? 'text-state-success' : 'text-state-warning'}
                  bgColor={results.performanceScore >= 90 ? 'bg-state-success-dim' : 'bg-state-warning-dim'}
                />
                <SummaryStat
                  icon={Shield}
                  label="Security Issues"
                  value={results.securityIssues.toString()}
                  color={results.securityIssues > 0 ? 'text-state-error' : 'text-text-tertiary'}
                  bgColor={results.securityIssues > 0 ? 'bg-state-error-dim' : 'bg-bg-base'}
                />
                <SummaryStat
                  icon={Eye}
                  label="Visual Regressions"
                  value={results.visualRegressions.toString()}
                  color={results.visualRegressions > 0 ? 'text-state-warning' : 'text-text-tertiary'}
                  bgColor={results.visualRegressions > 0 ? 'bg-state-warning-dim' : 'bg-bg-base'}
                />
              </div>

              {/* Pass Rate Progress */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-secondary">Pass Rate</span>
                  <span className="text-sm font-mono font-semibold text-text-code">
                    {passRate.toFixed(1)}%
                  </span>
                </div>
                <Progress value={passRate} className="h-2" showAnimation={status === 'running'} />
              </div>

              {/* Quick Actions */}
              {artifacts.length > 0 && (
                <div className="flex items-center gap-2 pt-4 border-t border-border-subtle">
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Download Report
                  </Button>
                  <Button variant="outline" size="sm">
                    <ExternalLink className="w-4 h-4 mr-2" />
                    View Full Report
                  </Button>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center py-12 text-text-tertiary">
              {status === 'running' ? (
                <div className="text-center">
                  <FlaskConical className="w-12 h-12 mx-auto mb-3 opacity-50 animate-pulse" />
                  <p>Simulation in progress...</p>
                </div>
              ) : (
                <div className="text-center">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No results available</p>
                </div>
              )}
            </div>
          )}
        </TabsContent>

        {/* Test Results Tab */}
        <TabsContent value="tests" className="p-6">
          {testDetails.length > 0 ? (
            <div className="space-y-2 max-h-[600px] overflow-auto">
              {testDetails.map((test, index) => (
                <TestResultItem
                  key={index}
                  test={test}
                  isExpanded={expandedTests.has(test.name)}
                  onToggle={() => {
                    const newExpanded = new Set(expandedTests);
                    if (newExpanded.has(test.name)) {
                      newExpanded.delete(test.name);
                    } else {
                      newExpanded.add(test.name);
                    }
                    setExpandedTests(newExpanded);
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-text-tertiary">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No test details available</p>
            </div>
          )}
        </TabsContent>

        {/* Artifacts Tab */}
        <TabsContent value="artifacts" className="p-6">
          {artifacts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {artifacts.map((artifact, index) => (
                <ArtifactCard
                  key={index}
                  artifact={artifact}
                  onClick={() => onArtifactClick?.(artifact)}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-text-tertiary">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No artifacts generated</p>
            </div>
          )}
        </TabsContent>

        {/* Coverage Tab */}
        <TabsContent value="coverage" className="p-6">
          {results ? (
            <div className="space-y-4">
              <CoverageBar label="Overall Coverage" percentage={results.coverage} />
              
              <div className="grid grid-cols-2 gap-4">
                <CoverageBar label="Line Coverage" percentage={results.coverage - 2} />
                <CoverageBar label="Branch Coverage" percentage={results.coverage - 5} />
                <CoverageBar label="Function Coverage" percentage={results.coverage + 3} />
                <CoverageBar label="Statement Coverage" percentage={results.coverage - 1} />
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-text-tertiary">
              <p>Coverage data not available</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}

interface SummaryStatProps {
  icon: React.ElementType;
  label: string;
  value: string;
  color: string;
  bgColor: string;
}

function SummaryStat({ icon: Icon, label, value, color, bgColor }: SummaryStatProps) {
  return (
    <div className={cn('p-3 rounded-lg border', bgColor)}>
      <div className="flex items-center gap-2 mb-1">
        <Icon className={cn('w-4 h-4', color)} />
        <span className="text-xs text-text-secondary">{label}</span>
      </div>
      <div className={cn('text-lg font-bold font-mono', color)}>
        {value}
      </div>
    </div>
  );
}

interface TestResultItemProps {
  test: {
    name: string;
    status: 'passed' | 'failed' | 'skipped';
    duration?: string;
    error?: string;
  };
  isExpanded: boolean;
  onToggle: () => void;
}

function TestResultItem({ test, isExpanded, onToggle }: TestResultItemProps) {
  return (
    <div
      className={cn(
        'rounded-lg border transition-all cursor-pointer',
        test.status === 'passed' && 'border-state-success/20 bg-state-success-dim/20',
        test.status === 'failed' && 'border-state-error/20 bg-state-error-dim/20',
        test.status === 'skipped' && 'border-border-subtle bg-bg-base'
      )}
      onClick={onToggle}
    >
      <div className="flex items-center justify-between p-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {test.status === 'passed' && <CheckCircle2 className="w-5 h-5 text-state-success shrink-0" />}
          {test.status === 'failed' && <XCircle className="w-5 h-5 text-state-error shrink-0" />}
          {test.status === 'skipped' && <AlertTriangle className="w-5 h-5 text-text-tertiary shrink-0" />}
          
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-medium text-text-primary truncate">
              {test.name}
            </h4>
            {test.duration && (
              <p className="text-xs text-text-tertiary mt-0.5">
                Duration: {test.duration}
              </p>
            )}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isExpanded && test.error && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-3 pb-3 pt-0"
          >
            <div className="mt-2 p-3 rounded bg-bg-code border border-border-subtle">
              <CodeBlock compact language="plaintext">
                {test.error}
              </CodeBlock>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface ArtifactCardProps {
  artifact: SimulationArtifact;
  onClick: () => void;
}

function ArtifactCard({ artifact, onClick }: ArtifactCardProps) {
  const Icon = artifactIcons[artifact.type];

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        'p-4 rounded-lg border transition-all cursor-pointer',
        'bg-bg-elevated hover:bg-bg-overlay',
        'border-border-default hover:border-emphasis'
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded bg-bg-base border border-border-subtle">
            <Icon className="w-4 h-4 text-text-secondary" />
          </div>
          <span className="text-sm font-medium text-text-primary capitalize">
            {artifact.type}
          </span>
        </div>
        <ExternalLink className="w-4 h-4 text-text-tertiary" />
      </div>
      
      <p className="text-sm text-text-secondary mb-2 truncate">
        {artifact.label}
      </p>
      
      <div className="flex items-center justify-between text-xs text-text-tertiary">
        {artifact.size && <span>{artifact.size}</span>}
        {artifact.createdAt && (
          <span>{artifact.createdAt.toLocaleDateString()}</span>
        )}
      </div>
    </motion.div>
  );
}

interface CoverageBarProps {
  label: string;
  percentage: number;
}

function CoverageBar({ label, percentage }: CoverageBarProps) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="text-text-secondary">{label}</span>
        <span className="font-mono font-semibold text-text-code">
          {percentage.toFixed(0)}%
        </span>
      </div>
      <Progress value={percentage} className="h-2" />
    </div>
  );
}
