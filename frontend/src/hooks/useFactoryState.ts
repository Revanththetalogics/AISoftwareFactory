'use client';

import { useEffect, useCallback, useReducer } from 'react';
import { PipelinePhase, PipelinePhaseStatus } from '@/components/factory/PipelineStepper';
import { AgentNode, AgentStatus } from '@/components/factory/AgentVisualization';
import { AgentGraphNode, AgentGraphEdge } from '@/components/factory/AgentGraph';
import { EnhancedWorkflowStep, EnhancedWorkflowStepStatus, LogEntry } from '@/components/factory/EnhancedWorkflowPanel';

// Factory State Types
export interface FactoryState {
  pipeline: {
    phases: PipelinePhase[];
    currentPhaseIndex: number;
    progress: number;
  };
  agents: AgentNode[];
  agentGraph: {
    nodes: AgentGraphNode[];
    edges: AgentGraphEdge[];
  };
  workflow: {
    steps: EnhancedWorkflowStep[];
    expandedStepId: string | null;
  };
  system: {
    cpu: number;
    memory: number;
    storage: number;
  };
}

// Factory Actions
export type FactoryAction =
  | { type: 'UPDATE_PIPELINE_PHASE'; payload: { phaseId: string; status: PipelinePhaseStatus } }
  | { type: 'SET_CURRENT_PHASE'; payload: number }
  | { type: 'UPDATE_AGENT_STATUS'; payload: { agentId: string; status: AgentStatus; currentTask?: string } }
  | { type: 'UPDATE_AGENT_POSITION'; payload: { agentId: string; x: number; y: number } }
  | { type: 'TOGGLE_WORKFLOW_STEP'; payload: string }
  | { type: 'UPDATE_WORKFLOW_STEP_STATUS'; payload: { stepId: string; status: EnhancedWorkflowStepStatus } }
  | { type: 'ADD_WORKFLOW_LOG'; payload: { stepId: string; log: LogEntry } }
  | { type: 'UPDATE_SYSTEM_METRICS'; payload: { cpu: number; memory: number; storage: number } }
  | { type: 'RESET_FACTORY' };

