'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TestTube,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Play,
  RotateCcw,
  FileCode,
  Shield,
  Clock,
  Bug,
  Zap,
  Search,
  MoreHorizontal,
  ChevronRight,
  Code2,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  AreaChart,
  Area,
} from 'recharts';

// Mock test data
const testStats = {
  total: 1248,
  passed: 1189,
  failed: 32,
  skipped: 27,
  coverage: 87.5,
  duration: '4m 32s',
};

// Mock bug data
const bugs = [
  {
    id: 'BUG-001',
    title: 'Memory leak in WebSocket connection handler',
    severity: 'critical',
    status: 'open',
    component: 'Backend',
    reportedAt: new Date('2024-01-18T10:30:00'),
    aiFixAvailable: true,
  },
  {
    id: 'BUG-002',
    title: 'Dashboard charts not responsive on mobile',
    severity: 'medium',
    status: 'in_progress',
    component: 'Frontend',
    reportedAt: new Date('2024-01-17T14:20:00'),
    aiFixAvailable: true,
  },
  {
    id: 'BUG-003',
    title: 'API rate limiting not enforced',
    severity: 'high',
    status: 'open',
    component: 'Backend',
    reportedAt: new Date('2024-01-16T09:15:00'),
    aiFixAvailable: false,
  },
  {
    id: 'BUG-004',
    title: 'Dark mode toggle state not persisted',
    severity: 'low',
    status: 'resolved',
    component: 'Frontend',
    reportedAt: new Date('2024-01-15T16:45:00'),
    resolvedAt: new Date('2024-01-16T11:30:00'),
    aiFixAvailable: true,
  },
  {
    id: 'BUG-005',
    title: 'Database connection pool exhaustion',
    severity: 'critical',
    status: 'in_progress',
    component: 'Infrastructure',
    reportedAt: new Date('2024-01-18T08:00:00'),
    aiFixAvailable: true,
  },
];

// Mock test files
const testFiles = [
  { name: 'auth.service.test.ts', tests: 24, passed: 24, failed: 0, coverage: 96.5, duration: '12s' },
  { name: 'user.controller.test.ts', tests: 18, passed: 17, failed: 1, coverage: 89.2, duration: '8s' },
  { name: 'payment.gateway.test.ts', tests: 32, passed: 30, failed: 2, coverage: 84.7, duration: '15s' },
  { name: 'dashboard.component.test.tsx', tests: 12, passed: 12, failed: 0, coverage: 92.1, duration: '6s' },
  { name: 'api.client.test.ts', tests: 45, passed: 43, failed: 2, coverage: 78.5, duration: '22s' },
];

// Chart data
const coverageData = [
  { name: 'Statements', value: 87.5, color: '#10b981' },
  { name: 'Branches', value: 82.3, color: '#3b82f6' },
  { name: 'Functions', value: 91.2, color: '#8b5cf6' },
  { name: 'Lines', value: 88.9, color: '#f59e0b' },
];

const bugSeverityData = [
  { name: 'Critical', value: 2, color: '#ef4444' },
  { name: 'High', value: 3, color: '#f97316' },
  { name: 'Medium', value: 8, color: '#f59e0b' },
  { name: 'Low', value: 12, color: '#3b82f6' },
];

const testTrendData = [
  { date: 'Mon', passed: 980, failed: 25 },
  { date: 'Tue', passed: 1050, failed: 30 },
  { date: 'Wed', passed: 1120, failed: 28 },
  { date: 'Thu', passed: 1150, failed: 35 },
  { date: 'Fri', passed: 1189, failed: 32 },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.25, 0.25, 0, 1] as const },
  },
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical':
      return 'bg-state-error-dim text-state-error border-state-error/30';
    case 'high':
      return 'bg-state-warning-dim text-state-warning border-state-warning/30';
    case 'medium':
      return 'bg-state-warning-dim text-state-warning border-state-warning/30';
    case 'low':
      return 'bg-state-running-dim text-state-running border-state-running/30';
    default:
      return 'bg-bg-elevated text-text-secondary border-border-default';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'open':
      return <AlertTriangle className="h-4 w-4 text-state-error" />;
    case 'in_progress':
      return <Clock className="h-4 w-4 text-state-warning" />;
    case 'resolved':
      return <CheckCircle2 className="h-4 w-4 text-state-success" />;
    default:
      return null;
  }
};

