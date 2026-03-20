'use client';

export const dynamic = 'force-dynamic';

import { motion } from 'framer-motion';
import {
  Layers,
  Database,
  Server,
  Globe,
  Cpu,
  Shield,
  ArrowDown,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Settings,
  Download,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

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

interface ArchitectureNode {
  id: string;
  name: string;
  type: string;
  icon: React.ElementType;
  color: string;
  description: string;
  status: 'healthy' | 'warning' | 'error';
  details: string[];
}

const architectureNodes: ArchitectureNode[] = [
  {
    id: '1',
    name: 'Next.js Frontend',
    type: 'Frontend',
    icon: Globe,
    color: 'from-violet-500 to-purple-600',
    description: 'React-based web application with SSR',
    status: 'healthy',
    details: ['App Router', 'TypeScript', 'Tailwind CSS', 'shadcn/ui'],
  },
  {
    id: '2',
    name: 'FastAPI Backend',
    type: 'Backend',
    icon: Server,
    color: 'from-emerald-500 to-teal-600',
    description: 'High-performance Python API server',
    status: 'healthy',
    details: ['Python 3.11', 'FastAPI', 'Pydantic', 'Uvicorn'],
  },
  {
    id: '3',
    name: 'PostgreSQL',
    type: 'Database',
    icon: Database,
    color: 'from-blue-500 to-cyan-600',
    description: 'Primary relational database',
    status: 'healthy',
    details: ['PostgreSQL 15', 'SQLAlchemy', 'Alembic migrations'],
  },
  {
    id: '4',
    name: 'Redis Cache',
    type: 'Cache',
    icon: Layers,
    color: 'from-red-500 to-rose-600',
    description: 'In-memory data store for caching',
    status: 'healthy',
    details: ['Redis 7', 'Session storage', 'Rate limiting'],
  },
  {
    id: '5',
    name: 'AI/LLM Service',
    type: 'AI',
    icon: Cpu,
    color: 'from-amber-500 to-orange-600',
    description: 'Language model integration layer',
    status: 'healthy',
    details: ['Ollama', 'CrewAI', 'LangGraph', 'Custom agents'],
  },
  {
    id: '6',
    name: 'Auth Service',
    type: 'Security',
    icon: Shield,
    color: 'from-indigo-500 to-blue-600',
    description: 'Authentication and authorization',
    status: 'healthy',
    details: ['JWT tokens', 'OAuth2', 'Role-based access'],
  },
];

const techStack = [
  { category: 'Frontend', items: ['Next.js 14', 'React 18', 'TypeScript', 'Tailwind CSS', 'shadcn/ui', 'Framer Motion'] },
  { category: 'Backend', items: ['FastAPI', 'Python 3.11', 'Pydantic', 'SQLAlchemy', 'Uvicorn'] },
  { category: 'Database', items: ['PostgreSQL', 'Redis', 'Alembic'] },
  { category: 'AI/ML', items: ['Ollama', 'CrewAI', 'LangGraph', 'LiteLLM'] },
  { category: 'DevOps', items: ['Docker', 'GitHub Actions', 'Terraform', 'Nginx'] },
];

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'healthy':
      return <CheckCircle2 className="h-4 w-4 text-state-success" />;
    case 'warning':
      return <AlertCircle className="h-4 w-4 text-state-warning" />;
    case 'error':
      return <AlertCircle className="h-4 w-4 text-state-error" />;
    default:
      return <CheckCircle2 className="h-4 w-4 text-state-success" />;
  }
};

