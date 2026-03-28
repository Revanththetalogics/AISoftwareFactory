'use client';

import { Wrench, Clock } from 'lucide-react';

export default function Maintenance() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-bg-base to-bg-surface">
      <div className="text-center max-w-2xl mx-auto p-8">
        {/* Maintenance Graphic */}
        <div className="relative mb-8">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full bg-accent-primary/10 blur-xl"></div>
          </div>
          <div className="relative flex items-center justify-center">
            <Wrench className="w-16 h-16 text-accent-primary animate-pulse" />
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-text-primary mb-3">
              System Maintenance
            </h1>
            <p className="text-text-secondary text-lg max-w-md mx-auto">
              We&apos;re currently performing scheduled maintenance to improve your experience. 
              We&apos;ll be back online shortly.
            </p>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center justify-center gap-3 mt-8">
            <div className="w-3 h-3 rounded-full bg-state-warning animate-pulse"></div>
            <span className="text-text-primary font-medium">Maintenance in progress</span>
          </div>

          {/* Estimated Time */}
          <div className="flex items-center justify-center gap-2 text-text-secondary">
            <Clock className="w-4 h-4" />
            <span>Estimated completion: 30 minutes</span>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-6 border-t border-border-subtle">
          <p className="text-sm text-text-tertiary">
            Thank you for your patience. Check back soon!
          </p>
        </div>
      </div>
    </div>
  );
}