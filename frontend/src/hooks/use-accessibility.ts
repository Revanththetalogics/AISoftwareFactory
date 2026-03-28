'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

interface ShortcutConfig {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  handler: () => void;
  description?: string;
  enabled?: boolean;
}

interface UseKeyboardShortcutsOptions {
  shortcuts: ShortcutConfig[];
  disabled?: boolean;
}

export const useKeyboardShortcuts = ({
  shortcuts,
  disabled = false
}: UseKeyboardShortcutsOptions) => {
  const activeShortcuts = useRef<ShortcutConfig[]>(shortcuts);

  useEffect(() => {
    activeShortcuts.current = shortcuts;
  }, [shortcuts]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (disabled) return;

    const matchingShortcut = activeShortcuts.current.find(shortcut => {
      if (shortcut.enabled === false) return false;
      
      const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
      const ctrlMatch = !!shortcut.ctrl === event.ctrlKey;
      const shiftMatch = !!shortcut.shift === event.shiftKey;
      const altMatch = !!shortcut.alt === event.altKey;
      const metaMatch = !!shortcut.meta === event.metaKey;

      return keyMatch && ctrlMatch && shiftMatch && altMatch && metaMatch;
    });

    if (matchingShortcut) {
      event.preventDefault();
      matchingShortcut.handler();
    }
  }, [disabled]);

  useEffect(() => {
    if (!disabled) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [handleKeyDown, disabled]);
};

// Predefined common shortcuts
export const COMMON_SHORTCUTS = {
  NAVIGATION: {
    HOME: { key: 'h', ctrl: true, description: 'Go to home/dashboard' },
    SEARCH: { key: 'k', ctrl: true, description: 'Open search' },
    HELP: { key: '/', description: 'Show help' }
  },
  ACTIONS: {
    SAVE: { key: 's', ctrl: true, description: 'Save current item' },
    REFRESH: { key: 'r', ctrl: true, description: 'Refresh page' },
    UNDO: { key: 'z', ctrl: true, description: 'Undo last action' },
    REDO: { key: 'y', ctrl: true, description: 'Redo action' }
  },
  NAVIGATION_ARROWS: {
    UP: { key: 'ArrowUp', description: 'Navigate up' },
    DOWN: { key: 'ArrowDown', description: 'Navigate down' },
    LEFT: { key: 'ArrowLeft', description: 'Navigate left' },
    RIGHT: { key: 'ArrowRight', description: 'Navigate right' }
  }
} as const;

// Focus management hook
export const useFocusTrap = (isActive: boolean) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTab = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement?.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement?.focus();
          }
        }
      }
    };

    container.addEventListener('keydown', handleTab);
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTab);
    };
  }, [isActive]);

  return containerRef;
};

// Skip to content hook
export const useSkipToContent = () => {
  const skipRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    const handleSkip = (event: KeyboardEvent) => {
      if (event.key === 'Tab' && event.altKey) {
        event.preventDefault();
        skipRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleSkip);
    return () => window.removeEventListener('keydown', handleSkip);
  }, []);

  return skipRef;
};

// Screen reader announcement hook
export const useScreenReaderAnnouncement = () => {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove after announcement is read
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }, []);

  return announce;
};

// High contrast mode hook
export const useHighContrast = () => {
  const [isHighContrast, setIsHighContrast] = useState(false);

  useEffect(() => {
    const checkHighContrast = () => {
      const mediaQuery = window.matchMedia('(prefers-contrast: high)');
      setIsHighContrast(mediaQuery.matches);
    };

    checkHighContrast();
    window.matchMedia('(prefers-contrast: high)').addEventListener('change', checkHighContrast);
    
    return () => {
      window.matchMedia('(prefers-contrast: high)').removeEventListener('change', checkHighContrast);
    };
  }, []);

  return isHighContrast;
};

// Reduced motion hook
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
};

// Focus visible indicator
export const useFocusVisible = () => {
  const [isFocusVisible, setIsFocusVisible] = useState(false);

  useEffect(() => {
    const handleKeyDown = () => setIsFocusVisible(true);
    const handleMouseDown = () => setIsFocusVisible(false);

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('mousedown', handleMouseDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  return isFocusVisible;
};