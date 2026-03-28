'use client';

import { useState } from 'react';
import ErrorBoundary, { useErrorBoundary, withErrorBoundary } from './ErrorBoundary';

// Example component that throws errors
const BuggyComponent = () => {
  const [count, setCount] = useState(0);
  
  if (count > 3) {
    throw new Error('Intentional error after 3 clicks!');
  }
  
  return (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Buggy Component</h3>
      <p className="text-gray-600 mb-4">This component will throw an error after 3 clicks</p>
      <button
        onClick={() => setCount(count + 1)}
        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
      >
        Click me! ({count}/3)
      </button>
      {count > 0 && (
        <p className="mt-2 text-sm text-gray-500">
          Count: {count} - {count >= 3 ? 'Will error on next click!' : 'Safe to click'}
        </p>
      )}
    </div>
  );
};

// Component with manual error triggering
const ManualErrorComponent = () => {
  const { triggerError, resetError } = useErrorBoundary();
  const [shouldError, setShouldError] = useState(false);

  const handleError = () => {
    triggerError(new Error('Manually triggered error!'));
  };

  if (shouldError) {
    throw new Error('Conditionally thrown error!');
  }

  return (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Manual Error Trigger</h3>
      <div className="space-y-3">
        <button
          onClick={handleError}
          className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
        >
          Trigger Error via Hook
        </button>
        
        <button
          onClick={() => setShouldError(true)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Trigger Conditional Error
        </button>
        
        <button
          onClick={resetError}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Reset Error State
        </button>
      </div>
    </div>
  );
};

// Network error simulator
const NetworkErrorComponent = () => {
  const [simulateError, setSimulateError] = useState(false);

  if (simulateError) {
    throw new Error('Network request failed: Failed to fetch');
  }

  return (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Network Error Simulator</h3>
      <p className="text-gray-600 mb-4">Simulates network-related errors</p>
      <button
        onClick={() => setSimulateError(true)}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Simulate Network Error
      </button>
    </div>
  );
};

// Authentication error simulator
const AuthErrorComponent = () => {
  const [simulateError, setSimulateError] = useState(false);

  if (simulateError) {
    throw new Error('Authentication failed: Invalid token provided');
  }

  return (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Auth Error Simulator</h3>
      <p className="text-gray-600 mb-4">Simulates authentication-related errors</p>
      <button
        onClick={() => setSimulateError(true)}
        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
      >
        Simulate Auth Error
      </button>
    </div>
  );
};

// Wrapped component example
const WrappedComponent = withErrorBoundary(
  () => (
    <div className="bg-white p-6 rounded-lg border">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Wrapped Component</h3>
      <p className="text-gray-600">This component is wrapped with an error boundary HOC</p>
      <button
        onClick={() => { throw new Error('Error from wrapped component!'); }}
        className="mt-4 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
      >
        Throw Error
      </button>
    </div>
  ),
  {
    recoveryAttempts: 1,
    logErrors: true
  }
);

export default function ErrorBoundaryDemo() {
  const [activeTab, setActiveTab] = useState<'examples' | 'configuration'>('examples');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h1 className="text-2xl font-bold text-gray-900">Error Boundary System</h1>
        <p className="text-gray-600 mt-1">
          Comprehensive error handling with automatic recovery and detailed logging
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            <button
              onClick={() => setActiveTab('examples')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'examples'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Error Examples
            </button>
            <button
              onClick={() => setActiveTab('configuration')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'configuration'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Configuration
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'examples' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Buggy Component with Error Boundary */}
                <ErrorBoundary
                  recoveryAttempts={2}
                  logErrors={true}
                  onError={(errorInfo) => {
                    console.log('Buggy component error:', errorInfo);
                  }}
                >
                  <BuggyComponent />
                </ErrorBoundary>

                {/* Manual Error Component */}
                <ErrorBoundary>
                  <ManualErrorComponent />
                </ErrorBoundary>

                {/* Network Error Component */}
                <ErrorBoundary
                  recoveryAttempts={3}
                  onRecover={(errorInfo) => {
                    console.log('Attempting network error recovery:', errorInfo.error.message);
                    return Math.random() > 0.5; // 50% chance of recovery
                  }}
                >
                  <NetworkErrorComponent />
                </ErrorBoundary>

                {/* Auth Error Component */}
                <ErrorBoundary
                  recoveryAttempts={1}
                  onError={(errorInfo) => {
                    console.log('Auth error detected:', errorInfo);
                    // Could redirect to login page here
                  }}
                >
                  <AuthErrorComponent />
                </ErrorBoundary>
              </div>

              {/* Wrapped Component Example */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Higher-Order Component Example</h2>
                <WrappedComponent />
              </div>

              {/* Global Error Boundary Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-800 mb-2">Global Error Boundary</h3>
                <p className="text-blue-700 text-sm">
                  The entire application is wrapped in a global error boundary that catches unhandled errors 
                  and provides a consistent recovery experience. All errors are logged and categorized 
                  automatically based on their content and severity.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'configuration' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Error Categories */}
                <div className="bg-white p-6 rounded-lg border">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Error Categories</h3>
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                      <span><strong>Network:</strong> Fetch failures, timeouts, connection issues</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-orange-500 rounded-full mr-3"></div>
                      <span><strong>Authentication:</strong> Token errors, unauthorized access</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
                      <span><strong>Validation:</strong> Form errors, invalid input</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-gray-500 rounded-full mr-3"></div>
                      <span><strong>Runtime:</strong> JavaScript errors, component crashes</span>
                    </div>
                  </div>
                </div>

                {/* Severity Levels */}
                <div className="bg-white p-6 rounded-lg border">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Severity Levels</h3>
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                      <span><strong>Critical:</strong> System-wide failures requiring immediate attention</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-orange-500 rounded-full mr-3"></div>
                      <span><strong>High:</strong> Major functionality impacted</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full mr-3"></div>
                      <span><strong>Medium:</strong> Partial functionality affected</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                      <span><strong>Low:</strong> Minor issues,不影响核心功能</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recovery Options */}
              <div className="bg-white p-6 rounded-lg border">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recovery Mechanisms</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </div>
                    <h4 className="font-medium text-gray-900">Automatic Retry</h4>
                    <p className="text-sm text-gray-600 mt-1">Configurable retry attempts with exponential backoff</p>
                  </div>
                  
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </div>
                    <h4 className="font-medium text-gray-900">State Reset</h4>
                    <p className="text-sm text-gray-600 mt-1">Reset component state to recover from errors</p>
                  </div>
                  
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    </div>
                    <h4 className="font-medium text-gray-900">Custom Recovery</h4>
                    <p className="text-sm text-gray-600 mt-1">Plug in custom recovery logic for specific error types</p>
                  </div>
                </div>
              </div>

              {/* Implementation Example */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 mb-2">Implementation Example</h3>
                <pre className="text-sm text-gray-700 overflow-x-auto">
                  <code>{`// Wrap your app with GlobalErrorBoundary
function App() {
  return (
    <GlobalErrorBoundary>
      <YourAppComponent />
    </GlobalErrorBoundary>
  );
}

// Or use specific boundaries for components
<ErrorBoundary
  recoveryAttempts={3}
  logErrors={true}
  onError={(errorInfo) => logToService(errorInfo)}
  onRecover={(errorInfo) => attemptRecovery(errorInfo)}
>
  <MyComponent />
</ErrorBoundary>`}</code>
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}