export default function ArchitecturePage() {
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
          <h1 className="text-3xl font-bold text-text-primary">Architecture</h1>
          <p className="mt-1 text-text-secondary">
            System design and component overview
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-border-default text-text-secondary hover:bg-bg-hover">
            <FileCode className="mr-2 h-4 w-4" />
            View Specs
          </Button>
          <Button className="bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
            <Download className="mr-2 h-4 w-4" />
            Export Diagram
          </Button>
        </div>
      </motion.div>

      <Tabs defaultValue="diagram" className="space-y-6">
        <TabsList className="border-border-default bg-bg-base/50">
          <TabsTrigger value="diagram" className="data-[state=active]:bg-bg-hover">
            System Diagram
          </TabsTrigger>
          <TabsTrigger value="stack" className="data-[state=active]:bg-bg-hover">
            Tech Stack
          </TabsTrigger>
          <TabsTrigger value="config" className="data-[state=active]:bg-bg-hover">
            Configuration
          </TabsTrigger>
        </TabsList>

        <TabsContent value="diagram" className="space-y-6">
          {/* Architecture Diagram */}
          <motion.div variants={itemVariants}>
            <Card className="border-border-default bg-bg-base/50">
              <CardHeader>
                <CardTitle className="text-lg text-text-primary">System Architecture</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative rounded-xl border border-border-default bg-slate-950/50 p-8">
                  {/* Client Layer */}
                  <div className="mb-8 text-center">
                    <div className="inline-flex items-center gap-3 rounded-xl border border-border-default bg-bg-hover/50 px-6 py-4">
                      <Globe className="h-6 w-6 text-state-running" />
                      <div className="text-left">
                        <p className="font-medium text-text-primary">Web Client</p>
                        <p className="text-xs text-text-tertiary">Browser / Mobile</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-center mb-8">
                    <ArrowDown className="h-6 w-6 text-text-tertiary" />
                  </div>

                  {/* Load Balancer */}
                  <div className="mb-8 text-center">
                    <div className="inline-flex items-center gap-3 rounded-xl border border-border-default bg-bg-hover/50 px-6 py-4">
                      <Server className="h-6 w-6 text-state-info" />
                      <div className="text-left">
                        <p className="font-medium text-text-primary">Load Balancer</p>
                        <p className="text-xs text-text-tertiary">Nginx / Traefik</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-center mb-8">
                    <ArrowDown className="h-6 w-6 text-text-tertiary" />
                  </div>

                  {/* Application Layer */}
                  <div className="grid gap-4 md:grid-cols-3 mb-8">
                    {architectureNodes.slice(0, 3).map((node) => (
                      <div
                        key={node.id}
                        className="rounded-xl border border-border-default bg-bg-hover/30 p-4 transition-all hover:border-border-default hover:bg-bg-hover/50"
                      >
                        <div className="flex items-start gap-3">
                          <div className={`rounded-lg bg-gradient-to-br ${node.color} p-2`}>
                            <node.icon className="h-5 w-5 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-text-primary">{node.name}</p>
                              {getStatusIcon(node.status)}
                            </div>
                            <p className="text-xs text-text-tertiary">{node.type}</p>
                          </div>
                        </div>
                        <p className="mt-3 text-sm text-text-secondary">{node.description}</p>
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-center mb-8">
                    <ArrowDown className="h-6 w-6 text-text-tertiary" />
                  </div>

                  {/* Data & AI Layer */}
                  <div className="grid gap-4 md:grid-cols-3">
                    {architectureNodes.slice(3).map((node) => (
                      <div
                        key={node.id}
                        className="rounded-xl border border-border-default bg-bg-hover/30 p-4 transition-all hover:border-border-default hover:bg-bg-hover/50"
                      >
                        <div className="flex items-start gap-3">
                          <div className={`rounded-lg bg-gradient-to-br ${node.color} p-2`}>
                            <node.icon className="h-5 w-5 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-text-primary">{node.name}</p>
                              {getStatusIcon(node.status)}
                            </div>
                            <p className="text-xs text-text-tertiary">{node.type}</p>
                          </div>
                        </div>
                        <p className="mt-3 text-sm text-text-secondary">{node.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Component Details */}
          <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {architectureNodes.map((node) => (
              <Card
                key={node.id}
                className="border-border-default bg-bg-base/50 backdrop-blur-sm"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`rounded-lg bg-gradient-to-br ${node.color} p-2`}>
                        <node.icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-base text-text-primary">{node.name}</CardTitle>
                        <p className="text-xs text-text-tertiary">{node.type}</p>
                      </div>
                    </div>
                    {getStatusIcon(node.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-text-secondary mb-4">{node.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {node.details.map((detail, idx) => (
                      <Badge
                        key={idx}
                        variant="outline"
                        className="bg-bg-hover text-text-secondary"
                      >
                        {detail}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        </TabsContent>

        <TabsContent value="stack" className="space-y-6">
          <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {techStack.map((stack) => (
              <Card key={stack.category} className="border-border-default bg-bg-base/50">
                <CardHeader>
                  <CardTitle className="text-lg text-text-primary">{stack.category}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {stack.items.map((item, idx) => (
                      <Badge
                        key={idx}
                        variant="outline"
                        className="bg-bg-hover px-3 py-1 text-text-secondary"
                      >
                        {item}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        </TabsContent>

        <TabsContent value="config" className="space-y-6">
          <motion.div variants={itemVariants}>
            <Card className="border-border-default bg-bg-base/50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg text-text-primary">System Configuration</CardTitle>
                  <Button variant="outline" size="sm" className="border-border-default text-text-secondary">
                    <Settings className="mr-2 h-4 w-4" />
                    Edit Config
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="rounded-lg border border-border-default bg-bg-hover/30 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-text-primary">Auto-scaling</p>
                        <p className="text-sm text-text-tertiary">Enable automatic scaling based on load</p>
                      </div>
                      <Badge className="bg-state-success-dim text-state-success">Enabled</Badge>
                    </div>
                  </div>
                  <div className="rounded-lg border border-border-default bg-bg-hover/30 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-text-primary">High Availability</p>
                        <p className="text-sm text-text-tertiary">Multi-zone deployment for redundancy</p>
                      </div>
                      <Badge className="bg-state-success-dim text-state-success">Enabled</Badge>
                    </div>
                  </div>
                  <div className="rounded-lg border border-border-default bg-bg-hover/30 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-text-primary">SSL/TLS</p>
                        <p className="text-sm text-text-tertiary">Automatic HTTPS certificates</p>
                      </div>
                      <Badge className="bg-state-success-dim text-state-success">Enabled</Badge>
                    </div>
                  </div>
                  <div className="rounded-lg border border-border-default bg-bg-hover/30 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-text-primary">Database Backups</p>
                        <p className="text-sm text-text-tertiary">Daily automated backups</p>
                      </div>
                      <Badge className="bg-state-success-dim text-state-success">Enabled</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
