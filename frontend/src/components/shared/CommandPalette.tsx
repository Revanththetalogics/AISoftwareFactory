'use client';

import { useRouter } from 'next/navigation';
import { Plus, Folder, GitBranch, Bot, Rocket, TestTube, Home, Settings } from 'lucide-react';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command';

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();

  const handleCommand = (command: string) => {
    onOpenChange(false);
    
    switch (command) {
      case 'new-project':
        window.dispatchEvent(new CustomEvent('create-project'));
        break;
      case 'projects':
        router.push('/projects');
        break;
      case 'workflows':
        router.push('/workflows');
        break;
      case 'agents':
        router.push('/agents');
        break;
      case 'deployment':
        router.push('/deployment');
        break;
      case 'testing':
        router.push('/testing');
        break;
      case 'dashboard':
        router.push('/');
        break;
      case 'settings':
        router.push('/settings');
        break;
    }
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Actions">
          <CommandItem onSelect={() => handleCommand('new-project')}>
            <Plus className="mr-2 h-4 w-4" />
            <span>Create New Project</span>
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Navigate">
          <CommandItem onSelect={() => handleCommand('dashboard')}>
            <Home className="mr-2 h-4 w-4" />
            <span>Dashboard</span>
            <span className="ml-auto text-xs text-muted-foreground">G H</span>
          </CommandItem>
          <CommandItem onSelect={() => handleCommand('projects')}>
            <Folder className="mr-2 h-4 w-4" />
            <span>Projects</span>
            <span className="ml-auto text-xs text-muted-foreground">G P</span>
          </CommandItem>
          <CommandItem onSelect={() => handleCommand('workflows')}>
            <GitBranch className="mr-2 h-4 w-4" />
            <span>Workflows</span>
            <span className="ml-auto text-xs text-muted-foreground">G W</span>
          </CommandItem>
          <CommandItem onSelect={() => handleCommand('agents')}>
            <Bot className="mr-2 h-4 w-4" />
            <span>Agents</span>
            <span className="ml-auto text-xs text-muted-foreground">G A</span>
          </CommandItem>
          <CommandItem onSelect={() => handleCommand('deployment')}>
            <Rocket className="mr-2 h-4 w-4" />
            <span>Deployment</span>
            <span className="ml-auto text-xs text-muted-foreground">G D</span>
          </CommandItem>
          <CommandItem onSelect={() => handleCommand('testing')}>
            <TestTube className="mr-2 h-4 w-4" />
            <span>Testing</span>
            <span className="ml-auto text-xs text-muted-foreground">G T</span>
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Settings">
          <CommandItem onSelect={() => handleCommand('settings')}>
            <Settings className="mr-2 h-4 w-4" />
            <span>Settings</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
