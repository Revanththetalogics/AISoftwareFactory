'use client';

import { useEffect } from 'react';
import { AlertTriangle, RotateCcw, Home, Bug } from 'lucide-react';

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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-bg-base to-bg-surface">
      <div className="text-center max-w-2xl mx-auto p-8">
        {/* Error Icon */}
        <div className="relative mb-8">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full bg-state-error-dim/20 blur-xl"></div>
          </div>
          <div className="relative w-20 h-20 mx-auto rounded-full bg-state-error-dim flex items-center justify-center mb-6">
            <AlertTriangle className="w-10 h-10 text-state-error" />
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-text-primary mb-3">
              Something went wrong
            </h1>
            <p className="text-text-secondary text-lg max-w-md mx-auto">
              An unexpected error occurred. Our team has been notified and is working to fix it.
            </p>
          </div>

          {/* Error Details (in development) */}
          {process.env.NODE_ENV === 'development' && error.message && (
            <div className="bg-bg-surface border border-border-default rounded-lg p-4 text-left max-w-lg mx-auto">
              <div className="flex items-center gap-2 mb-2">
                <Bug className="w-4 h-4 text-state-warning" />
                <span className="font-medium text-text-primary">Error Details</span>
              </div>
              <pre className="text-sm text-text-secondary overflow-x-auto">
                {error.message}
              </pre>
            </div>
          )}

          {/* Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8">
            <button
              onClick={reset}
              className="flex items-center justify-center gap-2 px-6 py-4 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <RotateCcw className="w-5 h-5" />
              Try Again
            </button>
            
            <a
              href="/dashboard"
              className="flex items-center justify-center gap-2 px-6 py-4 border border-border-default text-text-primary rounded-lg hover:bg-bg-surface transition-all duration-200 font-medium"
            >
              <Home className="w-5 h-5" />
              Dashboard
            </a>
          </div>

          {/* Error ID */}
          {error.digest && (
            <div className="pt-4">
              <p className="text-xs text-text-tertiary">
                Error ID: <span className="font-mono">{error.digest}</span>
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-12 pt-6 border-t border-border-subtle">
          <p className="text-sm text-text-tertiary">
            Still having issues? Contact support with the error ID above.
          </p>
        </div>
      </div>
    </div>
  );
}
