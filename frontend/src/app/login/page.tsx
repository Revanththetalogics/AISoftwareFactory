'use client';

import { LoginForm } from '@/components/auth/LoginForm';
import { motion } from 'framer-motion';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md p-6"
      >
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-state-running to-state-running-emphasis flex items-center justify-center">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-text-primary mb-2">
            ThetaAI Software Factory
          </h1>
          <p className="text-text-secondary">
            Sign in to access your AI-powered development environment
          </p>
        </div>
        
        <LoginForm />
        
        <div className="mt-6 p-4 rounded-lg bg-bg-panel border border-border-default">
          <h3 className="text-sm font-semibold text-text-primary mb-2">
            Test Credentials (Development)
          </h3>
          <div className="space-y-2 text-xs text-text-secondary">
            <div className="flex justify-between">
              <span>Admin:</span>
              <code className="text-text-tertiary">admin / admin123</code>
            </div>
            <div className="flex justify-between">
              <span>Developer:</span>
              <code className="text-text-tertiary">developer / dev123</code>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
