'use client';

import { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Grid3X3, GitGraph, Activity, Terminal, Wifi, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { PipelineStepper } from '@/components/factory/PipelineStepper';
import { AgentVisualization } from '@/components/factory/AgentVisualization';
import { AgentGraph } from '@/components/factory/AgentGraph';
import { EnhancedWorkflowPanel } from '@/components/factory/EnhancedWorkflowPanel';
import { LiveLogConsole, type LiveLogEntry, type LogLevel } from '@/components/factory/LiveLogConsole';
import { SystemHealthMonitor, DEFAULT_SYSTEM_METRICS, type SystemMetric } from '@/components/factory/SystemHealthMonitor';
import { useFactoryState } from '@/hooks/useFactoryState';
import { useFactoryWebSocket } from '@/hooks/useFactoryWebSocket';
import { useRealtimeSync } from '@/lib/hooks/useRealtimeSync';
import { useProjects } from '@/lib/hooks/useProjects';
import { useWorkflows } from '@/lib/hooks/useWorkflows';
import { useAgents } from '@/lib/hooks/useAgents';
import { cn } from '@/lib/utils';

export default function SuperEnhancedDashboardPage() {
  useRealtimeSync();

  // Fetch real data from API
  const { data: projects = [], isLoading: projectsLoading } = useProjects();
  const { data: workflows = [], isLoading: workflowsLoading } = useWorkflows();
  const { data: agents = [], isLoading: agentsLoading } = useAgents();
  
  // Keep factory state for UI interactions (will be removed in future refactor)
  const { state, dispatch, actions } = useFactoryState(); // Get both dispatch and actions
  const [isPlaying, setIsPlaying] = useState(true);
  const [agentView, setAgentView] = useState<'grid' | 'graph'>('grid');
  const [liveLogs, setLiveLogs] = useState<LiveLogEntry[]>([]);
  const [isLogsPaused, setIsLogsPaused] = useState(false);
  const [activeTab, setActiveTab] = useState<'logs' | 'health'>('logs');

  // Initialize WebSocket integration
  const {
    isConnected
    // sendPipelineUpdate,
    // sendAgentStatus,
    // sendWorkflowStep,
    // sendSystemMetric,
    // sendLogEntry,
    // sendFactoryReset
  } = useFactoryWebSocket(dispatch);

  // Generate live logs from workflow steps
  useEffect(() => {
    const generateLogs = () => {
      const newLogs: LiveLogEntry[] = [];
      
      state.workflow.steps.forEach(step => {
        if (step.logs && step.logs.length > 0) {
          step.logs.forEach((log, index) => {
            newLogs.push({
              id: `${step.id}-${index}`,
              timestamp: log.timestamp,
              level: log.level as LogLevel,
              source: log.source || step.title,
              message: log.message,
              details: step.output ? { output: step.output } : undefined
            });
          });
        }
      });

      // Add system logs
      const systemLogs: LiveLogEntry[] = [
        {
          id: 'sys-1',
          timestamp: new Date(),
          level: 'info',
          source: 'System',
          message: 'Factory initialized successfully'
        },
        {
          id: 'sys-2',
          timestamp: new Date(Date.now() - 1000),
          level: 'debug',
          source: 'Pipeline',
          message: `Current phase: ${state.pipeline.phases[state.pipeline.currentPhaseIndex]?.name || 'Unknown'}`
        }
      ];

      setLiveLogs([...systemLogs, ...newLogs].sort((a, b) => 
        b.timestamp.getTime() - a.timestamp.getTime()
      ));
    };

    generateLogs();
  }, [state.workflow.steps, state.pipeline]);

  const handlePhaseClick = (phaseId: string) => {
    console.log('Phase clicked:', phaseId);
  };

  const handleAgentClick = (agentId: string) => {
    console.log('Agent clicked:', agentId);
  };

  const handleAgentDrag = (agentId: string, x: number, y: number) => {
    actions.updateAgentPosition(agentId, x, y);
  };

  const handleStepToggle = (stepId: string) => {
    actions.toggleWorkflowStep(stepId);
  };

  const handleStepAction = (stepId: string, action: 'play' | 'pause' | 'reset' | 'retry' | 'skip') => {
    console.log('Step action:', stepId, action);
    // Handle step actions
    switch (action) {
      case 'play':
        actions.updateWorkflowStepStatus(stepId, 'running');
        break;
      case 'pause':
        actions.updateWorkflowStepStatus(stepId, 'pending');
        break;
      case 'reset':
        actions.updateWorkflowStepStatus(stepId, 'pending');
        break;
      case 'retry':
        actions.updateWorkflowStepStatus(stepId, 'running');
        break;
      case 'skip':
        actions.updateWorkflowStepStatus(stepId, 'skipped');
        break;
    }
  };

  const handleStepSelect = (stepId: string) => {
    console.log('Step selected:', stepId);
    // Handle step selection (could open a modal with details)
  };

  const handleViewLogs = (stepId: string) => {
    console.log('View logs for step:', stepId);
    // Handle log viewing (could open a dedicated logs panel)
  };

  const handleReset = () => {
    actions.resetFactory();
    setIsPlaying(false);
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleClearLogs = () => {
    setLiveLogs([]);
  };

  const handleMetricAlert = (metric: SystemMetric) => {
    // Add alert log entry
    const newLog: LiveLogEntry = {
      id: `alert-${Date.now()}`,
      timestamp: new Date(),
      level: metric.status === 'critical' ? 'error' : 'warn',
      source: 'System Monitor',
      message: `${metric.name} usage is ${metric.status}: ${metric.value.toFixed(1)}${metric.unit}`
    };
    setLiveLogs(prev => [newLog, ...prev]);
  };

  return (
    <div className="layout-container">
      {/* Left Sidebar */}
      <aside className="sidebar-panel">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-text-primary mb-1">ThetaAI</h1>
          <p className="text-sm text-text-secondary">Software Factory</p>
        </div>
        
        <nav className="space-y-2">
          <Button variant="ghost" className="w-full justify-start">
            <Grid3X3 className="w-4 h-4 mr-2" />
            Dashboard
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Activity className="w-4 h-4 mr-2" />
            Analytics
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Terminal className="w-4 h-4 mr-2" />
            Console
          </Button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Connection Status Bar */}
        <div className={cn(
          "flex items-center justify-between px-6 py-2 text-sm border-b border-border",
          (!projectsLoading && !workflowsLoading && !agentsLoading)
            ? "bg-success/10 text-success" 
            : "bg-warning/10 text-warning"
        )}>
          <div className="flex items-center gap-2">
            {(!projectsLoading && !workflowsLoading && !agentsLoading) ? (
              <>
                <Wifi className="w-4 h-4" />
                <span>Connected to database - {projects?.length || 0} projects, {workflows?.length || 0} workflows, {agents?.length || 0} agents</span>
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4" />
                <span>Loading data from database...</span>
              </>
            )}
          </div>
          <div className="text-xs text-text-secondary">
            {(!projectsLoading && !workflowsLoading && !agentsLoading) ? 'Real database connected' : 'Fetching real data...'}
          </div>
        </div>
        <div className="h-full flex flex-col">
          {/* Pipeline Section - TOP PRIORITY */}
          <section className="mb-6">
            <Card className="card-ai p-6">
              <div className="mb-4">
                <h2 className="text-xl font-semibold text-text-primary mb-2">
                  AI Pipeline Execution
                </h2>
                <p className="text-text-secondary text-sm">
                  Real-time visualization of software factory workflow
                </p>
              </div>
              
              <PipelineStepper
                phases={state.pipeline.phases}
                currentPhaseIndex={state.pipeline.currentPhaseIndex}
                onPhaseClick={(phase) => handlePhaseClick(phase.id)}
              />
              
              {/* Progress Bar */}
              <div className="w-full mt-6">
                <div className="flex justify-between text-xs text-text-secondary mb-2">
                  <span>Overall Progress</span>
                  <span>{state.pipeline.progress}%</span>
                </div>
                <Progress 
                  value={state.pipeline.progress} 
                  className="progress-ai" 
                />
              </div>
            </Card>
          </section>

          {/* Main Content Area */}
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Agent Visualization Section */}
            <section>
              <Card className="card-ai p-6 h-full">
                <div className="mb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-semibold text-text-primary mb-1">
                        Agent Collaboration
                      </h2>
                      <p className="text-text-secondary text-sm">
                        Multi-agent orchestration network
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant={agentView === 'grid' ? 'default' : 'outline'}
                        size="sm"
                        className="h-8 px-2"
                        onClick={() => setAgentView('grid')}
                      >
                        <Grid3X3 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant={agentView === 'graph' ? 'default' : 'outline'}
                        size="sm"
                        className="h-8 px-2"
                        onClick={() => setAgentView('graph')}
                      >
                        <GitGraph className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                
                <div className="h-80">
                  {agentView === 'grid' ? (
                    <AgentVisualization
                      agents={state.agents}
                      onAgentClick={(agent) => handleAgentClick(agent.id)}
                    />
                  ) : (
                    <AgentGraph
                      agents={state.agentGraph.nodes}
                      edges={state.agentGraph.edges}
                      onAgentClick={(agent) => handleAgentClick(agent.id)}
                      onAgentDrag={handleAgentDrag}
                    />
                  )}
                </div>
              </Card>
            </section>

            {/* Enhanced Workflow Execution */}
            <section>
              <Card className="card-ai p-6 h-full">
                <div className="mb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-semibold text-text-primary mb-1">
                        Workflow Execution
                      </h2>
                      <p className="text-text-secondary text-sm">
                        Advanced step management and monitoring
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-text-secondary">
                        {state.workflow.steps.filter(s => s.status === 'completed').length}/{state.workflow.steps.length} completed
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="h-80 overflow-y-auto pr-2">
                  <EnhancedWorkflowPanel
                    steps={state.workflow.steps}
                    expandedStepId={state.workflow.expandedStepId || undefined}
                    isPlaying={isPlaying}
                    onStepToggle={handleStepToggle}
                    onStepAction={handleStepAction}
                    onStepSelect={handleStepSelect}
                    onViewLogs={handleViewLogs}
                  />
                </div>
              </Card>
            </section>
          </div>

          {/* Control Panel */}
          <section className="mt-6">
            <Card className="card-ai p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-text-primary">Factory Controls</h3>
                  <p className="text-sm text-text-secondary">
                    Manage AI pipeline execution
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setIsPlaying(false)}
                  >
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleReset}
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                  <Button 
                    size="sm" 
                    className={cn(
                      "bg-primary hover:bg-primary/90",
                      !isPlaying && "opacity-50 cursor-not-allowed"
                    )}
                    onClick={handlePlayPause}
                    disabled={!isPlaying}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    {isPlaying ? 'Running' : 'Resume'}
                  </Button>
                </div>
              </div>
            </Card>
          </section>
        </div>
      </main>

      {/* Right Panel */}
      <aside className="right-panel">
        <div className="h-full flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-border">
            <button
              className={cn(
                "flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors",
                activeTab === 'logs' 
                  ? "border-primary text-primary bg-primary/5" 
                  : "border-transparent text-text-secondary hover:text-text-primary hover:bg-bg-hover"
              )}
              onClick={() => setActiveTab('logs')}
            >
              <Terminal className="w-4 h-4 inline mr-2" />
              Live Logs
            </button>
            <button
              className={cn(
                "flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors",
                activeTab === 'health' 
                  ? "border-primary text-primary bg-primary/5" 
                  : "border-transparent text-text-secondary hover:text-text-primary hover:bg-bg-hover"
              )}
              onClick={() => setActiveTab('health')}
            >
              <Activity className="w-4 h-4 inline mr-2" />
              Health
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === 'logs' ? (
              <LiveLogConsole
                logs={liveLogs}
                maxHeight="h-full"
                autoScroll={!isLogsPaused}
                isPaused={isLogsPaused}
                onPause={() => setIsLogsPaused(true)}
                onResume={() => setIsLogsPaused(false)}
                onClear={handleClearLogs}
              />
            ) : (
              <SystemHealthMonitor
                metrics={DEFAULT_SYSTEM_METRICS}
                isConnected={isConnected()}
                onMetricAlert={handleMetricAlert}
              />
            )}
          </div>
        </div>
      </aside>
    </div>
  );
}