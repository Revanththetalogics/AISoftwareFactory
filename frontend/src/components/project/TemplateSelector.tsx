'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Rocket, Server, Brain, ArrowRight, Clock, CheckCircle2 } from 'lucide-react';
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
import { useCreateProject } from '@/lib/hooks';
import { api } from '@/lib/api/client';
import { cn } from '@/lib/utils';

interface Template {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  deployTime: string;
  stack: string[];
  features: string[];
  defaultRequirements: string;
}

const templates: Template[] = [
  {
    id: 'saas-starter',
    name: 'SaaS Starter',
    description: 'Full-stack SaaS with auth, billing, and dashboard',
    icon: Rocket,
    deployTime: '3 min',
    stack: ['Next.js', 'FastAPI', 'PostgreSQL', 'Stripe'],
    features: ['Authentication', 'Billing', 'Admin Dashboard', 'API'],
    defaultRequirements: 'Build a SaaS application with user authentication, subscription billing via Stripe, and an admin dashboard. Include user roles (admin, user), email notifications, and responsive design.',
  },
  {
    id: 'api-service',
    name: 'API Service',
    description: 'High-performance API with caching and docs',
    icon: Server,
    deployTime: '2 min',
    stack: ['FastAPI', 'Redis', 'PostgreSQL', 'Docker'],
    features: ['REST API', 'Caching', 'Auto Docs', 'Rate Limiting'],
    defaultRequirements: 'Build a scalable REST API service with FastAPI. Include Redis caching, automatic API documentation, rate limiting, and Docker containerization.',
  },
  {
    id: 'ai-app',
    name: 'AI Application',
    description: 'AI-powered app with RAG and chat interface',
    icon: Brain,
    deployTime: '4 min',
    stack: ['Next.js', 'OpenAI', 'Vector DB', 'LangChain'],
    features: ['Chat Interface', 'RAG Pipeline', 'File Upload', 'Streaming'],
    defaultRequirements: 'Build an AI application with a chat interface using OpenAI GPT-4. Include RAG (Retrieval Augmented Generation) with vector database for knowledge base, file upload for documents, and streaming responses.',
  },
];

interface TemplateCardProps {
  template: Template;
  isSelected: boolean;
  onClick: () => void;
}

function TemplateCard({ template, isSelected, onClick }: TemplateCardProps) {
  const Icon = template.icon;
  
  return (
    <div
      onClick={onClick}
      className={cn(
        'relative cursor-pointer rounded-lg border p-4 transition-all',
        isSelected
          ? 'border-state-queued bg-state-queued-dim ring-2 ring-state-queued'
          : 'border-border-default bg-bg-panel hover:border-border-hover hover:bg-bg-hover'
      )}
    >
      {isSelected && (
        <div className="absolute top-2 right-2">
          <CheckCircle2 className="h-5 w-5 text-state-queued" />
        </div>
      )}
      
      <div className="flex items-start gap-4">
        <div className={cn(
          'flex h-12 w-12 shrink-0 items-center justify-center rounded-lg',
          isSelected ? 'bg-state-queued text-white' : 'bg-bg-base text-text-secondary'
        )}>
          <Icon className="h-6 w-6" />
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-text-primary">{template.name}</h3>
          <p className="text-sm text-text-secondary mt-1">{template.description}</p>
          
          <div className="flex items-center gap-4 mt-3 text-xs text-text-tertiary">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {template.deployTime}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-1 mt-3">
            {template.stack.map((tech) => (
              <span
                key={tech}
                className="px-2 py-0.5 text-xs rounded-full bg-bg-base text-text-secondary"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function TemplateSelector() {
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const createProject = useCreateProject();
  const router = useRouter();

  const handleCreateFromTemplate = async () => {
    if (!selectedTemplate) return;

    setIsCreating(true);
    
    try {
      const project = await createProject.mutateAsync({
        name: selectedTemplate.id,
        description: selectedTemplate.description,
        requirements: selectedTemplate.defaultRequirements,
      });

      toast.success(`Created ${selectedTemplate.name} project!`);

      // Activate and start workflow
      await api.activateProject(project.id);
      await api.executeWorkflow({
        project_id: project.id,
        phase: 'requirements',
        async_execution: true,
      });

      toast.success('AI team is building your project!');
      
      setOpen(false);
      router.push(`/projects/${project.id}`);
      
    } catch (error) {
      console.error('Template creation failed:', error);
      toast.error('Failed to create project from template');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button variant="outline">
            Use Template
          </Button>
        }
      />
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Choose a Template</DialogTitle>
          <DialogDescription>
            Start with a pre-configured template to accelerate development.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="grid gap-4">
            {templates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                isSelected={selectedTemplate?.id === template.id}
                onClick={() => setSelectedTemplate(template)}
              />
            ))}
          </div>
          
          {selectedTemplate && (
            <div className="rounded-lg bg-state-queued-dim p-4">
              <h4 className="font-medium text-text-primary mb-2">
                Included Features:
              </h4>
              <ul className="grid grid-cols-2 gap-2">
                {selectedTemplate.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm text-text-secondary">
                    <CheckCircle2 className="h-4 w-4 text-state-success" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        <div className="flex justify-end gap-3">
          <Button 
            variant="outline" 
            onClick={() => setOpen(false)}
            disabled={isCreating}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreateFromTemplate}
            disabled={!selectedTemplate || isCreating}
            className="bg-gradient-to-r from-state-queued to-state-running"
          >
            {isCreating ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Creating...
              </>
            ) : (
              <>
                Create Project
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
