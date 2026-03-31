'use client';

import { useState, useEffect } from 'react';
import { Pencil, Loader2 } from 'lucide-react';
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
import { Textarea } from '@/components/ui/textarea';
import { useUpdateProject } from '@/lib/hooks';
import type { Project } from '@/lib/types';

interface ProjectEditDialogProps {
  project: Project;
  trigger?: React.ReactNode;
}

export function ProjectEditDialog({ project, trigger }: ProjectEditDialogProps) {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: project.name,
    description: project.description || '',
    requirements: project.requirements || '',
  });

  const updateProject = useUpdateProject();

  useEffect(() => {
    if (open) {
      setFormData({
        name: project.name,
        description: project.description || '',
        requirements: project.requirements || '',
      });
    }
  }, [open, project]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast.error('Project name is required');
      return;
    }

    if (formData.name.length < 3) {
      toast.error('Project name must be at least 3 characters');
      return;
    }

    if (formData.name.length > 100) {
      toast.error('Project name must be less than 100 characters');
      return;
    }

    try {
      await updateProject.mutateAsync({
        id: project.id,
        data: formData,
      });
      toast.success('Project updated successfully');
      setOpen(false);
    } catch (error) {
      toast.error('Failed to update project');
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {trigger ? (
        <div onClick={() => setOpen(true)}>{trigger}</div>
      ) : (
        <Button
          variant="outline"
          size="sm"
          onClick={() => setOpen(true)}
          className="border-border-default text-text-secondary hover:text-text-primary"
        >
          <Pencil className="mr-2 h-4 w-4" />
          Edit
        </Button>
      )}
      <DialogContent className="sm:max-w-[600px] border-border-default bg-bg-base">
        <DialogHeader>
          <DialogTitle className="text-text-primary">Edit Project</DialogTitle>
          <DialogDescription className="text-text-secondary">
            Update your project details and requirements.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          <div>
            <Label htmlFor="name" className="text-sm font-medium text-text-secondary">
              Project Name *
            </Label>
            <Input
              id="name"
              placeholder="e.g., SaaS Analytics Platform"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="border-border-default bg-bg-elevated text-text-primary"
              required
              minLength={3}
              maxLength={100}
            />
          </div>
          <div>
            <Label htmlFor="description" className="text-sm font-medium text-text-secondary">
              Description
            </Label>
            <Textarea
              id="description"
              placeholder="Describe your project..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="border-border-default bg-bg-elevated text-text-primary min-h-[100px]"
              maxLength={500}
            />
            <p className="text-xs text-text-tertiary mt-1">
              {formData.description.length}/500 characters
            </p>
          </div>
          <div>
            <Label htmlFor="requirements" className="text-sm font-medium text-text-secondary">
              Requirements
            </Label>
            <Textarea
              id="requirements"
              placeholder="List your project requirements..."
              value={formData.requirements}
              onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
              className="border-border-default bg-bg-elevated text-text-primary min-h-[120px]"
            />
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
              disabled={updateProject.isPending}
              className="bg-gradient-to-r from-state-queued to-state-running"
            >
              {updateProject.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update Project'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
