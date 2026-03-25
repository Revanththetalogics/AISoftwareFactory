'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Lightbulb, 
  MessageSquare, 
  ListChecks, 
  Layers, 
  ArrowRight, 
  ArrowLeft,
  Loader2,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCreateProject } from '@/lib/hooks';
import { api } from '@/lib/api/client';

type WizardStep = 'idea' | 'clarify' | 'features' | 'tech' | 'review';

interface ClarificationQuestion {
  id: string;
  question: string;
  options?: string[];
}

interface SuggestedFeature {
  id: string;
  name: string;
  description: string;
  priority: 'must-have' | 'nice-to-have';
}

interface TechRecommendation {
  category: string;
  options: string[];
  recommended: string;
}

interface WizardData {
  idea: string;
  answers: Record<string, string>;
  selectedFeatures: string[];
  selectedTech: Record<string, string>;
}

// Mock AI responses - in production, these would come from API
const mockClarifications: ClarificationQuestion[] = [
  {
    id: 'target-users',
    question: 'Who are your target users?',
    options: ['B2B SaaS', 'B2C Consumers', 'Developers', 'Enterprise', 'Small Business'],
  },
  {
    id: 'scale',
    question: 'Expected user scale at launch?',
    options: ['< 100 users', '100-1000 users', '1000-10000 users', '> 10000 users'],
  },
  {
    id: 'timeline',
    question: 'Target launch timeline?',
    options: ['2 weeks (MVP)', '1 month', '3 months', '6 months'],
  },
];

const mockFeatures: SuggestedFeature[] = [
  { id: 'auth', name: 'User Authentication', description: 'Login, signup, password reset', priority: 'must-have' },
  { id: 'dashboard', name: 'Admin Dashboard', description: 'Analytics and management', priority: 'must-have' },
  { id: 'billing', name: 'Billing & Subscriptions', description: 'Stripe integration', priority: 'must-have' },
  { id: 'api', name: 'REST API', description: 'Programmatic access', priority: 'must-have' },
  { id: 'webhooks', name: 'Webhooks', description: 'Event notifications', priority: 'nice-to-have' },
  { id: 'teams', name: 'Team Collaboration', description: 'Multi-user workspaces', priority: 'nice-to-have' },
];

const mockTechStack: TechRecommendation[] = [
  { category: 'Frontend', options: ['Next.js', 'React', 'Vue', 'Svelte'], recommended: 'Next.js' },
  { category: 'Backend', options: ['FastAPI', 'Node.js', 'Django', 'Go'], recommended: 'FastAPI' },
  { category: 'Database', options: ['PostgreSQL', 'MongoDB', 'MySQL', 'Supabase'], recommended: 'PostgreSQL' },
  { category: 'Auth', options: ['Auth0', 'Clerk', 'Firebase Auth', 'Custom'], recommended: 'Clerk' },
];

interface StepIndicatorProps {
  currentStep: WizardStep;
  steps: { id: WizardStep; label: string; icon: React.ElementType }[];
}

function StepIndicator({ currentStep, steps }: StepIndicatorProps) {
  const currentIndex = steps.findIndex(s => s.id === currentStep);
  
  return (
    <div className="flex items-center justify-between mb-6">
      {steps.map((step, index) => {
        const Icon = step.icon;
        const isActive = index === currentIndex;
        const isCompleted = index < currentIndex;
        
        return (
          <div key={step.id} className="flex items-center">
            <div className={cn(
              'flex flex-col items-center gap-1',
              isActive ? 'text-state-queued' : isCompleted ? 'text-state-success' : 'text-text-tertiary'
            )}>
              <div className={cn(
                'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-colors',
                isActive ? 'border-state-queued bg-state-queued-dim' : 
                isCompleted ? 'border-state-success bg-state-success-dim' : 
                'border-border-default bg-bg-base'
              )}>
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
              </div>
              <span className="text-xs hidden sm:block">{step.label}</span>
            </div>
            {index < steps.length - 1 && (
              <div className={cn(
                'w-8 sm:w-16 h-0.5 mx-1 sm:mx-2',
                isCompleted ? 'bg-state-success' : 'bg-border-default'
              )} />
            )}
          </div>
        );
      })}
    </div>
  );
}

