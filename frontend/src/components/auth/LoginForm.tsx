'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useLogin } from '@/lib/hooks';

function LoginFormContent() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const router = useRouter();
  const searchParams = useSearchParams();
  const returnUrl = searchParams.get('returnUrl') || '/dashboard';

  const login = useLogin();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login.mutateAsync({ username, password });
      router.push(decodeURIComponent(returnUrl));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <div className="w-full p-6 bg-bg-panel rounded-lg shadow-lg border border-border-default">
      <h2 className="text-2xl font-bold mb-6 text-center text-text-primary">Sign In</h2>

      {error && (
        <div className="mb-4 p-3 bg-state-error-dim text-state-error border border-state-error rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-text-primary">
            Username
          </label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="mt-1 block w-full px-3 py-2 border border-border-default rounded-md shadow-sm bg-bg-base text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-running focus:border-state-running transition-colors"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-text-primary">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1 block w-full px-3 py-2 border border-border-default rounded-md shadow-sm bg-bg-base text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-2 focus:ring-state-running focus:border-state-running transition-colors"
          />
        </div>

        <button
          type="submit"
          disabled={login.isPending}
          className="w-full flex justify-center py-2 px-4 rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-state-running to-state-running-emphasis hover:from-state-running-emphasis hover:to-state-running focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-state-running disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {login.isPending ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}

export function LoginForm() {
  return (
    <Suspense fallback={<div className="p-6 bg-bg-panel rounded-lg border border-border-default">Loading...</div>}>
      <LoginFormContent />
    </Suspense>
  );
}
