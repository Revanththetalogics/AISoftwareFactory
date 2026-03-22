'use client';

import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { type ReactNode } from 'react';

interface ThemeProviderProps {
  children: ReactNode;
  forcedTheme?: string;
}

export function ThemeProvider({ children, forcedTheme }: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="light"
      enableSystem={false}
      disableTransitionOnChange
      forcedTheme={forcedTheme}
      themes={['dark', 'light']}
    >
      {children}
    </NextThemesProvider>
  );
}
