'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCcw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class GlobalErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console and any error reporting service
    console.error('Global Error Boundary caught an error:', error, errorInfo);
    
    // You can also log to external services here
    // errorReportingService.logError(error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      // If a custom fallback is provided, use it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-bg-base flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl border-border-critical bg-bg-critical-dim">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 rounded-full bg-state-error-dim flex items-center justify-center mb-4">
                <AlertTriangle className="w-8 h-8 text-state-error" />
              </div>
              <CardTitle className="text-2xl text-text-primary">
                Something went wrong
              </CardTitle>
            </CardHeader>
            
            <CardContent className="text-center space-y-4">
              <p className="text-text-secondary">
                We're sorry, but something unexpected happened. Our team has been notified.
              </p>
              
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="text-left bg-bg-overlay p-4 rounded-lg border border-border-default">
                  <h3 className="font-semibold text-text-primary mb-2">Error Details:</h3>
                  <pre className="text-sm text-text-secondary overflow-auto max-h-40">
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </div>
              )}
            </CardContent>
            
            <CardFooter className="flex justify-center gap-3">
              <Button 
                onClick={this.handleReset}
                className="bg-state-queued hover:bg-state-queued"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
              <Button 
                variant="outline"
                onClick={this.handleGoHome}
              >
                <Home className="w-4 h-4 mr-2" />
                Go Home
              </Button>
            </CardFooter>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook version for functional components
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = React.useCallback((error: Error) => {
    console.error('Caught error:', error);
    setError(error);
  }, []);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, resetError };
}

// Error boundary for specific components
export const ComponentErrorBoundary: React.FC<{
  children: ReactNode;
  componentName: string;
  onReset?: () => void;
}> = ({ children, componentName, onReset }) => {
  const { error, handleError, resetError } = useErrorHandler();

  // Wrap children in error boundary
  React.useEffect(() => {
    if (error) {
      console.error(`Error in ${componentName}:`, error);
    }
  }, [error, componentName]);

  const handleLocalReset = () => {
    resetError();
    onReset?.();
  };

  if (error) {
    return (
      <div className="p-4 border border-border-critical rounded-lg bg-bg-critical-dim">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-state-error mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="font-medium text-text-primary">Component Error</h3>
            <p className="text-sm text-text-secondary mt-1">
              An error occurred in {componentName}. {error.message}
            </p>
            <div className="flex gap-2 mt-3">
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleLocalReset}
              >
                Retry
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundaryWrapper onError={handleError}>
      {children}
    </ErrorBoundaryWrapper>
  );
};

// Wrapper component that catches errors from children
const ErrorBoundaryWrapper: React.FC<{
  children: ReactNode;
  onError: (error: Error) => void;
}> = ({ children, onError }) => {
  React.useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      onError(event.error);
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      onError(event.reason instanceof Error ? event.reason : new Error(String(event.reason)));
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [onError]);

  return <>{children}</>;
};