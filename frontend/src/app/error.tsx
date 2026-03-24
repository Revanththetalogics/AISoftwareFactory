'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <div className="text-center max-w-md mx-auto p-8">
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-state-error-dim flex items-center justify-center">
          <svg className="w-8 h-8 text-state-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-text-primary mb-2">Something went wrong</h1>
        <p className="text-text-secondary mb-6">
          An unexpected error occurred. Our team has been notified.
        </p>
        <div className="space-y-3">
          <button
            onClick={reset}
            className="w-full px-6 py-3 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 transition-colors font-medium"
          >
            Try Again
          </button>
          <a
            href="/dashboard"
            className="block w-full px-6 py-3 border border-border-default text-text-primary rounded-lg hover:bg-bg-surface transition-colors font-medium"
          >
            Go to Dashboard
          </a>
        </div>
        {error.digest && (
          <p className="mt-4 text-xs text-text-tertiary">Error ID: {error.digest}</p>
        )}
      </div>
    </div>
  );
}
