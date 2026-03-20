import * as React from "react"
import { Input as InputPrimitive } from "@base-ui/react/input"
import { motion } from "framer-motion"
import { Loader2, CheckCircle2, XCircle } from "lucide-react"

import { cn } from "@/lib/utils"

interface InputProps extends React.ComponentProps<"input"> {
  validationState?: 'valid' | 'invalid' | 'validating';
  asyncValidation?: {
    isChecking: boolean;
    message?: string;
  };
  helpText?: string;
  errorText?: string;
  compact?: boolean;
  leftElement?: React.ReactNode;
  rightElement?: React.ReactNode;
}

function Input({ 
  className, 
  type, 
  validationState,
  asyncValidation,
  helpText,
  errorText,
  compact,
  leftElement,
  rightElement,
  ...props 
}: InputProps) {
  const isInvalid = validationState === 'invalid' || errorText;
  const isValidating = validationState === 'validating' || asyncValidation?.isChecking;
  const isValid = validationState === 'valid';

  return (
    <div className="w-full">
      <div className="relative">
        {/* Left element */}
        {leftElement && (
          <div className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-tertiary">
            {leftElement}
          </div>
        )}

        <InputPrimitive
          type={type}
          data-slot="input"
          className={cn(
            "h-8 w-full min-w-0 rounded-lg border bg-transparent px-2.5 py-1 text-base transition-all outline-none file:inline-flex file:h-6 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-text-tertiary disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
            // State-driven borders
            isValid && "border-state-success focus-visible:border-state-success focus-visible:ring-3 focus-visible:ring-state-success/20",
            isInvalid && "border-state-error focus-visible:border-state-error focus-visible:ring-3 focus-visible:ring-state-error/20 aria-invalid:border-state-error aria-invalid:ring-3 aria-invalid:ring-state-error/20",
            !isValid && !isInvalid && "border-border-default focus-visible:border-state-running focus-visible:ring-3 focus-visible:ring-state-running/20",
            // Layout adjustments
            leftElement && "pl-9",
            (rightElement || isValidating || isValid || isInvalid) && "pr-9",
            compact && "h-7 text-sm py-1",
            className
          )}
          {...props}
        />

        {/* Right elements - validation indicators */}
        <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {isValidating && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
            >
              <Loader2 className="w-4 h-4 text-state-running animate-spin" />
            </motion.div>
          )}
          
          {isValid && !isValidating && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <CheckCircle2 className="w-4 h-4 text-state-success" />
            </motion.div>
          )}
          
          {isInvalid && !isValidating && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <XCircle className="w-4 h-4 text-state-error" />
            </motion.div>
          )}

          {!isValidating && !isValid && !isInvalid && rightElement && (
            <div className="text-text-tertiary">
              {rightElement}
            </div>
          )}
        </div>
      </div>

      {/* Help/Error text */}
      {(helpText || errorText) && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "mt-1.5 text-xs font-medium",
            errorText ? "text-state-error" : "text-text-secondary"
          )}
        >
          {errorText || helpText}
        </motion.div>
      )}

      {/* Async validation message */}
      {asyncValidation?.message && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-1.5 text-xs text-text-tertiary"
        >
          {asyncValidation.message}
        </motion.div>
      )}
    </div>
  )
}

export { Input }