// Initial Factory Data
export const INITIAL_FACTORY_STATE: FactoryState = {
  pipeline: {
    phases: [
      { id: '1', name: 'IDEA', status: 'completed' },
      { id: '2', name: 'REQUIREMENTS', status: 'completed' },
      { id: '3', name: 'ARCHITECTURE', status: 'running' },
      { id: '4', name: 'IMPLEMENTATION', status: 'pending' },
      { id: '5', name: 'TESTING', status: 'pending' },
      { id: '6', name: 'DEPLOYMENT', status: 'pending' },
      { id: '7', name: 'COMPLETE', status: 'pending' },
    ],
    currentPhaseIndex: 2,
    progress: 35,
  },
  agents: [
    { id: '1', name: 'CEO', role: 'Orchestrator', status: 'idle' },
    { id: '2', name: 'Product Manager', role: 'Planner', status: 'running', currentTask: 'Analyzing requirements' },
    { id: '3', name: 'Architect', role: 'Designer', status: 'idle' },
    { id: '4', name: 'Engineers', role: 'Implementers', status: 'idle' },
    { id: '5', name: 'QA Team', role: 'Validators', status: 'idle' },
    { id: '6', name: 'DevOps', role: 'Deployers', status: 'idle' },
  ],
  agentGraph: {
    nodes: [
      { 
        id: '1', 
        name: 'CEO', 
        role: 'Orchestrator', 
        status: 'idle',
        x: 50, 
        y: 10,
        connections: ['2', '3']
      },
      { 
        id: '2', 
        name: 'Product Manager', 
        role: 'Planner', 
        status: 'running', 
        currentTask: 'Analyzing requirements',
        x: 30, 
        y: 30,
        connections: ['1', '3', '4']
      },
      { 
        id: '3', 
        name: 'Architect', 
        role: 'Designer', 
        status: 'idle',
        x: 70, 
        y: 30,
        connections: ['1', '2', '4', '5']
      },
      { 
        id: '4', 
        name: 'Engineers', 
        role: 'Implementers', 
        status: 'idle',
        x: 20, 
        y: 60,
        connections: ['2', '3', '5']
      },
      { 
        id: '5', 
        name: 'QA Team', 
        role: 'Validators', 
        status: 'idle',
        x: 60, 
        y: 60,
        connections: ['3', '4', '6']
      },
      { 
        id: '6', 
        name: 'DevOps', 
        role: 'Deployers', 
        status: 'idle',
        x: 40, 
        y: 85,
        connections: ['5']
      },
    ],
    edges: [
      { source: '1', target: '2', strength: 0.8 },
      { source: '1', target: '3', strength: 0.7 },
      { source: '2', target: '3', strength: 0.9 },
      { source: '2', target: '4', strength: 0.6 },
      { source: '3', target: '4', strength: 0.8 },
      { source: '3', target: '5', strength: 0.7 },
      { source: '4', target: '5', strength: 0.6 },
      { source: '5', target: '6', strength: 0.9 },
    ]
  },
  workflow: {
    steps: [
      { 
        id: '1', 
        title: 'Project Initialization', 
        status: 'completed', 
        duration: '2m 34s',
        description: 'Environment setup and project scaffolding'
      },
      { 
        id: '2', 
        title: 'Requirements Analysis', 
        status: 'completed', 
        duration: '5m 12s',
        description: 'Gathering and documenting project requirements'
      },
      { 
        id: '3', 
        title: 'System Architecture', 
        status: 'running', 
        duration: 'In progress',
        description: 'Designing system architecture and components',
        logs: [
          { 
            id: '1', 
            timestamp: new Date(), 
            level: 'info', 
            message: 'Initializing architecture design...',
            source: 'Architect Agent'
          },
          { 
            id: '2', 
            timestamp: new Date(Date.now() - 30000), 
            level: 'success', 
            message: 'Core components identified',
            source: 'System Analyzer'
          },
          { 
            id: '3', 
            timestamp: new Date(Date.now() - 15000), 
            level: 'info', 
            message: 'Generating system diagrams...',
            source: 'Design Engine'
          }
        ]
      },
      { 
        id: '4', 
        title: 'API Development', 
        status: 'pending', 
        duration: 'Pending',
        description: 'Building RESTful API endpoints'
      },
      { 
        id: '5', 
        title: 'Frontend Implementation', 
        status: 'pending', 
        duration: 'Pending',
        description: 'Creating user interface components'
      },
    ],
    expandedStepId: '3',
  },
  system: {
    cpu: 45,
    memory: 62,
    storage: 38,
  },
};

