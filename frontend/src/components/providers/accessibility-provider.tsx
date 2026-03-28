'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { useKeyboardShortcuts, COMMON_SHORTCUTS } from '@/hooks/use-accessibility';

interface AccessibilityContextType {
  isHighContrast: boolean;
  prefersReducedMotion: boolean;
  focusVisible: boolean;
  shortcutsEnabled: boolean;
  toggleShortcuts: () => void;
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | null>(null);

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export const AccessibilityProvider = ({ children }: AccessibilityProviderProps) => {
  const [shortcutsEnabled, setShortcutsEnabled] = useState(true);
  const [announcements, setAnnouncements] = useState<Array<{message: string, priority: 'polite' | 'assertive'}>>([]);

  // Check system preferences
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [focusVisible, setFocusVisible] = useState(false);

  useEffect(() => {
    // High contrast detection
    const highContrastMedia = window.matchMedia('(prefers-contrast: high)');
    setIsHighContrast(highContrastMedia.matches);
    highContrastMedia.addEventListener('change', (e) => setIsHighContrast(e.matches));

    // Reduced motion detection
    const reducedMotionMedia = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(reducedMotionMedia.matches);
    reducedMotionMedia.addEventListener('change', (e) => setPrefersReducedMotion(e.matches));

    // Focus visible detection
    const handleKeyDown = () => setFocusVisible(true);
    const handleMouseDown = () => setFocusVisible(false);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('mousedown', handleMouseDown);

    return () => {
      highContrastMedia.removeEventListener('change', (e) => setIsHighContrast(e.matches));
      reducedMotionMedia.removeEventListener('change', (e) => setPrefersReducedMotion(e.matches));
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  // Handle announcements
  useEffect(() => {
    if (announcements.length > 0) {
      const announcement = announcements[0];
      const element = document.createElement('div');
      element.setAttribute('aria-live', announcement.priority);
      element.setAttribute('aria-atomic', 'true');
      element.className = 'sr-only';
      element.textContent = announcement.message;
      
      document.body.appendChild(element);
      
      setTimeout(() => {
        document.body.removeChild(element);
        setAnnouncements(prev => prev.slice(1));
      }, 1000);
    }
  }, [announcements]);

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    setAnnouncements(prev => [...prev, { message, priority }]);
  };

  const toggleShortcuts = () => {
    setShortcutsEnabled(!shortcutsEnabled);
    announce(`Keyboard shortcuts ${!shortcutsEnabled ? 'enabled' : 'disabled'}`);
  };

  // Register global shortcuts
  useKeyboardShortcuts({
    shortcuts: [
      {
        ...COMMON_SHORTCUTS.NAVIGATION.HOME,
        handler: () => {
          window.location.href = '/dashboard';
          announce('Navigated to dashboard');
        },
        enabled: shortcutsEnabled
      },
      {
        ...COMMON_SHORTCUTS.ACTIONS.REFRESH,
        handler: () => {
          window.location.reload();
          announce('Page refreshed');
        },
        enabled: shortcutsEnabled
      },
      {
        key: '?',
        handler: () => {
          // Show keyboard shortcuts modal
          announce('Keyboard shortcuts help opened');
        },
        enabled: shortcutsEnabled
      },
      {
        key: 'Escape',
        handler: () => {
          // Close modals, dropdowns, etc.
          const activeElement = document.activeElement as HTMLElement;
          if (activeElement?.tagName === 'DIALOG' || activeElement?.closest('[role="dialog"]')) {
            activeElement.blur();
          }
          announce('Dialog closed');
        },
        enabled: shortcutsEnabled
      }
    ],
    disabled: !shortcutsEnabled
  });

  const contextValue: AccessibilityContextType = {
    isHighContrast,
    prefersReducedMotion,
    focusVisible,
    shortcutsEnabled,
    toggleShortcuts,
    announce
  };

  return (
    <AccessibilityContext.Provider value={contextValue}>
      {children}
      {/* Accessibility announcements container */}
      <div aria-live="polite" aria-atomic="true" className="sr-only" id="a11y-announcer" />
    </AccessibilityContext.Provider>
  );
};

// Accessible Skip Link Component
export const SkipToContentLink = () => {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-bg-surface focus:text-text-primary focus:px-4 focus:py-2 focus:rounded focus:border focus:border-accent-primary focus:outline-none"
    >
      Skip to main content
    </a>
  );
};

// Accessible Focus Ring Component
export const FocusRing = ({ children, className = '' }: { 
  children: React.ReactNode; 
  className?: string;
}) => {
  return (
    <div 
      className={`${className} focus-within:ring-2 focus-within:ring-accent-primary focus-within:ring-offset-2 focus-within:ring-offset-bg-base rounded`}
    >
      {children}
    </div>
  );
};