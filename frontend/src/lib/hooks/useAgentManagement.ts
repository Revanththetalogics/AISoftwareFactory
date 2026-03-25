'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { toast } from 'sonner';

const AGENT_MANAGEMENT_KEY = 'agent-management';
const CUSTOM_AGENTS_KEY = 'custom-agents';
const CUSTOM_CREWS_KEY = 'custom-crews';
const LLM_MODELS_KEY = 'llm-models';

// LLM Models
export function useLLMModels() {
  return useQuery({
    queryKey: [AGENT_MANAGEMENT_KEY, LLM_MODELS_KEY],
    queryFn: () => api.getLLMModels(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Custom Agents
export function useCustomAgents() {
  return useQuery({
    queryKey: [AGENT_MANAGEMENT_KEY, CUSTOM_AGENTS_KEY],
    queryFn: () => api.getCustomAgents(),
    staleTime: 5000,
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      name: string;
      role: string;
      goal: string;
      backstory: string;
      llm_task_type?: string;
      allow_delegation?: boolean;
    }) => api.createAgent(data),
    onSuccess: (result) => {
      toast.success(`Agent "${result.name}" created with ${result.llm_model}`);
      queryClient.invalidateQueries({ queryKey: [AGENT_MANAGEMENT_KEY, CUSTOM_AGENTS_KEY] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to create agent: ${error.message}`);
    },
  });
}

export function useDeleteAgent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (agentId: string) => api.deleteAgent(agentId),
    onSuccess: () => {
      toast.success('Agent deleted');
      queryClient.invalidateQueries({ queryKey: [AGENT_MANAGEMENT_KEY, CUSTOM_AGENTS_KEY] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete agent: ${error.message}`);
    },
  });
}

// Custom Crews
export function useCustomCrews() {
  return useQuery({
    queryKey: [AGENT_MANAGEMENT_KEY, CUSTOM_CREWS_KEY],
    queryFn: () => api.getCustomCrews(),
    staleTime: 5000,
  });
}

export function useCreateCrew() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      name: string;
      description: string;
      agent_ids: string[];
      process?: 'sequential' | 'hierarchical' | 'parallel';
    }) => api.createCrew(data),
    onSuccess: (result) => {
      toast.success(`Crew "${result.name}" created with ${result.agent_count} agents`);
      queryClient.invalidateQueries({ queryKey: [AGENT_MANAGEMENT_KEY, CUSTOM_CREWS_KEY] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to create crew: ${error.message}`);
    },
  });
}

export function useDeleteCrew() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (crewId: string) => api.deleteCrew(crewId),
    onSuccess: () => {
      toast.success('Crew deleted');
      queryClient.invalidateQueries({ queryKey: [AGENT_MANAGEMENT_KEY, CUSTOM_CREWS_KEY] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete crew: ${error.message}`);
    },
  });
}
