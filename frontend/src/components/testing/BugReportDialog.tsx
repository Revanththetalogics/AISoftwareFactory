'use client';

import { useState } from 'react';
import { Bug, Loader2 } from 'lucide-react';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useCreateBug } from '@/lib/hooks/useTesting';
import { useProjects } from '@/lib/hooks';

export function BugReportDialog() {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    projectId: '',
    title: '',
    description: '',
    severity: 'medium',
    filePath: '',
    lineNumber: '',
  });

  const { data: projects = [] } = useProjects();
  const createBug = useCreateBug();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.projectId) {
      toast.error('Please select a project');
      return;
    }

    if (!formData.title.trim()) {
      toast.error('Please enter a bug title');
      return;
    }

    if (!formData.description.trim()) {
      toast.error('Please enter a bug description');
      return;
    }

    try {
      await createBug.mutateAsync({
        projectId: formData.projectId,
        title: formData.title,
        description: formData.description,
        severity: formData.severity,
        filePath: formData.filePath || undefined,
        lineNumber: formData.lineNumber ? parseInt(formData.lineNumber) : undefined,
      });
      toast.success('Bug reported successfully');
      setFormData({
        projectId: '',
        title: '',
        description: '',
        severity: 'medium',
        filePath: '',
        lineNumber: '',
      });
      setOpen(false);
    } catch (error) {
      toast.error('Failed to report bug');
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button
        variant="outline"
        onClick={() => setOpen(true)}
        className="border-border-default text-text-secondary"
      >
        <Bug className="mr-2 h-4 w-4" />
        Report Bug
      </Button>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto border-border-default bg-bg-base">
        <DialogHeader>
          <DialogTitle className="text-text-primary flex items-center gap-2">
            <Bug className="h-5 w-5 text-state-error" />
            Report a Bug
          </DialogTitle>
          <DialogDescription className="text-text-secondary">
            Report a bug found during testing or development.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          <div>
            <Label htmlFor="project" className="text-sm font-medium text-text-secondary">
              Project *
            </Label>
            <Select
              value={formData.projectId}
              onValueChange={(value) => setFormData({ ...formData, projectId: value })}
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
            <Label htmlFor="severity" className="text-sm font-medium text-text-secondary">
              Severity *
            </Label>
            <Select
              value={formData.severity}
              onValueChange={(value) => setFormData({ ...formData, severity: value })}
            >
              <SelectTrigger className="border-border-default bg-bg-elevated text-text-primary">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="border-border-default bg-bg-elevated">
                <SelectItem value="critical">🔴 Critical</SelectItem>
                <SelectItem value="high">🟠 High</SelectItem>
                <SelectItem value="medium">🟡 Medium</SelectItem>
                <SelectItem value="low">🔵 Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="title" className="text-sm font-medium text-text-secondary">
              Bug Title *
            </Label>
            <Input
              id="title"
              placeholder="e.g., Memory leak in WebSocket handler"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="border-border-default bg-bg-elevated text-text-primary"
              required
            />
          </div>
          <div>
            <Label htmlFor="description" className="text-sm font-medium text-text-secondary">
              Description *
            </Label>
            <Textarea
              id="description"
              placeholder="Describe the bug, steps to reproduce, and expected behavior..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="border-border-default bg-bg-elevated text-text-primary min-h-[120px]"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="filePath" className="text-sm font-medium text-text-secondary">
                File Path (Optional)
              </Label>
              <Input
                id="filePath"
                placeholder="e.g., src/services/websocket.ts"
                value={formData.filePath}
                onChange={(e) => setFormData({ ...formData, filePath: e.target.value })}
                className="border-border-default bg-bg-elevated text-text-primary"
              />
            </div>
            <div>
              <Label htmlFor="lineNumber" className="text-sm font-medium text-text-secondary">
                Line Number (Optional)
              </Label>
              <Input
                id="lineNumber"
                type="number"
                placeholder="e.g., 42"
                value={formData.lineNumber}
                onChange={(e) => setFormData({ ...formData, lineNumber: e.target.value })}
                className="border-border-default bg-bg-elevated text-text-primary"
              />
            </div>
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
              disabled={createBug.isPending}
              className="bg-state-error hover:bg-state-error/90"
            >
              {createBug.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Reporting...
                </>
              ) : (
                <>
                  <Bug className="mr-2 h-4 w-4" />
                  Report Bug
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
