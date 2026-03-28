'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useAccessibility } from '@/components/providers/accessibility-provider';
import { COMMON_SHORTCUTS } from '@/hooks/use-accessibility';
import { X, Keyboard } from 'lucide-react';

interface ShortcutCategory {
  title: string;
  shortcuts: Array<{
    key: string;
    description: string;
    modifier?: string;
  }>;
}

const SHORTCUT_CATEGORIES: ShortcutCategory[] = [
  {
    title: 'Navigation',
    shortcuts: [
      { key: 'H', description: 'Go to home/dashboard', modifier: 'Ctrl' },
      { key: 'K', description: 'Open search', modifier: 'Ctrl' },
      { key: '/', description: 'Show help' },
      { key: '← → ↑ ↓', description: 'Navigate between items' }
    ]
  },
  {
    title: 'Actions',
    shortcuts: [
      { key: 'S', description: 'Save current item', modifier: 'Ctrl' },
      { key: 'R', description: 'Refresh page', modifier: 'Ctrl' },
      { key: 'Z', description: 'Undo last action', modifier: 'Ctrl' },
      { key: 'Y', description: 'Redo action', modifier: 'Ctrl' }
    ]
  },
  {
    title: 'Interface',
    shortcuts: [
      { key: 'Escape', description: 'Close dialogs/modals' },
      { key: '?', description: 'Show this help' },
      { key: 'Tab', description: 'Move focus forward' },
      { key: 'Shift + Tab', description: 'Move focus backward' }
    ]
  }
];

export const KeyboardShortcutsModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { shortcutsEnabled, toggleShortcuts, announce } = useAccessibility();

  useEffect(() => {
    const handleHelpShortcut = (event: KeyboardEvent) => {
      if (event.key === '/' && !event.ctrlKey && !event.metaKey) {
        event.preventDefault();
        setIsOpen(true);
        announce('Keyboard shortcuts help opened');
      }
    };

    window.addEventListener('keydown', handleHelpShortcut);
    return () => window.removeEventListener('keydown', handleHelpShortcut);
  }, [announce]);

  const handleClose = () => {
    setIsOpen(false);
    announce('Keyboard shortcuts help closed');
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(true)}
        className="gap-2"
        aria-label="Show keyboard shortcuts"
      >
        <Keyboard className="h-4 w-4" />
        Shortcuts
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader className="flex-shrink-0">
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2">
                <Keyboard className="h-5 w-5" />
                Keyboard Shortcuts
              </DialogTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClose}
                aria-label="Close"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex items-center justify-between pt-2">
              <p className="text-sm text-text-secondary">
                Press <kbd className="px-2 py-1 bg-bg-surface border border-border-default rounded text-xs">?</kbd> anytime to open this help
              </p>
              
              <Button
                variant={shortcutsEnabled ? "outline" : "default"}
                size="sm"
                onClick={toggleShortcuts}
              >
                {shortcutsEnabled ? 'Disable Shortcuts' : 'Enable Shortcuts'}
              </Button>
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto py-4">
            <div className="space-y-8">
              {SHORTCUT_CATEGORIES.map((category) => (
                <div key={category.title}>
                  <h3 className="text-lg font-semibold text-text-primary mb-4 pb-2 border-b border-border-subtle">
                    {category.title}
                  </h3>
                  
                  <div className="grid gap-3">
                    {category.shortcuts.map((shortcut, index) => (
                      <div 
                        key={index} 
                        className="flex items-center justify-between p-3 rounded-lg bg-bg-surface border border-border-default hover:bg-bg-base transition-colors"
                      >
                        <span className="text-text-primary">
                          {shortcut.description}
                        </span>
                        
                        <div className="flex items-center gap-2">
                          {shortcut.modifier && (
                            <kbd className="px-2 py-1 bg-bg-base border border-border-default rounded text-xs font-mono">
                              {shortcut.modifier}
                            </kbd>
                          )}
                          <kbd className="px-2 py-1 bg-accent-primary/10 border border-accent-primary/20 rounded text-xs font-mono text-accent-primary">
                            {shortcut.key}
                          </kbd>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex-shrink-0 pt-4 border-t border-border-subtle">
            <div className="flex items-center justify-between text-sm text-text-secondary">
              <div className="flex items-center gap-4">
                <span>Shortcuts are {shortcutsEnabled ? 'enabled' : 'disabled'}</span>
                <span>•</span>
                <span>Press Escape to close</span>
              </div>
              
              <Button variant="ghost" size="sm" onClick={handleClose}>
                Close
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};