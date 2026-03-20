"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";

import { 
  Play, 
  Bug, 
  Shield, 
  Activity, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  FileCode,
  Eye,
  Zap,
  TrendingUp,
} from "lucide-react";

interface TestHealthData {
  summary: {
    total_test_suites: number;
    total_tests: number;
    flaky_tests: number;
    total_bugs_detected: number;
    critical_bugs: number;
    average_coverage: number;
    fixes_applied: number;
  };
  flaky_tests: Array<{
    id: string;
    name: string;
    failure_rate: number;
    quarantined: boolean;
  }>;
  recent_bugs: Array<{
    id: string;
    severity: string;
    category: string;
    title: string;
    file_path: string;
  }>;
  recent_fixes: Array<{
    bug_id: string;
    success: boolean;
    file_path: string;
  }>;
  coverage_trend: Array<{
    timestamp: string;
    overall_coverage: number;
  }>;
}

export default function TestingDashboard() {
  const [healthData, setHealthData] = useState<TestHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchHealthData();
  }, []);

  const fetchHealthData = async () => {
    try {
      const response = await fetch("/api/v1/testing/health");
      const data = await response.json();
      setHealthData(data);
    } catch (error) {
      console.error("Failed to fetch health data:", error);
    } finally {
      setLoading(false);
    }
  };

  const runFullSuite = async () => {
    try {
      await fetch("/api/v1/testing/run-full-suite", { method: "POST" });
      alert("Full test suite started in background");
    } catch (error) {
      console.error("Failed to start test suite:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  const summary = healthData?.summary || {
    total_test_suites: 0,
    total_tests: 0,
    flaky_tests: 0,
    total_bugs_detected: 0,
    critical_bugs: 0,
    average_coverage: 0,
    fixes_applied: 0,
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">AI Testing Dashboard</h1>
          <p className="text-muted-foreground">
            Autonomous test generation, bug detection, and self-healing
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchHealthData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={runFullSuite}>
            <Play className="w-4 h-4 mr-2" />
            Run Full Suite
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Test Coverage</CardTitle>
            <Shield className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary.average_coverage?.toFixed(1) || 0}%
            </div>
            <Progress 
              value={summary.average_coverage || 0} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
            <CheckCircle className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_tests || 0}</div>
            <p className="text-xs text-muted-foreground">
              {summary.total_test_suites || 0} test suites
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Bugs Detected</CardTitle>
            <Bug className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_bugs_detected || 0}</div>
            <p className="text-xs text-red-500">
              {summary.critical_bugs || 0} critical
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Auto-Fixes</CardTitle>
            <Zap className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.fixes_applied || 0}</div>
            <p className="text-xs text-green-500">Successfully applied</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="bugs">Bugs</TabsTrigger>
          <TabsTrigger value="flaky">Flaky Tests</TabsTrigger>
          <TabsTrigger value="coverage">Coverage</TabsTrigger>
          <TabsTrigger value="actions">Actions</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Bugs</CardTitle>
                <CardDescription>Latest detected issues</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {healthData?.recent_bugs?.slice(0, 5).map((bug) => (
                    <div 
                      key={bug.id} 
                      className="flex items-center justify-between p-2 border rounded"
                    >
                      <div className="flex items-center gap-2">
                        <Bug className={`w-4 h-4 ${
                          bug.severity === 'critical' ? 'text-red-500' : 
                          bug.severity === 'high' ? 'text-orange-500' : 'text-yellow-500'
                        }`} />
                        <div>
                          <p className="text-sm font-medium">{bug.title}</p>
                          <p className="text-xs text-muted-foreground">{bug.file_path}</p>
                        </div>
                      </div>
                      <Badge variant={
                        bug.severity === 'critical' ? 'destructive' : 
                        bug.severity === 'high' ? 'default' : 'secondary'
                      }>
                        {bug.severity}
                      </Badge>
                    </div>
                  )) || <p className="text-muted-foreground">No recent bugs</p>}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Fixes</CardTitle>
                <CardDescription>Automatically applied fixes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {healthData?.recent_fixes?.slice(0, 5).map((fix, idx) => (
                    <div 
                      key={idx} 
                      className="flex items-center justify-between p-2 border rounded"
                    >
                      <div className="flex items-center gap-2">
                        {fix.success ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-500" />
                        )}
                        <div>
                          <p className="text-sm font-medium">Bug {fix.bug_id}</p>
                          <p className="text-xs text-muted-foreground">{fix.file_path}</p>
                        </div>
                      </div>
                      <Badge variant={fix.success ? 'default' : 'destructive'}>
                        {fix.success ? 'Fixed' : 'Failed'}
                      </Badge>
                    </div>
                  )) || <p className="text-muted-foreground">No recent fixes</p>}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Coverage Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Coverage Trend</CardTitle>
              <CardDescription>Test coverage over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-48 flex items-end gap-2">
                {healthData?.coverage_trend?.map((point, idx) => (
                  <div 
                    key={idx}
                    className="flex-1 bg-primary/20 rounded-t"
                    style={{ height: `${point.overall_coverage}%` }}
                    title={`${new Date(point.timestamp).toLocaleDateString()}: ${point.overall_coverage.toFixed(1)}%`}
                  />
                )) || <p className="text-muted-foreground">No coverage data</p>}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Bugs Tab */}
        <TabsContent value="bugs" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Bug Detection</CardTitle>
                <CardDescription>Scan your code for bugs and security issues</CardDescription>
              </div>
              <Button>
                <Bug className="w-4 h-4 mr-2" />
                Scan All Files
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {healthData?.recent_bugs?.map((bug) => (
                  <div 
                    key={bug.id} 
                    className={`p-4 rounded-lg border ${
                      bug.severity === 'critical' 
                        ? 'border-red-500/50 bg-red-500/10' 
                        : 'border-slate-700 bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                        bug.severity === 'critical' ? 'text-red-400' : 'text-amber-400'
                      }`} />
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium text-slate-200">{bug.title}</p>
                            <p className="text-sm text-slate-400">{bug.file_path}</p>
                            <p className="text-xs text-slate-500">Category: {bug.category}</p>
                          </div>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="w-4 h-4 mr-1" />
                              View
                            </Button>
                            <Button size="sm">
                              <Zap className="w-4 h-4 mr-1" />
                              Fix
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )) || <p className="text-muted-foreground">No bugs detected</p>}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Flaky Tests Tab */}
        <TabsContent value="flaky" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Flaky Tests</CardTitle>
              <CardDescription>Tests with inconsistent results</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {healthData?.flaky_tests?.map((test) => (
                  <div 
                    key={test.id}
                    className="flex items-center justify-between p-3 border rounded"
                  >
                    <div className="flex items-center gap-3">
                      <Activity className="w-4 h-4 text-yellow-500" />
                      <div>
                        <p className="font-medium">{test.name}</p>
                        <p className="text-sm text-muted-foreground">
                          Failure rate: {(test.failure_rate * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {test.quarantined ? (
                        <Badge variant="secondary">Quarantined</Badge>
                      ) : (
                        <Button size="sm" variant="outline">
                          Quarantine
                        </Button>
                      )}
                      <Button size="sm" variant="outline">
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                )) || <p className="text-muted-foreground">No flaky tests detected</p>}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Coverage Tab */}
        <TabsContent value="coverage" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Coverage Analysis</CardTitle>
                <CardDescription>Identify coverage gaps</CardDescription>
              </div>
              <Button>
                <TrendingUp className="w-4 h-4 mr-2" />
                Analyze Coverage
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 border rounded text-center">
                    <p className="text-2xl font-bold text-green-500">
                      {summary.average_coverage >= 80 ? 'Good' : summary.average_coverage >= 50 ? 'Fair' : 'Poor'}
                    </p>
                    <p className="text-sm text-muted-foreground">Coverage Level</p>
                  </div>
                  <div className="p-4 border rounded text-center">
                    <p className="text-2xl font-bold">{healthData?.flaky_tests?.length || 0}</p>
                    <p className="text-sm text-muted-foreground">Flaky Tests</p>
                  </div>
                  <div className="p-4 border rounded text-center">
                    <p className="text-2xl font-bold">{summary.fixes_applied || 0}</p>
                    <p className="text-sm text-muted-foreground">Auto-Fixes</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Actions Tab */}
        <TabsContent value="actions" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Generate Tests</CardTitle>
                <CardDescription>AI-powered test generation</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" variant="outline">
                  <FileCode className="w-4 h-4 mr-2" />
                  Generate Unit Tests
                </Button>
                <Button className="w-full" variant="outline">
                  <Eye className="w-4 h-4 mr-2" />
                  Generate E2E Tests
                </Button>
                <Button className="w-full" variant="outline">
                  <Shield className="w-4 h-4 mr-2" />
                  Generate Security Tests
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Run Tests</CardTitle>
                <CardDescription>Execute test suites</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" variant="outline">
                  <Play className="w-4 h-4 mr-2" />
                  Run Unit Tests
                </Button>
                <Button className="w-full" variant="outline">
                  <Eye className="w-4 h-4 mr-2" />
                  Run E2E Tests
                </Button>
                <Button className="w-full" variant="outline">
                  <Activity className="w-4 h-4 mr-2" />
                  Run Visual Regression
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Auto-Fix</CardTitle>
                <CardDescription>Automatically fix detected issues</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" variant="outline">
                  <Zap className="w-4 h-4 mr-2" />
                  Fix All Critical Bugs
                </Button>
                <Button className="w-full" variant="outline">
                  <Bug className="w-4 h-4 mr-2" />
                  Fix Security Issues
                </Button>
                <Button className="w-full" variant="outline">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Fix Performance Issues
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Reports</CardTitle>
                <CardDescription>View detailed reports</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" variant="outline">
                  <FileCode className="w-4 h-4 mr-2" />
                  Coverage Report
                </Button>
                <Button className="w-full" variant="outline">
                  <Bug className="w-4 h-4 mr-2" />
                  Bug Report
                </Button>
                <Button className="w-full" variant="outline">
                  <Activity className="w-4 h-4 mr-2" />
                  Test Execution Report
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
