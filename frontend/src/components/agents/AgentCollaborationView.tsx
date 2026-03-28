'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Code2,
  TestTube,
  Rocket,
  MessageSquare,
  ArrowRight,
  Zap
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useEventStream } from '@/lib/hooks';

interface Agent {
  id: string;
  name: string;
  role: string;
  icon: React.ElementType;
  color: string;
  position: { x: number; y: number };
  status: 'idle' | 'working' | 'thinking';
  currentTask?: string;
}

interface Message {
  id: string;
  from: string;
  to: string;
  content: string;
  timestamp: string;
  type: 'request' | 'response' | 'broadcast';
}

const agents: Agent[] = [
  { 
    id: 'pm', 
    name: 'Product Manager', 
    role: 'pm',
    icon: Brain, 
    color: 'text-purple-400',
    position: { x: 50, y: 20 },
    status: 'working',
    currentTask: 'Defining user stories',
  },
  { 
    id: 'architect', 
    name: 'Architect', 
    role: 'architect',
    icon: Brain, 
    color: 'text-blue-400',
    position: { x: 20, y: 50 },
    status: 'thinking',
    currentTask: 'Designing database schema',
  },
  { 
    id: 'backend', 
    name: 'Backend Dev', 
    role: 'backend',
    icon: Code2, 
    color: 'text-green-400',
    position: { x: 80, y: 50 },
    status: 'idle',
  },
  { 
    id: 'frontend', 
    name: 'Frontend Dev', 
    role: 'frontend',
    icon: Code2, 
    color: 'text-yellow-400',
    position: { x: 35, y: 80 },
    status: 'working',
    currentTask: 'Building UI components',
  },
  { 
    id: 'qa', 
    name: 'QA Engineer', 
    role: 'qa',
    icon: TestTube, 
    color: 'text-pink-400',
    position: { x: 65, y: 80 },
    status: 'idle',
  },
  { 
    id: 'devops', 
    name: 'DevOps', 
    role: 'devops',
    icon: Rocket, 
    color: 'text-orange-400',
    position: { x: 50, y: 50 },
    status: 'thinking',
    currentTask: 'Setting up CI/CD',
  },
];

const mockMessages: Message[] = [
  { 
    id: '1', 
    from: 'pm', 
    to: 'architect', 
    content: 'Need to support 10k concurrent users. Can you design for that scale?',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    type: 'request',
  },
  { 
    id: '2', 
    from: 'architect', 
    to: 'pm', 
    content: 'Yes, I\'ll design a horizontally scalable architecture with Redis caching and read replicas.',
    timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
    type: 'response',
  },
  { 
    id: '3', 
    from: 'architect', 
    to: 'backend', 
    content: 'Please implement the auth service with JWT tokens and refresh token rotation.',
    timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    type: 'request',
  },
  { 
    id: '4', 
    from: 'backend', 
    to: 'architect', 
    content: 'On it. I\'ll use FastAPI with async SQLAlchemy for the auth endpoints.',
    timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
    type: 'response',
  },
  { 
    id: '5', 
    from: 'frontend', 
    to: 'backend', 
    content: 'What\'s the API schema for the login endpoint?',
    timestamp: new Date(Date.now() - 1000 * 60 * 1).toISOString(),
    type: 'request',
  },
];

interface AgentNodeProps {
  agent: Agent;
  isActive: boolean;
}

function AgentNode({ agent, isActive }: AgentNodeProps) {
  const Icon = agent.icon;
  
  return (
    <motion.div
      className="absolute transform -translate-x-1/2 -translate-y-1/2"
      style={{ left: `${agent.position.x}%`, top: `${agent.position.y}%` }}
      animate={{
        scale: isActive ? 1.1 : 1,
      }}
      transition={{ duration: 0.3 }}
    >
      <div className={cn(
        'relative flex flex-col items-center gap-1',
        agent.status === 'working' && 'animate-pulse'
      )}>
        {/* Status Ring */}
        <div className={cn(
          'absolute -inset-2 rounded-full opacity-50',
          agent.status === 'working' && 'bg-state-running/20 animate-ping',
          agent.status === 'thinking' && 'bg-state-queued/20',
        )} />
        
        {/* Avatar */}
        <div className={cn(
          'relative flex h-12 w-12 items-center justify-center rounded-full border-2 bg-bg-panel',
          agent.color.replace('text-', 'border-')
        )}>
          <Icon className={cn('h-6 w-6', agent.color)} />
          
          {/* Status Dot */}
          <div className={cn(
            'absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-bg-panel',
            agent.status === 'working' ? 'bg-state-running' :
            agent.status === 'thinking' ? 'bg-state-queued' :
            'bg-state-idle'
          )} />
        </div>
        
        {/* Label */}
        <div className="text-center">
          <p className="text-xs font-medium text-text-primary whitespace-nowrap">{agent.name}</p>
          {agent.currentTask && (
            <p className="text-[10px] text-text-tertiary max-w-[100px] truncate">{agent.currentTask}</p>
          )}
        </div>
      </div>
    </motion.div>
  );
}

