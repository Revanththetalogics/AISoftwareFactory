'use client';

import { motion } from 'framer-motion';
import { Cloud, Database, Shield, Globe, Container } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const infraComponents = [
  { id: '1', name: 'Docker Containers', status: 'healthy', count: 8, icon: Container },
  { id: '2', name: 'Kubernetes Pods', status: 'healthy', count: 12, icon: Cloud },
  { id: '3', name: 'Database', status: 'healthy', count: 2, icon: Database },
  { id: '4', name: 'Load Balancer', status: 'healthy', count: 1, icon: Globe },
];

export default function InfrastructurePage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Infrastructure</h1>
          <p className="text-text-secondary">Manage cloud infrastructure and resources</p>
        </div>
        <Button className="bg-cyan-500 hover:bg-cyan-600">
          <Cloud className="mr-2 h-4 w-4" />
          Provision Resources
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {infraComponents.map((component) => (
          <Card key={component.id} className="border-border-default bg-bg-base/50">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="rounded-lg bg-cyan-500/10 p-3">
                  <component.icon className="h-6 w-6 text-cyan-400" />
                </div>
                <Badge
                  variant="secondary"
                  className="bg-state-success-dim text-state-success"
                >
                  {component.status}
                </Badge>
              </div>
              <h3 className="mt-4 font-semibold text-text-primary">{component.name}</h3>
              <p className="text-2xl font-bold text-text-primary">{component.count}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border-default bg-bg-base/50">
        <CardHeader>
          <CardTitle className="text-text-primary">Terraform Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg bg-slate-950 p-4 font-mono text-sm text-text-secondary">
            <pre>{`# Infrastructure as Code
resource "docker_container" "app" {
  image = "ai-factory:latest"
  name  = "ai-factory-app"
  
  ports {
    internal = 8000
    external = 8000
  }
}`}</pre>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
