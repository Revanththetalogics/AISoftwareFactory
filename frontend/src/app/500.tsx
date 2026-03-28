'use client';

import Link from 'next/link';
import { Server, Home, RefreshCw } from 'lucide-react';

export default function Custom500() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-bg-base to-bg-surface">
      <div className="text-center max-w-2xl mx-auto p-8">
        {/* 500 Graphic */}
        <div className="relative mb-8">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full bg-state-error-dim/20 blur-xl"></div>
          </div>
          <div className="relative flex items-center justify-center">
            <Server className="w-16 h-16 text-state-error mr-4" />
            <div className="text-7xl font-black text-text-secondary opacity-20">500</div>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-text-primary mb-3">
              Server Error
            </h1>
            <p className="text-text-secondary text-lg max-w-md mx-auto">
              Something went wrong on our end. We&apos;re working to fix the issue right now.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8">
            <button
              onClick={() => window.location.reload()}
              className="flex items-center justify-center gap-2 px-6 py-4 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <RefreshCw className="w-5 h-5" />
              Reload Page
            </button>
            
            <Link
              href="/dashboard"
              className="flex items-center justify-center gap-2 px-6 py-4 border border-border-default text-text-primary rounded-lg hover:bg-bg-surface transition-all duration-200 font-medium"
            >
              <Home className="w-5 h-5" />
              Dashboard
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-6 border-t border-border-subtle">
          <p className="text-sm text-text-tertiary">
            Our team has been notified about this issue.
          </p>
        </div>
      </div>
    </div>
  );
}