'use client';

export const dynamic = 'force-dynamic';

import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Bot,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Sparkles,
  FolderKanban,
  Loader2,
  Play,
} from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { ProjectEditDialog } from '@/components/project/ProjectEditDialog';
import { DeleteConfirmDialog } from '@/components/shared/DeleteConfirmDialog';
import { BulkActions } from '@/components/shared/BulkActions';
import { useState } from 'react';
import { useProjects, useCreateProject, useDeleteProject, useExecuteWorkflow } from '@/lib/hooks';
import { exportToCSV, exportToJSON } from '@/lib/utils/export';
import { debounce } from '@/lib/utils/performance';
import { toast } from 'sonner';
import type { Project } from '@/lib/types';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.25, 0, 1] as const,
    },
  },
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-state-success-dim text-state-success border-state-success/30';
    case 'completed':
      return 'bg-state-running-dim text-state-running border-state-running/30';
    case 'draft':
      return 'bg-state-idle-dim text-state-idle border-state-idle/30';
    default:
      return 'bg-state-idle-dim text-state-idle';
  }
};

const getHealthIcon = (health: string) => {
  switch (health) {
    case 'good':
      return <CheckCircle2 className="h-4 w-4 text-state-success" />;
    case 'warning':
      return <AlertCircle className="h-4 w-4 text-state-warning" />;
    default:
      return <CheckCircle2 className="h-4 w-4 text-state-success" />;
  }
};

