/**
 * Error Handler Service
 * 
 * Centralized error handling with retry mechanisms, fallback strategies,
 * and user-friendly error messages for missing backend services.
 */

import { toast } from 'sonner';

// Error types
export enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND_ERROR = 'NOT_FOUND_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

// Error severity levels
export enum ErrorSeverity {
  LOW = 'LOW',      // Can retry silently
  MEDIUM = 'MEDIUM', // Show warning to user
  HIGH = 'HIGH',    // Show error dialog
  CRITICAL = 'CRITICAL' // App-wide failure
}

export interface ErrorHandlerOptions {
  showToast?: boolean;
  retryAttempts?: number;
  retryDelay?: number;
  fallbackData?: any;
  onRetry?: () => void;
  onError?: (error: ServiceError) => void;
}

export interface ServiceError {
  type: ErrorType;
  severity: ErrorSeverity;
  message: string;
  originalError?: any;
  timestamp: Date;
  serviceName?: string;
  action?: string;
  canRetry: boolean;
  userMessage: string;
}

export class ErrorHandlerService {
  private static instance: ErrorHandlerService;
  private globalErrorHandler?: (error: ServiceError) => void;

  private constructor() {}

  static getInstance(): ErrorHandlerService {
    if (!ErrorHandlerService.instance) {
      ErrorHandlerService.instance = new ErrorHandlerService();
    }
    return ErrorHandlerService.instance;
  }

  /**
   * Set global error handler for application-wide error tracking
   */
  setGlobalErrorHandler(handler: (error: ServiceError) => void) {
    this.globalErrorHandler = handler;
  }

  /**
   * Classify error based on error object or status code
   */
  classifyError(error: any, statusCode?: number): ServiceError {
    let type: ErrorType;
    let severity: ErrorSeverity;
    let userMessage: string;
    let canRetry = false;

    // Network connectivity issues
    if (error instanceof TypeError && error.message.includes('fetch')) {
      type = ErrorType.NETWORK_ERROR;
      severity = ErrorSeverity.HIGH;
      userMessage = 'Unable to connect to the server. Please check your internet connection.';
      canRetry = true;
    }
    // Timeout errors
    else if (error.name === 'AbortError' || error.code === 'TIMEOUT') {
      type = ErrorType.TIMEOUT_ERROR;
      severity = ErrorSeverity.MEDIUM;
      userMessage = 'Request timed out. Please try again.';
      canRetry = true;
    }
    // Authentication errors
    else if (statusCode === 401 || statusCode === 403) {
      type = ErrorType.AUTH_ERROR;
      severity = ErrorSeverity.HIGH;
      userMessage = 'Authentication failed. Please log in again.';
      canRetry = false;
    }
    // Validation errors
    else if (statusCode === 400 || statusCode === 422) {
      type = ErrorType.VALIDATION_ERROR;
      severity = ErrorSeverity.LOW;
      userMessage = 'Invalid input data. Please check your request.';
      canRetry = false;
    }
    // Not found errors
    else if (statusCode === 404) {
      type = ErrorType.NOT_FOUND_ERROR;
      severity = ErrorSeverity.LOW;
      userMessage = 'Requested resource not found.';
      canRetry = false;
    }
    // Server errors
    else if (statusCode && statusCode >= 500) {
      type = ErrorType.SERVER_ERROR;
      severity = ErrorSeverity.HIGH;
      userMessage = 'Server error occurred. Our team has been notified.';
      canRetry = true;
    }
    // Service unavailable
    else if (statusCode === 503) {
      type = ErrorType.SERVICE_UNAVAILABLE;
      severity = ErrorSeverity.CRITICAL;
      userMessage = 'Service temporarily unavailable. Please try again later.';
      canRetry = true;
    }
    // Unknown errors
    else {
      type = ErrorType.UNKNOWN_ERROR;
      severity = ErrorSeverity.MEDIUM;
      userMessage = error.message || 'An unexpected error occurred.';
      canRetry = true;
    }

    const serviceError: ServiceError = {
      type,
      severity,
      message: error.message || 'Unknown error',
      originalError: error,
      timestamp: new Date(),
      canRetry,
      userMessage
    };

    return serviceError;
  }

