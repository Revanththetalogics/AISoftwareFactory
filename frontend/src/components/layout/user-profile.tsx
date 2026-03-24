'use client';

import { useTheme } from 'next-themes';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Sun, User, Settings, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/lib/auth';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="text-text-secondary hover:bg-bg-hover hover:text-text-primary"
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
    >
      <AnimatePresence mode="wait">
        {theme === 'dark' ? (
          <motion.div
            key="moon"
            initial={{ scale: 0, rotate: -90 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 90 }}
            transition={{ duration: 0.2 }}
          >
            <Moon className="h-5 w-5" aria-hidden="true" />
          </motion.div>
        ) : (
          <motion.div
            key="sun"
            initial={{ scale: 0, rotate: 90 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: -90 }}
            transition={{ duration: 0.2 }}
          >
            <Sun className="h-5 w-5" aria-hidden="true" />
          </motion.div>
        )}
      </AnimatePresence>
    </Button>
  );
}

export function UserProfile() {
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const displayName = user?.username || 'User';
  const displayEmail = user?.email || '';
  const initials = getInitials(displayName);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <Button
          variant="ghost"
          className="relative h-9 w-9 rounded-full border border-border-default bg-bg-panel hover:bg-bg-hover"
          aria-label="User menu"
          aria-haspopup="menu"
        >
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-gradient-to-br from-state-queued to-state-running text-text-primary text-sm">
              {initials}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56 border-border-default bg-bg-elevated" role="menu" aria-label="User settings">
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium text-text-primary">{displayName}</p>
            {displayEmail && (
              <p className="text-xs text-text-secondary">{displayEmail}</p>
            )}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-border-default" />
        <DropdownMenuItem className="text-text-secondary focus:bg-bg-hover focus:text-text-primary" role="menuitem">
          <User className="mr-2 h-4 w-4" aria-hidden="true" />
          Profile
        </DropdownMenuItem>
        <DropdownMenuItem className="text-text-secondary focus:bg-bg-hover focus:text-text-primary" role="menuitem">
          <Settings className="mr-2 h-4 w-4" aria-hidden="true" />
          Settings
        </DropdownMenuItem>
        <DropdownMenuSeparator className="bg-border-default" />
        <DropdownMenuItem 
          onClick={handleLogout}
          className="text-state-error focus:bg-bg-hover focus:text-state-error cursor-pointer"
          role="menuitem"
        >
          <LogOut className="mr-2 h-4 w-4" aria-hidden="true" />
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
