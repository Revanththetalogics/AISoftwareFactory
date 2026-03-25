'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useCreateProject } from '@/lib/hooks';
import { api } from '@/lib/api/client';

interface QuickStartButtonProps {
  variant?: 'default' | 'ai-action' | 'outline';
  size?: 'default' | 'sm' | 'lg';
  className?: string;
}

export function QuickStartButton({ 
  variant = 'ai-action', 
  size = 'default',
  className 
}: QuickStartButtonProps) {
  const [open, setOpen] = useState(false);
  const [idea, setIdea] = useState('');
  const [isStarting, setIsStarting] = useState(false);
  const createProject = useCreateProject();
  const router = useRouter();

  const generateProjectName = (idea: string): string => {
    // Simple name generation - could be enhanced with AI
    const words = idea.toLowerCase().split(' ').slice(0, 3);
    return words.join('-').replace(/[^a-z0-9-]/g, '');
  };

  const handleQuickStart = async () => {
    if (!idea.trim()) {
      toast.error('Please describe your idea');
      return;
    }

    setIsStarting(true);
    
    try {
      // Use the new single-prompt endpoint
      const response = await api.quickstartProject({
        idea: idea.trim(),
        template: 'saas_starter',
      });

      toast.success('Project created and AI workflow started!');
      
      // Close dialog and navigate to the project
      setOpen(false);
      router.push(`/projects/${response.project_id}`);
      
    } catch (error) {
      console.error('Quick start failed:', error);
      toast.error('Failed to start project. Please try again.');
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button variant={variant} size={size} className={className}>
            <Sparkles className="mr-2 h-4 w-4" />
            Quick Start
          </Button>
        }
      />
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-state-queued" />
            Start Building Your SaaS
          </DialogTitle>
          <DialogDescription>
            Describe your idea and our AI team will start building it immediately.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="idea">What do you want to build?</Label>
            <textarea
              id="idea"
              placeholder="e.g., A SaaS platform for managing freelance projects with time tracking, invoicing, and client collaboration..."
              value={idea}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setIdea(e.target.value)}
              rows={4}
              disabled={isStarting}
              className="w-full rounded-md border border-border-default bg-bg-panel px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-queued disabled:opacity-50"
            />
          </div>
          
          <div className="rounded-lg bg-state-queued-dim p-3 text-sm">
            <p className="font-medium text-text-primary">What happens next:</p>
            <ol className="mt-2 space-y-1 text-text-secondary list-decimal list-inside">
              <li>AI Product Manager analyzes your requirements</li>
              <li>AI Architect designs the system</li>
              <li>AI Developers generate production-ready code</li>
              <li>AI QA Engineer tests everything</li>
              <li>You get a working SaaS to customize</li>
            </ol>
          </div>
        </div>
        
        <div className="flex justify-end gap-3">
          <Button 
            variant="outline" 
            onClick={() => setOpen(false)}
            disabled={isStarting}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleQuickStart}
            disabled={isStarting || !idea.trim()}
            className="bg-gradient-to-r from-state-queued to-state-running"
          >
            {isStarting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Start Building
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
