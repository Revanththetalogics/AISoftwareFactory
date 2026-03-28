'use client';

import { useState } from 'react';
import { Play, Pause, RotateCcw, Grid3X3, GitGraph } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { PipelineStepper } from '@/components/factory/PipelineStepper';
import { AgentVisualization } from '@/components/factory/AgentVisualization';
import { AgentGraph } from '@/components/factory/AgentGraph';
import { EnhancedWorkflowPanel } from '@/components/factory/EnhancedWorkflowPanel';
import { useFactoryState, useFactoryWebSocket } from '@/hooks/useFactoryState';
import { cn } from '@/lib/utils';

export default function SuperEnhancedDashboardPage() {
  const { state, actions } = useFactoryState();
  const [isPlaying, setIsPlaying] = useState(true);
  const [agentView, setAgentView] = useState<'grid' | 'graph'>('grid');

  // Initialize WebSocket simulation
  useFactoryWebSocket(actions);

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

  return (
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
  );
}