'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';

export default function UnauthorizedPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-base">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="text-center p-8 max-w-md"
      >
        <div className="mb-6">
          <div className="mx-auto w-20 h-20 rounded-full bg-state-error-dim flex items-center justify-center">
            <svg
              className="w-10 h-10 text-state-error"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
        </div>

        <h1 className="text-3xl font-bold text-text-primary mb-3">
          Access Denied
        </h1>
        
        <p className="text-text-secondary mb-6">
          You don&apos;t have permission to access this resource. Please contact your administrator if you believe this is an error.
        </p>

        <div className="flex gap-3 justify-center">
          <Button
            onClick={() => router.back()}
            variant="outline"
            className="border-border-default text-text-primary hover:bg-bg-panel"
          >
            Go Back
          </Button>
          
          <Button
            onClick={() => router.push('/dashboard')}
            className="bg-gradient-to-r from-state-running to-state-running-emphasis text-white hover:from-state-running-emphasis hover:to-state-running"
          >
            Go to Dashboard
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