// Reducer
export function factoryReducer(state: FactoryState, action: FactoryAction): FactoryState {
  switch (action.type) {
    case 'UPDATE_PIPELINE_PHASE':
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          phases: state.pipeline.phases.map(phase =>
            phase.id === action.payload.phaseId
              ? { ...phase, status: action.payload.status }
              : phase
          ),
        },
      };
    
    case 'SET_CURRENT_PHASE':
      return {
        ...state,
        pipeline: {
          ...state.pipeline,
          currentPhaseIndex: action.payload,
        },
      };
    
    case 'UPDATE_AGENT_STATUS':
      return {
        ...state,
        agents: state.agents.map(agent =>
          agent.id === action.payload.agentId
            ? { 
                ...agent, 
                status: action.payload.status,
                currentTask: action.payload.currentTask
              }
            : agent
        ),
        agentGraph: {
          ...state.agentGraph,
          nodes: state.agentGraph.nodes.map(node =>
            node.id === action.payload.agentId
              ? { 
                  ...node, 
                  status: action.payload.status,
                  currentTask: action.payload.currentTask
                }
              : node
          )
        }
      };
    
    case 'UPDATE_AGENT_POSITION':
      return {
        ...state,
        agentGraph: {
          ...state.agentGraph,
          nodes: state.agentGraph.nodes.map(node =>
            node.id === action.payload.agentId
              ? { ...node, x: action.payload.x, y: action.payload.y }
              : node
          )
        }
      };
    
    case 'TOGGLE_WORKFLOW_STEP':
      return {
        ...state,
        workflow: {
          ...state.workflow,
          expandedStepId: state.workflow.expandedStepId === action.payload 
            ? null 
            : action.payload,
        },
      };
    
    case 'UPDATE_WORKFLOW_STEP_STATUS':
      return {
        ...state,
        workflow: {
          ...state.workflow,
          steps: state.workflow.steps.map(step =>
            step.id === action.payload.stepId
              ? { ...step, status: action.payload.status }
              : step
          )
        }
      };
    
    case 'ADD_WORKFLOW_LOG':
      return {
        ...state,
        workflow: {
          ...state.workflow,
          steps: state.workflow.steps.map(step =>
            step.id === action.payload.stepId
              ? { 
                  ...step, 
                  logs: [...(step.logs || []), action.payload.log]
                }
              : step
          )
        }
      };
    
    case 'UPDATE_SYSTEM_METRICS':
      return {
        ...state,
        system: action.payload,
      };
    
    case 'RESET_FACTORY':
      return INITIAL_FACTORY_STATE;
    
    default:
      return state;
  }
}

// Hook for factory state management
export function useFactoryState() {
  const [state, dispatch] = useReducer(factoryReducer, INITIAL_FACTORY_STATE);

  const updatePipelinePhase = useCallback((phaseId: string, status: PipelinePhaseStatus) => {
    dispatch({ type: 'UPDATE_PIPELINE_PHASE', payload: { phaseId, status } });
  }, []);

  const setCurrentPhase = useCallback((index: number) => {
    dispatch({ type: 'SET_CURRENT_PHASE', payload: index });
  }, []);

  const updateAgentStatus = useCallback((agentId: string, status: AgentStatus, currentTask?: string) => {
    dispatch({ type: 'UPDATE_AGENT_STATUS', payload: { agentId, status, currentTask } });
  }, []);

  const updateAgentPosition = useCallback((agentId: string, x: number, y: number) => {
    dispatch({ type: 'UPDATE_AGENT_POSITION', payload: { agentId, x, y } });
  }, []);

  const toggleWorkflowStep = useCallback((stepId: string) => {
    dispatch({ type: 'TOGGLE_WORKFLOW_STEP', payload: stepId });
  }, []);

  const updateWorkflowStepStatus = useCallback((stepId: string, status: EnhancedWorkflowStepStatus) => {
    dispatch({ type: 'UPDATE_WORKFLOW_STEP_STATUS', payload: { stepId, status } });
  }, []);

  const addWorkflowLog = useCallback((stepId: string, log: LogEntry) => {
    dispatch({ type: 'ADD_WORKFLOW_LOG', payload: { stepId, log } });
  }, []);

  const updateSystemMetrics = useCallback((cpu: number, memory: number, storage: number) => {
    dispatch({ type: 'UPDATE_SYSTEM_METRICS', payload: { cpu, memory, storage } });
  }, []);

  const resetFactory = useCallback(() => {
    dispatch({ type: 'RESET_FACTORY' });
  }, []);

  return {
    state,
    dispatch, // Expose dispatch for WebSocket integration
    actions: {
      updatePipelinePhase,
      setCurrentPhase,
      updateAgentStatus,
      updateAgentPosition,
      toggleWorkflowStep,
      updateWorkflowStepStatus,
      addWorkflowLog,
      updateSystemMetrics,
      resetFactory,
    },
  };
}

// Hook for real-time updates
export function useFactoryWebSocket(factoryActions: ReturnType<typeof useFactoryState>['actions']) {
// Real-time updates are now handled by useFactoryWebSocket hook
// Mock WebSocket simulator removed - using real backend WebSocket connection
}