'use client';

import { motion } from 'framer-motion';
import { Activity, User, FolderPlus, GitBranch, Trash2, Edit, Play } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';

const activities = [
  {
    id: '1',
    user: { name: 'System', avatar: '', initials: 'SYS' },
    action: 'created',
    entity: 'Project "Analytics Dashboard"',
    timestamp: new Date(Date.now() - 5 * 60000),
    icon: FolderPlus,
    color: 'text-state-success',
  },
  {
    id: '2',
    user: { name: 'AI Agent', avatar: '', initials: 'AI' },
    action: 'executed',
    entity: 'Workflow for "SaaS Platform"',
    timestamp: new Date(Date.now() - 15 * 60000),
    icon: Play,
    color: 'text-state-running',
  },
  {
    id: '3',
    user: { name: 'System', avatar: '', initials: 'SYS' },
    action: 'updated',
    entity: 'Agent "CEO"',
    timestamp: new Date(Date.now() - 30 * 60000),
    icon: Edit,
    color: 'text-state-warning',
  },
  {
    id: '4',
    user: { name: 'System', avatar: '', initials: 'SYS' },
    action: 'deleted',
    entity: 'Project "Old Demo"',
    timestamp: new Date(Date.now() - 60 * 60000),
    icon: Trash2,
    color: 'text-state-error',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4 },
  },
};

export default function ActivityPage() {
  const formatTime = (date: Date) => {
    const minutes = Math.floor((Date.now() - date.getTime()) / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <motion.div variants={itemVariants}>
        <h1 className="text-2xl font-bold text-text-primary">Activity Feed</h1>
        <p className="text-text-secondary">Recent actions and changes across the system</p>
      </motion.div>

      <motion.div variants={itemVariants} className="space-y-4">
        {activities.map((activity) => {
          const Icon = activity.icon;
          return (
            <Card key={activity.id} className="border-border-default bg-bg-panel hover:bg-bg-elevated transition-colors">
              <CardContent className="flex items-start gap-4 p-4">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={activity.user.avatar} />
                  <AvatarFallback className="bg-state-running-dim text-state-running">
                    {activity.user.initials}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Icon className={`h-4 w-4 ${activity.color}`} />
                    <p className="text-sm text-text-primary">
                      <span className="font-semibold">{activity.user.name}</span>
                      {' '}{activity.action}{' '}
                      <span className="font-semibold">{activity.entity}</span>
                    </p>
                  </div>
                  <p className="text-xs text-text-tertiary">{formatTime(activity.timestamp)}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </motion.div>
    </motion.div>
  );
}
