'use client';

import { useState } from 'react';
import { 
  Lightbulb, 
  FileText, 
  GitBranch, 
  Code2, 
  TestTube, 
  Rocket,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  Circle,
  Loader2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface ProjectPhase {
  id: string;
  name: string;
  icon: React.ElementType;
  status: 'locked' | 'available' | 'in_progress' | 'completed';
  description: string;
  sections: PhaseSection[];
}

interface PhaseSection {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed';
  content?: React.ReactNode;
}

const projectPhases: ProjectPhase[] = [
  {
    id: 'idea',
    name: 'Idea',
    icon: Lightbulb,
    status: 'completed',
    description: 'Product concept and market research',
    sections: [
      { id: 'concept', name: 'Product Concept', status: 'completed' },
      { id: 'market', name: 'Market Research', status: 'completed' },
      { id: 'validation', name: 'Idea Validation', status: 'completed' },
    ],
  },
  {
    id: 'requirements',
    name: 'Requirements',
    icon: FileText,
    status: 'completed',
    description: 'Detailed requirements and specifications',
    sections: [
      { id: 'user-stories', name: 'User Stories', status: 'completed' },
      { id: 'technical-specs', name: 'Technical Specs', status: 'completed' },
      { id: 'api-design', name: 'API Design', status: 'completed' },
    ],
  },
  {
    id: 'architecture',
    name: 'Architecture',
    icon: GitBranch,
    status: 'in_progress',
    description: 'System design and architecture',
    sections: [
      { id: 'system-design', name: 'System Design', status: 'completed' },
      { id: 'database-schema', name: 'Database Schema', status: 'in_progress' },
      { id: 'infrastructure', name: 'Infrastructure Plan', status: 'pending' },
    ],
  },
  {
    id: 'implementation',
    name: 'Implementation',
    icon: Code2,
    status: 'available',
    description: 'Code development and feature implementation',
    sections: [
      { id: 'backend', name: 'Backend Development', status: 'pending' },
      { id: 'frontend', name: 'Frontend Development', status: 'pending' },
      { id: 'integration', name: 'Integration', status: 'pending' },
    ],
  },
  {
    id: 'testing',
    name: 'Testing',
    icon: TestTube,
    status: 'locked',
    description: 'Quality assurance and testing',
    sections: [
      { id: 'unit-tests', name: 'Unit Tests', status: 'pending' },
      { id: 'integration-tests', name: 'Integration Tests', status: 'pending' },
      { id: 'e2e-tests', name: 'E2E Tests', status: 'pending' },
    ],
  },
  {
    id: 'deployment',
    name: 'Deployment',
    icon: Rocket,
    status: 'locked',
    description: 'Production deployment and launch',
    sections: [
      { id: 'staging', name: 'Staging Deployment', status: 'pending' },
      { id: 'production', name: 'Production Deployment', status: 'pending' },
      { id: 'monitoring', name: 'Monitoring Setup', status: 'pending' },
    ],
  },
];

interface PhaseCardProps {
  phase: ProjectPhase;
  isExpanded: boolean;
  onToggle: () => void;
  isActive: boolean;
}

function PhaseCard({ phase, isExpanded, onToggle, isActive }: PhaseCardProps) {
  const Icon = phase.icon;
  
  const statusConfig = {
    locked: {
      bgColor: 'bg-bg-base',
      borderColor: 'border-border-subtle',
      iconColor: 'text-text-tertiary',
      badge: 'Locked',
      badgeVariant: 'secondary' as const,
    },
    available: {
      bgColor: 'bg-bg-panel',
      borderColor: 'border-border-default',
      iconColor: 'text-text-secondary',
      badge: 'Ready',
      badgeVariant: 'outline' as const,
    },
    in_progress: {
      bgColor: 'bg-state-queued-dim',
      borderColor: 'border-state-queued/30',
      iconColor: 'text-state-queued',
      badge: 'In Progress',
      badgeVariant: 'default' as const,
    },
    completed: {
      bgColor: 'bg-state-success-dim',
      borderColor: 'border-state-success/30',
      iconColor: 'text-state-success',
      badge: 'Completed',
      badgeVariant: 'default' as const,
    },
  };

  const config = statusConfig[phase.status];

  return (
    <div
      className={cn(
        'rounded-lg border transition-all',
        config.borderColor,
        isActive ? 'ring-2 ring-state-queued' : '',
        phase.status === 'locked' ? 'opacity-60' : ''
      )}
    >
      <button
        onClick={onToggle}
        disabled={phase.status === 'locked'}
        className={cn(
          'w-full flex items-center gap-3 p-3 rounded-lg transition-colors',
          config.bgColor,
          phase.status !== 'locked' && 'hover:bg-bg-hover'
        )}
      >
        <div className={cn('flex h-10 w-10 items-center justify-center rounded-lg bg-bg-base', config.iconColor)}>
          <Icon className="h-5 w-5" />
        </div>
        
        <div className="flex-1 text-left">
          <div className="flex items-center gap-2">
            <span className="font-medium text-text-primary">{phase.name}</span>
            <Badge variant={config.badgeVariant} className="text-xs">
              {config.badge}
            </Badge>
          </div>
          <p className="text-xs text-text-secondary">{phase.description}</p>
        </div>
        
        {phase.status !== 'locked' && (
          <div className="flex items-center gap-2">
            {phase.status === 'in_progress' && (
              <Loader2 className="h-4 w-4 animate-spin text-state-queued" />
            )}
            {phase.status === 'completed' && (
              <CheckCircle2 className="h-4 w-4 text-state-success" />
            )}
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-text-tertiary" />
            ) : (
              <ChevronRight className="h-4 w-4 text-text-tertiary" />
            )}
          </div>
        )}
      </button>
      
      {/* Expanded Content */}
      {isExpanded && phase.status !== 'locked' && (
        <div className="border-t border-border-subtle px-3 pb-3">
          <div className="pt-3 space-y-2">
            {phase.sections.map((section) => (
              <div
                key={section.id}
                className="flex items-center gap-3 p-2 rounded-md bg-bg-base/50"
              >
                {section.status === 'completed' ? (
                  <CheckCircle2 className="h-4 w-4 text-state-success" />
                ) : section.status === 'in_progress' ? (
                  <Loader2 className="h-4 w-4 animate-spin text-state-queued" />
                ) : (
                  <Circle className="h-4 w-4 text-text-tertiary" />
                )}
                <span className={cn(
                  'text-sm',
                  section.status === 'completed' ? 'text-text-secondary' : 'text-text-primary'
                )}>
                  {section.name}
                </span>
              </div>
            ))}
          </div>
          
          {/* Action Button */}
          <div className="mt-3">
            {phase.status === 'available' && (
              <Button size="sm" className="w-full">
                Start {phase.name}
              </Button>
            )}
            {phase.status === 'in_progress' && (
              <Button size="sm" variant="outline" className="w-full">
                View Details
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

interface ProgressiveProjectDashboardProps {
  projectId?: string;
  currentPhase?: string;
  className?: string;
}

export function ProgressiveProjectDashboard({
  projectId,
  currentPhase = 'architecture',
  className,
}: ProgressiveProjectDashboardProps) {
  const [expandedPhase, setExpandedPhase] = useState<string | null>(currentPhase);

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary">Project Progress</CardTitle>
            <p className="text-sm text-text-secondary">
              Development phases and current status
            </p>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-state-queued">50%</span>
            <p className="text-xs text-text-tertiary">Complete</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="h-2 w-full rounded-full bg-bg-base overflow-hidden">
            <div 
              className="h-full rounded-full bg-gradient-to-r from-state-queued to-state-running transition-all duration-500"
              style={{ width: '50%' }}
            />
          </div>
        </div>
        
        {/* Phase List */}
        <div className="space-y-2">
          {projectPhases.map((phase) => (
            <PhaseCard
              key={phase.id}
              phase={phase}
              isExpanded={expandedPhase === phase.id}
              onToggle={() => setExpandedPhase(
                expandedPhase === phase.id ? null : phase.id
              )}
              isActive={phase.id === currentPhase}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