interface MessageFlowProps {
  message: Message;
  agents: Agent[];
}

function MessageFlow({ message, agents }: MessageFlowProps) {
  const fromAgent = agents.find(a => a.id === message.from);
  const toAgent = agents.find(a => a.id === message.to);
  
  if (!fromAgent || !toAgent) return null;

  // eslint-disable-next-line react-hooks/purity -- Time comparison for UI highlighting
  const isRecent = new Date(message.timestamp).getTime() > Date.now() - 1000 * 60 * 2;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'flex items-start gap-3 p-3 rounded-lg',
        isRecent ? 'bg-state-queued-dim/30' : 'bg-bg-base/30'
      )}
    >
      <div className="flex items-center gap-1 text-xs text-text-tertiary">
        <span className={cn('font-medium', fromAgent.color)}>{fromAgent.name}</span>
        <ArrowRight className="h-3 w-3" />
        <span className={cn('font-medium', toAgent.color)}>{toAgent.name}</span>
      </div>
      <p className="text-sm text-text-secondary flex-1">{message.content}</p>
    </motion.div>
  );
}

interface AgentCollaborationViewProps {
// Remove unused _projectId parameter
  className?: string;
}

export function AgentCollaborationView({ className }: AgentCollaborationViewProps) {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [activeAgents, setActiveAgents] = useState<string[]>(['pm', 'architect']);
  const { lastMessage } = useEventStream();

  useEffect(() => {
    if (lastMessage?.type === 'agent_message') {
      const msg = lastMessage.data as Message;
      // eslint-disable-next-line react-hooks/set-state-in-effect -- Handling external SSE events
      setMessages(prev => [msg, ...prev].slice(0, 50));
       
      setActiveAgents([msg.from, msg.to]);
    }
  }, [lastMessage]);

  return (
    <Card className={cn('glass-panel border-border-default/50', className)}>
      <CardHeader>
        <CardTitle className="text-lg text-text-primary flex items-center gap-2">
          <Zap className="h-5 w-5 text-state-queued" />
          Agent Collaboration
        </CardTitle>
        <p className="text-sm text-text-secondary">
          Real-time AI team communication
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Collaboration Map */}
        <div className="relative h-[300px] rounded-lg bg-bg-base/50 border border-border-default/30 overflow-hidden">
          {/* Connection Lines (SVG) */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {messages.slice(0, 5).map((msg, i) => {
              const from = agents.find(a => a.id === msg.from);
              const to = agents.find(a => a.id === msg.to);
              if (!from || !to) return null;
              
              return (
                <motion.line
                  key={msg.id}
                  x1={`${from.position.x}%`}
                  y1={`${from.position.y}%`}
                  x2={`${to.position.x}%`}
                  y2={`${to.position.y}%`}
                  stroke="var(--state-queued)"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 0.3 }}
                  transition={{ duration: 1, delay: i * 0.1 }}
                />
              );
            })}
          </svg>

          {/* Agent Nodes */}
          {agents.map((agent) => (
            <AgentNode 
              key={agent.id} 
              agent={agent} 
              isActive={activeAgents.includes(agent.id)}
            />
          ))}
        </div>

        {/* Message Feed */}
        <div>
          <h4 className="text-sm font-medium text-text-primary mb-2 flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Recent Messages
          </h4>
          <ScrollArea className="h-[200px] rounded-lg border border-border-default/30 bg-bg-base/30 p-2">
            <div className="space-y-2">
              {messages.map((message) => (
                <MessageFlow key={message.id} message={message} agents={agents} />
              ))}
            </div>
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
}
