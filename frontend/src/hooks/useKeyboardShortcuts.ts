'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useHotkeys } from 'react-hotkeys-hook';

export function useKeyboardShortcuts() {
  const router = useRouter();
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  useHotkeys('ctrl+k, cmd+k', (e) => {
    e.preventDefault();
    setCommandPaletteOpen(true);
  }, { enableOnFormTags: true });

  useHotkeys('ctrl+n, cmd+n', (e) => {
    e.preventDefault();
    const event = new CustomEvent('create-project');
    window.dispatchEvent(event);
  });

  useHotkeys('/', (e) => {
    e.preventDefault();
    const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"]') as HTMLInputElement;
    searchInput?.focus();
  });

  useHotkeys('g p', () => router.push('/projects'));
  useHotkeys('g w', () => router.push('/workflows'));
  useHotkeys('g a', () => router.push('/agents'));
  useHotkeys('g d', () => router.push('/deployment'));
  useHotkeys('g t', () => router.push('/testing'));
  useHotkeys('g h', () => router.push('/'));

  useHotkeys('esc', () => {
    setCommandPaletteOpen(false);
  });

  return { commandPaletteOpen, setCommandPaletteOpen };
}