export default function ProjectsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [executingProjectId, setExecutingProjectId] = useState<string | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const { data: projects = [], isLoading } = useProjects();
  const createProject = useCreateProject();
  const deleteProject = useDeleteProject();
  const executeWorkflow = useExecuteWorkflow();

  const handleBulkDelete = async () => {
    try {
      await Promise.all(selectedIds.map(id => deleteProject.mutateAsync(id)));
      toast.success(`${selectedIds.length} projects deleted`);
      setSelectedIds([]);
    } catch {
      toast.error('Failed to delete projects');
    }
  };

  const handleBulkExport = () => {
    const selectedProjects = projects.filter(p => selectedIds.includes(p.id));
    exportToCSV(selectedProjects, 'projects.csv');
    toast.success('Projects exported');
  };

  const debouncedSearch = debounce((query: string) => {
    setSearchQuery(query);
  }, 300);

  const filteredProjects = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) {
      toast.error('Project name is required');
      return;
    }

    try {
      await createProject.mutateAsync({
        name: newProjectName,
        description: newProjectDescription,
      });
      toast.success('Project created successfully');
      setNewProjectName('');
      setNewProjectDescription('');
      setIsCreateDialogOpen(false);
    } catch {
      toast.error('Failed to create project');
    }
  };

  const handleDeleteProject = async () => {
    if (!projectToDelete) return;
    
    try {
      await deleteProject.mutateAsync(projectToDelete);
      toast.success('Project deleted successfully');
      setSelectedProject(null);
      setDeleteConfirmOpen(false);
      setProjectToDelete(null);
    } catch {
      toast.error('Failed to delete project');
    }
  };

  const handleExecuteWorkflow = async (projectId: string) => {
    try {
      setExecutingProjectId(projectId);
      await executeWorkflow.mutateAsync({ project_id: projectId });
      toast.success('Workflow started successfully! AI agents are now working on your project.');
    } catch {
      toast.error('Failed to start workflow');
    } finally {
      setExecutingProjectId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-state-running" />
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Projects</h1>
          <p className="mt-1 text-text-secondary">
            Manage and monitor your AI-powered software projects
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger>
            <Button className="bg-gradient-to-r from-state-queued to-state-running hover:from-state-queued hover:to-state-running">
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="border-border-default bg-bg-base">
            <DialogHeader>
              <DialogTitle className="text-text-primary">Create New Project</DialogTitle>
              <DialogDescription className="text-text-secondary">
                Describe your product idea and let AI agents build it for you.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <label className="text-sm font-medium text-text-secondary">Project Name</label>
                <Input
                  placeholder="e.g., SaaS Analytics Platform"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="border-border-default bg-bg-elevated text-text-primary"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-text-secondary">Description</label>
                <textarea
                  placeholder="Describe what you want to build..."
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border-default bg-bg-elevated p-3 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-running"
                  rows={4}
                />
              </div>
              <Button 
                className="w-full bg-gradient-to-r from-state-queued to-state-running hover:from-state-queued hover:to-state-running"
                onClick={handleCreateProject}
                disabled={createProject.isPending}
              >
                {createProject.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="mr-2 h-4 w-4" />
                )}
                Start Building
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </motion.div>

      {/* Filters */}
      <motion.div variants={itemVariants} className="flex items-center gap-4">
        <BulkActions
          selectedIds={selectedIds}
          totalCount={filteredProjects.length}
          onSelectAll={() => setSelectedIds(filteredProjects.map(p => p.id))}
          onClearSelection={() => setSelectedIds([])}
          onDelete={handleBulkDelete}
          onExport={handleBulkExport}
        />
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <Input
            placeholder="Search projects..."
            defaultValue={searchQuery}
            onChange={(e) => debouncedSearch(e.target.value)}
            className="border-border-default bg-bg-input pl-10 text-text-primary placeholder:text-text-tertiary"
          />
        </div>
        <Button variant="outline" className="border-border-default text-text-secondary hover:bg-bg-hover">
          <Filter className="mr-2 h-4 w-4" />
          Filter
        </Button>
      </motion.div>

      {/* Projects Grid */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredProjects.map((project) => (
          <Card
            key={project.id}
            className="group cursor-pointer border-border-default bg-bg-panel/50 backdrop-blur-sm transition-all hover:border-border-emphasis hover:bg-bg-elevated/50"
            onClick={() => setSelectedProject(project)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-state-running-dim/20">
                    <FolderKanban className="h-5 w-5 text-state-running" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{project.name}</h3>
                    <p className="text-xs text-text-tertiary">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-text-secondary">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    align="end"
                    className="border-border-default bg-bg-elevated"
                  >
                    <DropdownMenuItem className="text-text-secondary focus:bg-bg-hover">
                      View Details
                    </DropdownMenuItem>
                    <ProjectEditDialog 
                      project={project}
                      trigger={
                        <DropdownMenuItem 
                          className="text-text-secondary focus:bg-bg-hover"
                          onSelect={(e) => e.preventDefault()}
                        >
                          Edit Project
                        </DropdownMenuItem>
                      }
                    />
                    <DropdownMenuItem 
                      className="text-state-error focus:bg-bg-hover"
                      onClick={(e) => {
                        e.stopPropagation();
                        setProjectToDelete(project.id);
                        setDeleteConfirmOpen(true);
                      }}
                    >
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-text-secondary line-clamp-2">{project.description}</p>

              <div className="flex items-center gap-4">
                <Badge variant="outline" className={getStatusColor(project.status)}>
                  {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                </Badge>
                <div className="flex items-center gap-1 text-xs text-text-tertiary">
                  {getHealthIcon('good')}
                  <span className="capitalize">good</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-tertiary">Stage: {project.current_phase || 'Idea'}</span>
                  <span className="text-text-primary">{project.progress_percent}%</span>
                </div>
                <Progress value={project.progress_percent} className="h-2 bg-bg-base" />
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-border-default">
                <div className="flex items-center gap-1 text-xs text-text-tertiary">
                  <Bot className="h-3.5 w-3.5" />
                  <span>3 agents</span>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExecuteWorkflow(project.id);
                    }}
                    disabled={executingProjectId === project.id}
                    className="h-auto px-3 text-state-running hover:bg-state-running-dim disabled:opacity-50"
                  >
                    {executingProjectId === project.id ? (
                      <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Play className="mr-2 h-3.5 w-3.5" />
                    )}
                    {executingProjectId === project.id ? 'Starting...' : 'Start Workflow'}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-0 text-state-running hover:text-state-running/80"
                    onClick={(e) => e.stopPropagation()}
                  >
                    View
                    <ArrowRight className="ml-1 h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Project Detail Dialog */}
      <Dialog open={!!selectedProject} onOpenChange={() => setSelectedProject(null)}>
        <DialogContent className="max-w-2xl border-border-default bg-bg-base">
          {selectedProject && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-state-running-dim/20">
                    <FolderKanban className="h-6 w-6 text-state-running" />
                  </div>
                  <div>
                    <DialogTitle className="text-xl text-text-primary">
                      {selectedProject.name}
                    </DialogTitle>
                    <DialogDescription className="text-text-secondary">
                      {selectedProject.description}
                    </DialogDescription>
                  </div>
                </div>
              </DialogHeader>
              <div className="space-y-6 pt-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="rounded-lg border border-border-default bg-bg-elevated p-4">
                    <p className="text-xs text-text-tertiary">Status</p>
                    <Badge variant="outline" className={`mt-1 ${getStatusColor(selectedProject.status)}`}>
                      {selectedProject.status.charAt(0).toUpperCase() + selectedProject.status.slice(1)}
                    </Badge>
                  </div>
                  <div className="rounded-lg border border-border-default bg-bg-elevated p-4">
                    <p className="text-xs text-text-tertiary">Stage</p>
                    <p className="mt-1 font-medium text-text-primary">{selectedProject.current_phase || 'Idea'}</p>
                  </div>
                  <div className="rounded-lg border border-border-default bg-bg-elevated p-4">
                    <p className="text-xs text-text-tertiary">Progress</p>
                    <p className="mt-1 font-medium text-text-primary">{selectedProject.progress_percent}%</p>
                  </div>
                </div>

                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm text-text-tertiary">Progress</span>
                    <span className="text-sm font-medium text-text-primary">
                      {selectedProject.progress_percent}%
                    </span>
                  </div>
                  <Progress value={selectedProject.progress_percent} className="h-3 bg-bg-base" />
                </div>

                <div className="flex gap-3">
                  <Button className="flex-1 bg-gradient-to-r from-state-queued to-state-running hover:from-state-queued hover:to-state-running">
                    <Sparkles className="mr-2 h-4 w-4" />
                    Continue Building
                  </Button>
                  <Button variant="outline" className="border-border-default text-text-secondary hover:bg-bg-hover">
                    View Architecture
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        open={deleteConfirmOpen}
        onOpenChange={setDeleteConfirmOpen}
        onConfirm={handleDeleteProject}
        title="Delete Project?"
        description="This will permanently delete this project and all associated data."
        entityName={projects.find(p => p.id === projectToDelete)?.name}
      />
    </motion.div>
  );
}
