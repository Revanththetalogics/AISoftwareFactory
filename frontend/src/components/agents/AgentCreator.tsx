'use client';

import { useState } from 'react';
import { Plus, Bot, Loader2, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useLLMModels, useCreateAgent } from '@/lib/hooks';

const TASK_TYPE_OPTIONS = [
  { value: 'coding', label: 'Coding', description: 'DeepSeek Coder - Best for code generation' },
  { value: 'code_review', label: 'Code Review', description: 'DeepSeek Coder - Best for code review' },
  { value: 'reasoning', label: 'Reasoning', description: 'Mixtral - Best for complex reasoning' },
  { value: 'chat', label: 'Chat', description: 'Qwen - Good for general chat' },
  { value: 'general', label: 'General', description: 'Llama 3.2 - General purpose' },
];

export function AgentCreator() {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    goal: '',
    backstory: '',
    llm_task_type: 'general',
    allow_delegation: true,
  });

  const { data: llmModels } = useLLMModels();
  const createAgent = useCreateAgent();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.role || !formData.goal || !formData.backstory) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      await createAgent.mutateAsync(formData);
      setOpen(false);
      setFormData({
        name: '',
        role: '',
        goal: '',
        backstory: '',
        llm_task_type: 'general',
        allow_delegation: true,
      });
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button variant="ai-action" onClick={() => setOpen(true)}>
        <Plus className="mr-2 h-4 w-4" />
        Create Agent
      </Button>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-state-queued" />
            Create Custom Agent
          </DialogTitle>
          <DialogDescription>
            Define a new AI agent with a specific role and capabilities. The LLM model will be selected automatically based on the task type.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Agent Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Security Expert"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-bg-panel"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role *</Label>
              <Input
                id="role"
                placeholder="e.g., Security Engineer"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="bg-bg-panel"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="goal">Goal *</Label>
            <textarea
              id="goal"
              placeholder="What does this agent aim to accomplish? e.g., Identify and fix security vulnerabilities in code"
              value={formData.goal}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({ ...formData, goal: e.target.value })}
              rows={2}
              className="w-full rounded-md border border-border-default bg-bg-panel px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-queued"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="backstory">Backstory *</Label>
            <textarea
              id="backstory"
              placeholder="Describe the agent's expertise and background..."
              value={formData.backstory}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({ ...formData, backstory: e.target.value })}
              rows={3}
              className="w-full rounded-md border border-border-default bg-bg-panel px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-queued"
            />
          </div>

          <div className="space-y-2">
            <Label>Task Type / LLM Model</Label>
            <div className="grid grid-cols-1 gap-2">
              {TASK_TYPE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, llm_task_type: option.value })}
                  className={`flex items-center justify-between rounded-lg border p-3 text-left transition-colors ${
                    formData.llm_task_type === option.value
                      ? 'border-state-queued bg-state-queued-dim'
                      : 'border-border-default bg-bg-panel hover:border-border-hover'
                  }`}
                >
                  <div>
                    <p className={`font-medium ${formData.llm_task_type === option.value ? 'text-state-queued' : 'text-text-primary'}`}>
                      {option.label}
                    </p>
                    <p className="text-xs text-text-secondary">{option.description}</p>
                  </div>
                  {formData.llm_task_type === option.value && (
                    <Sparkles className="h-4 w-4 text-state-queued" />
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="allow_delegation"
              checked={formData.allow_delegation}
              onChange={(e) => setFormData({ ...formData, allow_delegation: e.target.checked })}
              className="rounded border-border-default"
            />
            <Label htmlFor="allow_delegation" className="text-sm text-text-secondary">
              Allow this agent to delegate tasks to other agents
            </Label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={createAgent.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createAgent.isPending}
              className="bg-gradient-to-r from-state-queued to-state-running"
            >
              {createAgent.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-4 w-4" />
                  Create Agent
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
