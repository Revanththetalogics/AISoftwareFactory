'use client';

import { useState } from 'react';
import { Rocket, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useCreateDeployment } from '@/lib/hooks/useDeployments';
import { useProjects } from '@/lib/hooks';

export function DeploymentCreateDialog() {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    project_id: '',
    environment: 'staging',
    version: '',
  });

  const { data: projects = [] } = useProjects();
  const createDeployment = useCreateDeployment();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.project_id) {
      toast.error('Please select a project');
      return;
    }

    if (!formData.version.trim()) {
      toast.error('Please enter a version');
      return;
    }

    try {
      await createDeployment.mutateAsync(formData);
      toast.success(`Deployment to ${formData.environment} started successfully`);
      setFormData({ project_id: '', environment: 'staging', version: '' });
      setOpen(false);
    } catch (error) {
      toast.error('Failed to create deployment');
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button
        variant="ai-action"
        onClick={() => setOpen(true)}
      >
        <Rocket className="mr-2 h-4 w-4" />
        Deploy Project
      </Button>
      <DialogContent className="sm:max-w-[500px] border-border-default bg-bg-base">
        <DialogHeader>
          <DialogTitle className="text-text-primary flex items-center gap-2">
            <Rocket className="h-5 w-5 text-state-running" />
            Create Deployment
          </DialogTitle>
          <DialogDescription className="text-text-secondary">
            Deploy your project to a specific environment.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          <div>
            <Label htmlFor="project" className="text-sm font-medium text-text-secondary">
              Project *
            </Label>
            <Select
              value={formData.project_id}
              onValueChange={(value) => setFormData({ ...formData, project_id: value })}
            >
              <SelectTrigger className="border-border-default bg-bg-elevated text-text-primary">
                <SelectValue placeholder="Select a project" />
              </SelectTrigger>
              <SelectContent className="border-border-default bg-bg-elevated">
                {projects.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="environment" className="text-sm font-medium text-text-secondary">
              Environment *
            </Label>
            <Select
              value={formData.environment}
              onValueChange={(value) => setFormData({ ...formData, environment: value })}
            >
              <SelectTrigger className="border-border-default bg-bg-elevated text-text-primary">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="border-border-default bg-bg-elevated">
                <SelectItem value="development">Development</SelectItem>
                <SelectItem value="staging">Staging</SelectItem>
                <SelectItem value="production">Production</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="version" className="text-sm font-medium text-text-secondary">
              Version *
            </Label>
            <Input
              id="version"
              placeholder="e.g., v1.0.0 or main"
              value={formData.version}
              onChange={(e) => setFormData({ ...formData, version: e.target.value })}
              className="border-border-default bg-bg-elevated text-text-primary"
              required
            />
            <p className="text-xs text-text-tertiary mt-1">
              Enter a version tag or branch name
            </p>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              className="border-border-default text-text-secondary"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createDeployment.isPending}
              className="bg-gradient-to-r from-state-queued to-state-running"
            >
              {createDeployment.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deploying...
                </>
              ) : (
                <>
                  <Rocket className="mr-2 h-4 w-4" />
                  Deploy
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
