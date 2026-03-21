'use client';

import { motion } from 'framer-motion';
import { GitBranch, Settings, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useWorkflows, useCancelWorkflow } from '@/lib/hooks';
import { toast } from 'sonner';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export default function WorkflowsPage() {
  const { data: workflows = [], isLoading, refetch } = useWorkflows();
  const cancelWorkflow = useCancelWorkflow();

  const handleCancel = async (workflowId: string) => {
    try {
      await cancelWorkflow.mutateAsync(workflowId);
      toast.success('Workflow cancelled');
      refetch();
    } catch {
      toast.error('Failed to cancel workflow');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-state-running-dim text-state-running border-state-running';
      case 'completed':
        return 'bg-state-success-dim text-state-success border-state-success';
      case 'pending':
        return 'bg-state-idle-dim text-state-idle border-state-idle';
      case 'cancelled':
        return 'bg-state-warning-dim text-state-warning border-state-warning';
      case 'failed':
        return 'bg-state-error-dim text-state-error border-state-error';
      default:
        return 'bg-state-idle-dim text-state-idle border-state-idle';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-state-running" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Workflows</h1>
          <p className="text-text-secondary">Manage AI-powered development workflows</p>
        </div>
      </div>

      {workflows.length === 0 ? (
        <Card className="border-border-default bg-bg-panel/50">
          <CardContent className="p-12 text-center text-text-secondary">
            <GitBranch className="h-12 w-12 mx-auto mb-4 text-text-tertiary" />
            <p>No workflows yet. Start a workflow from the Projects page.</p>
          </CardContent>
        </Card>
      ) : (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid gap-4"
        >
          {workflows.map((workflow) => (
            <Card key={workflow.workflow_id} className="border-border-default bg-bg-panel/50 backdrop-blur-sm transition-all hover:border-border-emphasis hover:bg-bg-elevated/50">
              <CardContent className="flex items-center justify-between p-6">
                <div className="flex items-center gap-4">
                  <div className="rounded-lg bg-state-running-dim p-3">
                    <GitBranch className="h-6 w-6 text-state-running" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">
                      Workflow {workflow.workflow_id.slice(-8)}
                    </h3>
                    <p className="text-sm text-text-secondary">
                      Phase: {workflow.current_phase} • Progress: {workflow.progress_percent}%
                    </p>
                    {workflow.logs && workflow.logs.length > 0 && (
                      <p className="text-xs text-text-tertiary mt-1">
                        Last: {workflow.logs[workflow.logs.length - 1]}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className={getStatusColor(workflow.status)}>
                    {workflow.status}
                  </Badge>
                  {workflow.status === 'running' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCancel(workflow.workflow_id)}
                      className="text-state-error hover:bg-state-error-dim"
                    >
                      Cancel
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-text-secondary hover:text-text-primary hover:bg-bg-hover"
                  >
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