  /**
   * Handle error with retry logic and user feedback
   */
  async handleError(
    error: any,
    options: ErrorHandlerOptions = {},
    serviceName?: string,
    action?: string
  ): Promise<ServiceError> {
    const {
      showToast = true,
      retryAttempts = 3,
      retryDelay = 1000,
      fallbackData = null,
      onRetry,
      onError
    } = options;

    const classifiedError = this.classifyError(error, error?.status);
    classifiedError.serviceName = serviceName;
    classifiedError.action = action;

    // Log error
    console.error('Service Error:', {
      service: serviceName,
      action,
      error: classifiedError,
      timestamp: classifiedError.timestamp
    });

    // Trigger global error handler
    if (this.globalErrorHandler) {
      this.globalErrorHandler(classifiedError);
    }

    // Trigger local error callback
    if (onError) {
      onError(classifiedError);
    }

    // Show user feedback based on severity
    if (showToast) {
      this.showUserFeedback(classifiedError);
    }

    // Handle retries for retryable errors
    if (classifiedError.canRetry && retryAttempts > 0) {
      try {
        await this.delay(retryDelay);
        if (onRetry) onRetry();
        // Return fallback data if provided, otherwise rethrow
        return fallbackData ? classifiedError : Promise.reject(classifiedError);
      } catch (retryError) {
        // If retry fails, return the original error with fallback data
        if (fallbackData) {
          return classifiedError;
        }
        throw classifiedError;
      }
    }

    // Return fallback data if available
    if (fallbackData) {
      return classifiedError;
    }

    // Throw the error for upstream handling
    throw classifiedError;
  }

  /**
   * Show appropriate user feedback based on error severity
   */
  private showUserFeedback(error: ServiceError) {
    switch (error.severity) {
      case ErrorSeverity.LOW:
        // Silent handling or subtle notification
        break;
      case ErrorSeverity.MEDIUM:
        toast.warning(error.userMessage);
        break;
      case ErrorSeverity.HIGH:
        toast.error(error.userMessage);
        break;
      case ErrorSeverity.CRITICAL:
        toast.error(error.userMessage, {
          duration: 10000,
          action: {
            label: 'Retry',
            onClick: () => window.location.reload()
          }
        });
        break;
    }
  }

  /**
   * Utility delay function
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Create a wrapped service method with automatic error handling
   */
  wrapServiceMethod<T>(
    method: () => Promise<T>,
    serviceName: string,
    action: string,
    options: ErrorHandlerOptions = {}
  ): Promise<T> {
    return method().catch(error => {
      return this.handleError(error, options, serviceName, action).then(() => {
        // If handleError resolves (fallback case), return fallback data
        if (options.fallbackData !== undefined) {
          return options.fallbackData as T;
        }
        throw error;
      });
    }) as Promise<T>;
  }

  /**
   * Check if backend service is available
   */
  async checkServiceHealth(serviceName: string, endpoint: string): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(endpoint, { 
        method: 'GET', 
        signal: controller.signal 
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      const serviceError = this.classifyError(error);
      console.warn(`Service health check failed for ${serviceName}:`, serviceError.message);
      return false;
    }
  }

  /**
   * Get user-friendly error message for display
   */
  getUserMessage(error: ServiceError): string {
    return error.userMessage;
  }

  /**
   * Get technical error details for debugging
   */
  getTechnicalDetails(error: ServiceError): string {
    return `
      Service: ${error.serviceName || 'Unknown'}
      Action: ${error.action || 'Unknown'}
      Error Type: ${error.type}
      Message: ${error.message}
      Timestamp: ${error.timestamp.toISOString()}
      Original Error: ${error.originalError?.stack || error.originalError?.message || 'N/A'}
    `.trim();
  }
}

// Export singleton instance
export const errorHandler = ErrorHandlerService.getInstance();

// Types are already exported in the interface declaration above