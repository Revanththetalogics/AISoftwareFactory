'use client';

import { useState } from 'react';
import { Plus, Users, Loader2, Check } from 'lucide-react';
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
import { useCustomAgents, useCreateCrew } from '@/lib/hooks';
import { cn } from '@/lib/utils';

const PROCESS_OPTIONS = [
  { value: 'sequential', label: 'Sequential', description: 'Agents work one after another' },
  { value: 'hierarchical', label: 'Hierarchical', description: 'Manager agent coordinates others' },
  { value: 'parallel', label: 'Parallel', description: 'Agents work simultaneously' },
];

export function CrewCreator() {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    agent_ids: [] as string[],
    process: 'sequential' as 'sequential' | 'hierarchical' | 'parallel',
  });

  const { data: agents = [] } = useCustomAgents();
  const createCrew = useCreateCrew();

  const toggleAgent = (agentId: string) => {
    setFormData((prev) => ({
      ...prev,
      agent_ids: prev.agent_ids.includes(agentId)
        ? prev.agent_ids.filter((id) => id !== agentId)
        : [...prev.agent_ids, agentId],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.description || formData.agent_ids.length === 0) {
      toast.error('Please fill in all fields and select at least one agent');
      return;
    }

    try {
      await createCrew.mutateAsync(formData);
      setOpen(false);
      setFormData({
        name: '',
        description: '',
        agent_ids: [],
        process: 'sequential',
      });
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <>
      <Button variant="ai-action" onClick={() => setOpen(true)}>
        <Plus className="mr-2 h-4 w-4" />
        Create Crew
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-state-queued" />
              Create Custom Crew
            </DialogTitle>
            <DialogDescription>
              Combine multiple agents into a collaborative crew for specific tasks.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Crew Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Security Audit Team"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-bg-panel"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <textarea
                id="description"
                placeholder="What does this crew do?"
                value={formData.description}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="w-full rounded-md border border-border-default bg-bg-panel px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-queued"
              />
            </div>

            <div className="space-y-2">
              <Label>Process Type</Label>
              <div className="grid grid-cols-1 gap-2">
                {PROCESS_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, process: option.value as typeof formData.process })}
                    className={`flex items-center justify-between rounded-lg border p-3 text-left transition-colors ${
                      formData.process === option.value
                        ? 'border-state-queued bg-state-queued-dim'
                        : 'border-border-default bg-bg-panel hover:border-border-hover'
                    }`}
                  >
                    <div>
                      <p className={`font-medium ${formData.process === option.value ? 'text-state-queued' : 'text-text-primary'}`}>
                        {option.label}
                      </p>
                      <p className="text-xs text-text-secondary">{option.description}</p>
                    </div>
                    {formData.process === option.value && (
                      <Check className="h-4 w-4 text-state-queued" />
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Select Agents * ({formData.agent_ids.length} selected)</Label>
              {agents.length === 0 ? (
                <p className="text-sm text-text-secondary italic">No custom agents available. Create agents first.</p>
              ) : (
                <div className="grid grid-cols-1 gap-2 max-h-[200px] overflow-y-auto">
                  {agents.map((agent) => (
                    <button
                      key={agent.agent_id}
                      type="button"
                      onClick={() => toggleAgent(agent.agent_id)}
                      className={cn(
                        'flex items-center justify-between rounded-lg border p-3 text-left transition-colors',
                        formData.agent_ids.includes(agent.agent_id)
                          ? 'border-state-queued bg-state-queued-dim'
                          : 'border-border-default bg-bg-panel hover:border-border-hover'
                      )}
                    >
                      <div>
                        <p className={cn(
                          'font-medium',
                          formData.agent_ids.includes(agent.agent_id) ? 'text-state-queued' : 'text-text-primary'
                        )}>
                          {agent.name}
                        </p>
                        <p className="text-xs text-text-secondary">{agent.role} • {agent.llm_model}</p>
                      </div>
                      {formData.agent_ids.includes(agent.agent_id) && (
                        <Check className="h-4 w-4 text-state-queued" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                disabled={createCrew.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createCrew.isPending || formData.agent_ids.length === 0}
                className="bg-gradient-to-r from-state-queued to-state-running"
              >
                {createCrew.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Users className="mr-2 h-4 w-4" />
                    Create Crew
                  </>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
