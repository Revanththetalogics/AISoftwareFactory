// Comprehensive error boundary system for React applications
// Provides centralized error handling, logging, and recovery mechanisms

import React, { Component, ReactNode } from 'react';

export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';
export type ErrorCategory = 'network' | 'validation' | 'authentication' | 'runtime' | 'unknown';

export interface ErrorInfo {
  error: Error;
  errorInfo?: React.ErrorInfo;
  componentStack?: string;
  timestamp: string;
  severity: ErrorSeverity;
  category: ErrorCategory;
  context?: Record<string, unknown>;
  recoveryAttempted: boolean;
  recoverySuccessful: boolean;
}

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: React.ComponentType<{ error: ErrorInfo; resetError: () => void }>;
  onError?: (error: ErrorInfo) => void;
  onRecover?: (error: ErrorInfo) => boolean;
  logErrors?: boolean;
  recoveryAttempts?: number;
  recoveryDelay?: number;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  errorInfo: ErrorInfo | null;
  recoveryAttempts: number;
  isRecovering: boolean;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public static defaultProps: Partial<ErrorBoundaryProps> = {
    logErrors: true,
    recoveryAttempts: 3,
    recoveryDelay: 1000
  };

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      errorInfo: null,
      recoveryAttempts: 0,
      isRecovering: false
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      errorInfo: {
        error,
        timestamp: new Date().toISOString(),
        severity: 'high',
        category: 'runtime',
        recoveryAttempted: false,
        recoverySuccessful: false
      }
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    const errorInfoObj: ErrorInfo = {
      error,
      errorInfo,
      componentStack: errorInfo.componentStack || undefined,
      timestamp: new Date().toISOString(),
      severity: this.categorizeError(error),
      category: this.determineCategory(error),
      recoveryAttempted: false,
      recoverySuccessful: false
    };

    this.setState({ errorInfo: errorInfoObj });

    // Log error if enabled
    if (this.props.logErrors) {
      this.logError(errorInfoObj);
    }

    // Call custom error handler
    if (this.props.onError) {
      this.props.onError(errorInfoObj);
    }
  }

  private categorizeError(error: Error): ErrorSeverity {
    const message = error.message.toLowerCase();
    
    if (message.includes('network') || message.includes('fetch') || message.includes('timeout')) {
      return 'medium';
    }
    
    if (message.includes('authentication') || message.includes('unauthorized')) {
      return 'high';
    }
    
    if (message.includes('validation') || message.includes('invalid')) {
      return 'low';
    }
    
    return 'medium';
  }

  private determineCategory(error: Error): ErrorCategory {
    const message = error.message.toLowerCase();
    
    if (message.includes('network') || message.includes('fetch') || message.includes('timeout')) {
      return 'network';
    }
    
    if (message.includes('authentication') || message.includes('unauthorized') || message.includes('token')) {
      return 'authentication';
    }
    
    if (message.includes('validation') || message.includes('invalid') || message.includes('required')) {
      return 'validation';
    }
    
    return 'unknown';
  }

  private logError(errorInfo: ErrorInfo): void {
    // In a real implementation, this would send to logging service
    console.error('Error Boundary Caught:', {
      error: errorInfo.error.message,
      stack: errorInfo.error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: errorInfo.timestamp,
      severity: errorInfo.severity,
      category: errorInfo.category
    });
  }

  private async attemptRecovery(): Promise<boolean> {
    const { errorInfo } = this.state;
    const { onRecover, recoveryDelay = 1000 } = this.props;
    
    if (!errorInfo) return false;

    this.setState({ isRecovering: true });

    // Wait for recovery delay
    await new Promise(resolve => setTimeout(resolve, recoveryDelay));

    try {
      // Try custom recovery logic
      if (onRecover) {
        const recovered = onRecover(errorInfo);
        if (recovered) {
          this.resetError();
          return true;
        }
      }

      // Default recovery attempts
      const { recoveryAttempts = 3 } = this.props;
      if (this.state.recoveryAttempts < recoveryAttempts) {
        this.setState(prev => ({
          recoveryAttempts: prev.recoveryAttempts + 1,
          isRecovering: false
        }));
        
        // Try to reset and re-render
        this.resetError();
        return true;
      }

      return false;
    } catch (recoveryError) {
      console.error('Recovery attempt failed:', recoveryError);
      this.setState({ isRecovering: false });
      return false;
    }
  }

  private resetError(): void {
    this.setState({
      hasError: false,
      errorInfo: null,
      recoveryAttempts: 0,
      isRecovering: false
    });
  }

  render(): ReactNode {
    const { children, fallback: FallbackComponent } = this.props;
    const { hasError, errorInfo, isRecovering } = this.state;

    if (hasError && errorInfo) {
      if (FallbackComponent) {
        return (
          <FallbackComponent 
            error={errorInfo} 
            resetError={this.resetError.bind(this)} 
          />
        );
      }

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                Something went wrong
              </h3>
              
              <div className="mt-2 text-sm text-gray-500">
                <p>We&apos;re sorry, but an unexpected error occurred.</p>
                {errorInfo.severity === 'critical' && (
                  <p className="mt-1 text-red-600 font-medium">This is a critical error requiring immediate attention.</p>
                )}
              </div>

              {this.props.logErrors && (
                <details className="mt-4 text-left bg-gray-50 p-3 rounded text-xs text-gray-600">
                  <summary className="cursor-pointer font-medium">Error details</summary>
                  <div className="mt-2 font-mono whitespace-pre-wrap">
                    {errorInfo.error.message}
                    {errorInfo.componentStack && (
                      <div className="mt-2 text-gray-500">
                        Component Stack:
                        {errorInfo.componentStack}
                      </div>
                    )}
                  </div>
                </details>
              )}

              <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.resetError.bind(this)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Try Again
                </button>
                
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Refresh Page
                </button>
              </div>

              {isRecovering && (
                <div className="mt-4 flex items-center justify-center text-sm text-blue-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  Attempting recovery...
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    return children;
  }
}

// Global error boundary provider
export class GlobalErrorBoundary extends Component<{ children: ReactNode }> {
  render(): ReactNode {
    return (
      <ErrorBoundary
        logErrors={true}
        recoveryAttempts={2}
        onError={(errorInfo) => {
          // Send to error reporting service
          console.error('Global error caught:', errorInfo);
        }}
        onRecover={(errorInfo) => {
          // Custom recovery logic
          console.log('Attempting recovery for:', errorInfo.error.message);
          return true;
        }}
      >
        {this.props.children}
      </ErrorBoundary>
    );
  }
}

// Hook for manual error boundary triggering
export const useErrorBoundary = () => {
  const [error, setError] = React.useState<Error | null>(null);

  const triggerError = (error: Error) => {
    setError(error);
  };

  const resetError = () => {
    setError(null);
  };

  // Throw error to trigger boundary
  if (error) {
    throw error;
  }

  return { triggerError, resetError };
};

// Higher-order component for wrapping components with error boundaries
export const withErrorBoundary = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorBoundaryProps?: Partial<ErrorBoundaryProps>
) => {
  const ComponentWithErrorBoundary: React.FC<P> = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  ComponentWithErrorBoundary.displayName = `WithErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;
  
  return ComponentWithErrorBoundary;
};

export default ErrorBoundary;