export default function TestingPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string | null>(null);

  const filteredBugs = bugs.filter((bug) => {
    const matchesSearch =
      bug.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bug.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = !selectedSeverity || bug.severity === selectedSeverity;
    return matchesSearch && matchesSeverity;
  });

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Testing & QA</h1>
          <p className="mt-1 text-text-secondary">
            AI-powered testing, bug detection, and quality assurance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="border-border-default text-text-secondary">
            <RotateCcw className="mr-2 h-4 w-4" />
            Regenerate Tests
          </Button>
          <Button variant="ai-action">
            <Play className="mr-2 h-4 w-4" />
            Run Test Suite
          </Button>
        </div>
      </motion.div>

      {/* Test Summary Stats */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-5">
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Total Tests</p>
                <p className="text-2xl font-bold text-text-primary font-mono">{testStats.total}</p>
              </div>
              <TestTube className="h-8 w-8 text-state-running opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Passed</p>
                <p className="text-2xl font-bold text-state-success font-mono">{testStats.passed}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-state-success opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Failed</p>
                <p className="text-2xl font-bold text-state-error font-mono">{testStats.failed}</p>
              </div>
              <XCircle className="h-8 w-8 text-state-error opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Coverage</p>
                <p className="text-2xl font-bold text-state-running font-mono">{testStats.coverage}%</p>
              </div>
              <Shield className="h-8 w-8 text-state-running opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-border-default bg-bg-panel">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary">Duration</p>
                <p className="text-2xl font-bold text-text-primary font-mono">{testStats.duration}</p>
              </div>
              <Clock className="h-8 w-8 text-text-secondary opacity-50" />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main Content Grid */}
      <motion.div variants={itemVariants} className="grid gap-6 lg:grid-cols-3">
        {/* Coverage Chart */}
        <Card className="border-border-default bg-bg-panel">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">Code Coverage</CardTitle>
            <CardDescription className="text-text-secondary">
              Coverage metrics by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={coverageData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {coverageData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--bg-elevated)',
                      border: '1px solid var(--border-default)',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {coverageData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-xs text-text-secondary">{item.name}</span>
                  <span className="text-xs font-mono text-text-primary">{item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bug Severity */}
        <Card className="border-border-default bg-bg-panel">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">Bug Distribution</CardTitle>
            <CardDescription className="text-text-secondary">
              Issues by severity level
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={bugSeverityData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" horizontal={false} />
                  <XAxis type="number" stroke="var(--text-tertiary)" fontSize={12} />
                  <YAxis dataKey="name" type="category" stroke="var(--text-tertiary)" fontSize={11} width={60} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--bg-elevated)',
                      border: '1px solid var(--border-default)',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {bugSeverityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Test Trend */}
        <Card className="border-border-default bg-bg-panel">
          <CardHeader>
            <CardTitle className="text-lg text-text-primary">Test Trend</CardTitle>
            <CardDescription className="text-text-secondary">
              Pass/fail rate over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={testTrendData}>
                  <defs>
                    <linearGradient id="colorPassed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--state-success)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="var(--state-success)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                  <XAxis dataKey="date" stroke="var(--text-tertiary)" fontSize={12} />
                  <YAxis stroke="var(--text-tertiary)" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--bg-elevated)',
                      border: '1px solid var(--border-default)',
                      borderRadius: '8px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="passed"
                    stroke="var(--state-success)"
                    strokeWidth={2}
                    fill="url(#colorPassed)"
                  />
                  <Area
                    type="monotone"
                    dataKey="failed"
                    stroke="var(--state-error)"
                    strokeWidth={2}
                    fill="transparent"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tabs Section */}
      <motion.div variants={itemVariants}>
        <Tabs defaultValue="bugs" className="space-y-4">
          <TabsList className="bg-bg-panel border border-border-default">
            <TabsTrigger
              value="bugs"
              className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running"
            >
              <Bug className="mr-2 h-4 w-4" />
              Bugs ({bugs.length})
            </TabsTrigger>
            <TabsTrigger
              value="files"
              className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running"
            >
              <FileCode className="mr-2 h-4 w-4" />
              Test Files
            </TabsTrigger>
            <TabsTrigger
              value="ai-fixes"
              className="data-[state=active]:bg-state-running-dim data-[state=active]:text-state-running"
            >
              <Zap className="mr-2 h-4 w-4" />
              AI Fixes
            </TabsTrigger>
          </TabsList>

          <TabsContent value="bugs">
            <Card className="border-border-default bg-bg-panel">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg text-text-primary">Bug Tracker</CardTitle>
                  <CardDescription className="text-text-secondary">
                    AI-detected issues and suggested fixes
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
                    <Input
                      placeholder="Search bugs..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-64 border-border-default bg-bg-input pl-10 text-text-primary"
                    />
                  </div>
                  <div className="flex items-center gap-1">
                    {['critical', 'high', 'medium', 'low'].map((severity) => (
                      <button
                        key={severity}
                        onClick={() => setSelectedSeverity(selectedSeverity === severity ? null : severity)}
                        className={`px-2 py-1 rounded-md text-xs font-medium transition-all capitalize ${
                          selectedSeverity === severity
                            ? 'bg-state-running-dim text-state-running'
                            : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                        }`}
                      >
                        {severity}
                      </button>
                    ))}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {filteredBugs.map((bug) => (
                    <div
                      key={bug.id}
                      className="flex items-center justify-between p-4 rounded-lg border border-border-subtle bg-bg-elevated hover:border-emphasis transition-all"
                    >
                      <div className="flex items-start gap-4">
                        <div className="mt-0.5">{getStatusIcon(bug.status)}</div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-mono text-text-tertiary">{bug.id}</span>
                            <Badge variant="outline" className={`text-xs ${getSeverityColor(bug.severity)}`}>
                              {bug.severity}
                            </Badge>
                            {bug.aiFixAvailable && (
                              <Badge variant="outline" className="bg-state-success-dim text-state-success text-xs">
                                <Zap className="mr-1 h-3 w-3" />
                                AI Fix Available
                              </Badge>
                            )}
                          </div>
                          <p className="font-medium text-text-primary">{bug.title}</p>
                          <p className="text-xs text-text-secondary mt-1">
                            {bug.component} • Reported {bug.reportedAt.toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {bug.aiFixAvailable && (
                          <Button variant="outline" size="sm" className="border-state-success text-state-success hover:bg-state-success-dim">
                            <Code2 className="mr-2 h-4 w-4" />
                            Apply Fix
                          </Button>
                        )}
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-text-secondary">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="files">
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">Test Files</CardTitle>
                <CardDescription className="text-text-secondary">
                  Coverage and results by file
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {testFiles.map((file) => (
                    <div
                      key={file.name}
                      className="flex items-center justify-between p-4 rounded-lg border border-border-subtle bg-bg-elevated"
                    >
                      <div className="flex items-center gap-4">
                        <FileCode className="h-5 w-5 text-state-running" />
                        <div>
                          <p className="font-medium text-text-primary font-mono text-sm">{file.name}</p>
                          <p className="text-xs text-text-secondary">
                            {file.tests} tests • {file.duration}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <div className="flex items-center gap-2 text-xs">
                            <span className="text-state-success">{file.passed} passed</span>
                            {file.failed > 0 && (
                              <span className="text-state-error">{file.failed} failed</span>
                            )}
                          </div>
                          <Progress value={(file.passed / file.tests) * 100} className="h-1 w-24 mt-1 bg-bg-base" />
                        </div>
                        <div className="text-right">
                          <span className="text-xs text-text-secondary">Coverage</span>
                          <p className={`font-mono font-medium ${file.coverage >= 90 ? 'text-state-success' : file.coverage >= 80 ? 'text-state-warning' : 'text-state-error'}`}>
                            {file.coverage}%
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai-fixes">
            <Card className="border-border-default bg-bg-panel">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">AI-Generated Fixes</CardTitle>
                <CardDescription className="text-text-secondary">
                  Automated code corrections suggested by AI agents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center justify-center py-12 text-text-secondary">
                  <Zap className="h-12 w-12 mb-4 opacity-50" />
                  <p className="text-lg font-medium">3 AI fixes ready to apply</p>
                  <p className="text-sm mt-1">Review and approve suggested corrections</p>
                  <Button variant="ai-action" className="mt-4">
                    Review Fixes
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </motion.div>
  );
}