export function RequirementsWizard() {
  const [step, setStep] = useState<WizardStep>('idea');
  const [data, setData] = useState<WizardData>({
    idea: '',
    answers: {},
    selectedFeatures: [],
    selectedTech: {},
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const createProject = useCreateProject();
  const router = useRouter();

  const steps = [
    { id: 'idea' as WizardStep, label: 'Idea', icon: Lightbulb },
    { id: 'clarify' as WizardStep, label: 'Clarify', icon: MessageSquare },
    { id: 'features' as WizardStep, label: 'Features', icon: ListChecks },
    { id: 'tech' as WizardStep, label: 'Tech Stack', icon: Layers },
    { id: 'review' as WizardStep, label: 'Review', icon: Sparkles },
  ];

  const handleNext = async () => {
    const stepOrder: WizardStep[] = ['idea', 'clarify', 'features', 'tech', 'review'];
    const currentIndex = stepOrder.indexOf(step);
    
    if (step === 'idea' && !data.idea.trim()) {
      toast.error('Please describe your idea');
      return;
    }
    
    if (currentIndex < stepOrder.length - 1) {
      setIsProcessing(true);
      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 800));
      setIsProcessing(false);
      setStep(stepOrder[currentIndex + 1]);
    }
  };

  const handleBack = () => {
    const stepOrder: WizardStep[] = ['idea', 'clarify', 'features', 'tech', 'review'];
    const currentIndex = stepOrder.indexOf(step);
    if (currentIndex > 0) {
      setStep(stepOrder[currentIndex - 1]);
    }
  };

  const handleCreateProject = async () => {
    setIsProcessing(true);
    
    try {
      const requirements = `
Project Idea: ${data.idea}

Target Users: ${data.answers['target-users']}
Expected Scale: ${data.answers['scale']}
Timeline: ${data.answers['timeline']}

Features:
${data.selectedFeatures.map(id => {
  const f = mockFeatures.find(f => f.id === id);
  return `- ${f?.name}: ${f?.description}`;
}).join('\n')}

Tech Stack:
${Object.entries(data.selectedTech).map(([cat, tech]) => `- ${cat}: ${tech}`).join('\n')}
      `.trim();

      const project = await createProject.mutateAsync({
        name: data.idea.slice(0, 30).toLowerCase().replace(/[^a-z0-9]/g, '-'),
        description: data.idea,
        requirements,
      });

      await api.activateProject(project.id);
      await api.executeWorkflow({
        project_id: project.id,
        phase: 'requirements',
        async_execution: true,
      });

      toast.success('Project created! AI team is working on it.');
      router.push(`/projects/${project.id}`);
    } catch (error) {
      toast.error('Failed to create project');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case 'idea':
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-text-primary">What do you want to build?</h3>
              <p className="text-sm text-text-secondary">Describe your idea and we&apos;ll help refine it</p>
            </div>
            <textarea
              value={data.idea}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => 
                setData({ ...data, idea: e.target.value })
              }
              placeholder="e.g., A SaaS platform for managing freelance projects with time tracking, invoicing, and client collaboration..."
              rows={5}
              className="w-full rounded-lg border border-border-default bg-bg-panel px-4 py-3 text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-queued"
            />
            <div className="flex gap-2 flex-wrap">
              {['SaaS Dashboard', 'API Service', 'AI App', 'E-commerce'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setData({ ...data, idea: `Build a ${suggestion.toLowerCase()} for...` })}
                  className="px-3 py-1 text-xs rounded-full bg-state-queued-dim text-state-queued hover:bg-state-queued/20 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        );

      case 'clarify':
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-text-primary">Let&apos;s clarify your requirements</h3>
              <p className="text-sm text-text-secondary">Answer these questions to help us understand better</p>
            </div>
            {mockClarifications.map((q) => (
              <div key={q.id} className="space-y-2">
                <label className="text-sm font-medium text-text-primary">{q.question}</label>
                <div className="flex flex-wrap gap-2">
                  {q.options?.map((option) => (
                    <button
                      key={option}
                      onClick={() => setData({ 
                        ...data, 
                        answers: { ...data.answers, [q.id]: option }
                      })}
                      className={cn(
                        'px-3 py-2 text-sm rounded-lg border transition-all',
                        data.answers[q.id] === option
                          ? 'border-state-queued bg-state-queued-dim text-state-queued'
                          : 'border-border-default bg-bg-panel text-text-secondary hover:border-border-hover'
                      )}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        );

      case 'features':
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-text-primary">Select Features</h3>
              <p className="text-sm text-text-secondary">Choose the features for your MVP</p>
            </div>
            <div className="space-y-2">
              {mockFeatures.map((feature) => (
                <button
                  key={feature.id}
                  onClick={() => {
                    const selected = data.selectedFeatures.includes(feature.id)
                      ? data.selectedFeatures.filter(id => id !== feature.id)
                      : [...data.selectedFeatures, feature.id];
                    setData({ ...data, selectedFeatures: selected });
                  }}
                  className={cn(
                    'w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left',
                    data.selectedFeatures.includes(feature.id)
                      ? 'border-state-queued bg-state-queued-dim'
                      : 'border-border-default bg-bg-panel hover:border-border-hover'
                  )}
                >
                  <div className={cn(
                    'h-5 w-5 rounded border flex items-center justify-center',
                    data.selectedFeatures.includes(feature.id)
                      ? 'bg-state-queued border-state-queued'
                      : 'border-border-default'
                  )}>
                    {data.selectedFeatures.includes(feature.id) && (
                      <CheckCircle2 className="h-3 w-3 text-white" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-text-primary">{feature.name}</span>
                      <Badge variant={feature.priority === 'must-have' ? 'default' : 'secondary'} className="text-xs">
                        {feature.priority}
                      </Badge>
                    </div>
                    <p className="text-xs text-text-secondary">{feature.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        );

      case 'tech':
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-text-primary">Choose Your Tech Stack</h3>
              <p className="text-sm text-text-secondary">We&apos;ve recommended options based on your requirements</p>
            </div>
            {mockTechStack.map((tech) => (
              <div key={tech.category} className="space-y-2">
                <label className="text-sm font-medium text-text-primary">{tech.category}</label>
                <div className="flex flex-wrap gap-2">
                  {tech.options.map((option) => (
                    <button
                      key={option}
                      onClick={() => setData({
                        ...data,
                        selectedTech: { ...data.selectedTech, [tech.category]: option }
                      })}
                      className={cn(
                        'px-3 py-2 text-sm rounded-lg border transition-all flex items-center gap-2',
                        data.selectedTech[tech.category] === option
                          ? 'border-state-queued bg-state-queued-dim text-state-queued'
                          : 'border-border-default bg-bg-panel text-text-secondary hover:border-border-hover',
                        option === tech.recommended && 'ring-1 ring-state-success/50'
                      )}
                    >
                      {option}
                      {option === tech.recommended && (
                        <Badge variant="outline" className="text-xs bg-state-success-dim text-state-success">
                          Recommended
                        </Badge>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        );

      case 'review':
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-text-primary">Review & Create</h3>
              <p className="text-sm text-text-secondary">Here&apos;s what we&apos;ll build for you</p>
            </div>
            
            <div className="space-y-3 rounded-lg bg-bg-base p-4">
              <div>
                <span className="text-xs text-text-tertiary uppercase">Idea</span>
                <p className="text-sm text-text-primary">{data.idea}</p>
              </div>
              
              <div>
                <span className="text-xs text-text-tertiary uppercase">Features ({data.selectedFeatures.length})</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.selectedFeatures.map(id => {
                    const f = mockFeatures.find(f => f.id === id);
                    return f ? (
                      <Badge key={id} variant="secondary" className="text-xs">
                        {f.name}
                      </Badge>
                    ) : null;
                  })}
                </div>
              </div>
              
              <div>
                <span className="text-xs text-text-tertiary uppercase">Tech Stack</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {Object.entries(data.selectedTech).map(([cat, tech]) => (
                    <Badge key={cat} variant="outline" className="text-xs">
                      {cat}: {tech}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <Card className="glass-panel border-border-default/50 max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-xl text-text-primary">AI Requirements Wizard</CardTitle>
        <p className="text-sm text-text-secondary">
          Let&apos;s refine your idea into a complete project specification
        </p>
      </CardHeader>
      <CardContent>
        <StepIndicator currentStep={step} steps={steps} />
        
        <div className="min-h-[300px]">
          {renderStepContent()}
        </div>
        
        <div className="flex justify-between mt-6 pt-4 border-t border-border-default">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={step === 'idea' || isProcessing}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          
          {step === 'review' ? (
            <Button
              onClick={handleCreateProject}
              disabled={isProcessing}
              className="bg-gradient-to-r from-state-queued to-state-running"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Create Project
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
