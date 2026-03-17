'use client';

import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Bot,
  Clock,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Sparkles,
  FolderKanban,
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
import { useState } from 'react';

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

const projects = [
  {
    id: '1',
    name: 'SaaS Dashboard',
    description: 'Modern analytics dashboard with real-time data visualization',
    stage: 'Design',
    progress: 45,
    agents: 3,
    status: 'active',
    createdAt: '2 days ago',
    health: 'good',
  },
  {
    id: '2',
    name: 'E-commerce API',
    description: 'RESTful API for online store with payment integration',
    stage: 'Planning',
    progress: 25,
    agents: 2,
    status: 'active',
    createdAt: '5 days ago',
    health: 'good',
  },
  {
    id: '3',
    name: 'Mobile Banking App',
    description: 'Secure mobile banking application with biometric auth',
    stage: 'Engineering',
    progress: 68,
    agents: 5,
    status: 'active',
    createdAt: '1 week ago',
    health: 'warning',
  },
  {
    id: '4',
    name: 'AI Content Platform',
    description: 'Content generation platform powered by LLMs',
    stage: 'Testing',
    progress: 85,
    agents: 4,
    status: 'active',
    createdAt: '2 weeks ago',
    health: 'good',
  },
  {
    id: '5',
    name: 'Healthcare Portal',
    description: 'Patient management system for clinics',
    stage: 'Deployment',
    progress: 95,
    agents: 3,
    status: 'completed',
    createdAt: '3 weeks ago',
    health: 'good',
  },
  {
    id: '6',
    name: 'Social Media Analytics',
    description: 'Track and analyze social media metrics',
    stage: 'Idea',
    progress: 5,
    agents: 1,
    status: 'draft',
    createdAt: '1 day ago',
    health: 'good',
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'completed':
      return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    case 'draft':
      return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    default:
      return 'bg-slate-500/10 text-slate-400';
  }
};

const getHealthIcon = (health: string) => {
  switch (health) {
    case 'good':
      return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
    case 'warning':
      return <AlertCircle className="h-4 w-4 text-amber-400" />;
    default:
      return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
  }
};

export default function ProjectsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProject, setSelectedProject] = useState<typeof projects[0] | null>(null);

  const filteredProjects = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
          <h1 className="text-3xl font-bold text-slate-100">Projects</h1>
          <p className="mt-1 text-slate-400">
            Manage and monitor your AI-powered software projects
          </p>
        </div>
        <Dialog>
          <DialogTrigger>
            <Button className="bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="border-slate-800 bg-slate-900">
            <DialogHeader>
              <DialogTitle className="text-slate-100">Create New Project</DialogTitle>
              <DialogDescription className="text-slate-400">
                Describe your product idea and let AI agents build it for you.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <label className="text-sm font-medium text-slate-300">Project Name</label>
                <Input
                  placeholder="e.g., SaaS Analytics Platform"
                  className="mt-1 border-slate-700 bg-slate-800 text-slate-200"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-300">Description</label>
                <textarea
                  placeholder="Describe what you want to build..."
                  className="mt-1 w-full rounded-md border border-slate-700 bg-slate-800 p-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
                  rows={4}
                />
              </div>
              <Button className="w-full bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
                <Sparkles className="mr-2 h-4 w-4" />
                Start Building
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </motion.div>

      {/* Filters */}
      <motion.div variants={itemVariants} className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <Input
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="border-slate-700 bg-slate-900/50 pl-10 text-slate-200 placeholder:text-slate-500"
          />
        </div>
        <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
          <Filter className="mr-2 h-4 w-4" />
          Filter
        </Button>
      </motion.div>

      {/* Projects Grid */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredProjects.map((project) => (
          <Card
            key={project.id}
            className="group cursor-pointer border-slate-800 bg-slate-900/50 backdrop-blur-sm transition-all hover:border-slate-700 hover:bg-slate-800/50"
            onClick={() => setSelectedProject(project)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/20 to-indigo-500/20">
                    <FolderKanban className="h-5 w-5 text-violet-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-100">{project.name}</h3>
                    <p className="text-xs text-slate-500">{project.createdAt}</p>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    align="end"
                    className="border-slate-700 bg-slate-900"
                  >
                    <DropdownMenuItem className="text-slate-300 focus:bg-slate-800">
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-slate-300 focus:bg-slate-800">
                      Edit Project
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-red-400 focus:bg-slate-800">
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-400 line-clamp-2">{project.description}</p>

              <div className="flex items-center gap-4">
                <Badge variant="outline" className={getStatusColor(project.status)}>
                  {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                </Badge>
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  {getHealthIcon(project.health)}
                  <span className="capitalize">{project.health}</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500">Stage: {project.stage}</span>
                  <span className="text-slate-300">{project.progress}%</span>
                </div>
                <Progress value={project.progress} className="h-2 bg-slate-800" />
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  <Bot className="h-3.5 w-3.5" />
                  <span>{project.agents} agents</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-auto p-0 text-violet-400 hover:text-violet-300"
                >
                  View
                  <ArrowRight className="ml-1 h-3.5 w-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Project Detail Dialog */}
      <Dialog open={!!selectedProject} onOpenChange={() => setSelectedProject(null)}>
        <DialogContent className="max-w-2xl border-slate-800 bg-slate-900">
          {selectedProject && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-indigo-500/20">
                    <FolderKanban className="h-6 w-6 text-violet-400" />
                  </div>
                  <div>
                    <DialogTitle className="text-xl text-slate-100">
                      {selectedProject.name}
                    </DialogTitle>
                    <DialogDescription className="text-slate-400">
                      {selectedProject.description}
                    </DialogDescription>
                  </div>
                </div>
              </DialogHeader>
              <div className="space-y-6 pt-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-4">
                    <p className="text-xs text-slate-500">Status</p>
                    <Badge variant="outline" className={`mt-1 ${getStatusColor(selectedProject.status)}`}>
                      {selectedProject.status.charAt(0).toUpperCase() + selectedProject.status.slice(1)}
                    </Badge>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-4">
                    <p className="text-xs text-slate-500">Stage</p>
                    <p className="mt-1 font-medium text-slate-200">{selectedProject.stage}</p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-4">
                    <p className="text-xs text-slate-500">Active Agents</p>
                    <p className="mt-1 font-medium text-slate-200">{selectedProject.agents}</p>
                  </div>
                </div>

                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm text-slate-500">Progress</span>
                    <span className="text-sm font-medium text-slate-200">
                      {selectedProject.progress}%
                    </span>
                  </div>
                  <Progress value={selectedProject.progress} className="h-3 bg-slate-800" />
                </div>

                <div className="flex gap-3">
                  <Button className="flex-1 bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
                    <Sparkles className="mr-2 h-4 w-4" />
                    Continue Building
                  </Button>
                  <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                    View Architecture
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
