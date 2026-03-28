'use client';

import Link from 'next/link';
import { Home, ArrowLeft, Search } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-bg-base to-bg-surface">
      <div className="text-center max-w-2xl mx-auto p-8">
        {/* 404 Graphic */}
        <div className="relative mb-8">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full bg-accent-primary/10 blur-xl"></div>
          </div>
          <h1 className="relative text-9xl font-black text-accent-primary mb-4 tracking-tight">
            404
          </h1>
        </div>

        {/* Content */}
        <div className="space-y-6">
          <div>
            <h2 className="text-3xl font-bold text-text-primary mb-3">
              Page Not Found
            </h2>
            <p className="text-text-secondary text-lg max-w-md mx-auto">
              The page you&apos;re looking for doesn&apos;t exist or has been moved. 
              Don&apos;t worry, we&apos;ll help you get back on track.
            </p>
          </div>

          {/* Helpful Links */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8">
            <Link
              href="/dashboard"
              className="flex items-center justify-center gap-2 px-6 py-4 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <Home className="w-5 h-5" />
              Dashboard
            </Link>
            
            <Link
              href="/dashboard/projects"
              className="flex items-center justify-center gap-2 px-6 py-4 border border-border-default text-text-primary rounded-lg hover:bg-bg-surface transition-all duration-200 font-medium"
            >
              <Search className="w-5 h-5" />
              Browse Projects
            </Link>
          </div>

          <div className="pt-4">
            <button
              onClick={() => window.history.back()}
              className="inline-flex items-center gap-2 px-4 py-2 text-text-secondary hover:text-text-primary transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Go Back
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-6 border-t border-border-subtle">
          <p className="text-sm text-text-tertiary">
            Need help? Contact support or check our documentation.
          </p>
        </div>
      </div>
    </div>
  );
}
