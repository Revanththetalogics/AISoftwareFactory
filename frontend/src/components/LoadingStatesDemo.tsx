'use client';

import { useState, useEffect } from 'react';
import { 
  loadingStateService, 
  LoadingState, 
  NetworkStatus,
  useLoadingState,
  useNetworkStatus
} from '@/services/loading-state.service';

export default function LoadingStatesDemo() {
  const [demoData, setDemoData] = useState<{ items: any[]; timestamp: string } | null>(null);
  const [showSkeleton, setShowSkeleton] = useState(true);
  const [progressValue, setProgressValue] = useState(0);
  const [retryCount, setRetryCount] = useState(0);

  // Use the loading state hooks
  const listLoadingState = useLoadingState('list-data');
  const detailLoadingState = useLoadingState('detail-data');
  const networkStatus = useNetworkStatus();

  useEffect(() => {
    // Simulate initial data loading
    loadData();
    
    // Set up progress simulation
    const progressInterval = setInterval(() => {
      setProgressValue(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    return () => clearInterval(progressInterval);
  }, []);

  const loadData = async () => {
    const controller = loadingStateService.createLoadingController('list-data', {
      timeout: 8000,
      retryAttempts: 2,
      showSkeleton: true
    });

    controller.start();

    try {
      // Simulate API call with network delay
      await loadingStateService.simulateNetworkDelay(1000, 3000);
      
      // Simulate potential network failure
      if (Math.random() > 0.7 && networkStatus === 'offline') {
        throw new Error('Network error');
      }

      const data = {
        items: Array.from({ length: 10 }, (_, i) => ({
          id: i + 1,
          name: `Item ${i + 1}`,
          description: `Description for item ${i + 1}`,
          status: ['active', 'pending', 'completed'][Math.floor(Math.random() * 3)]
        })),
        timestamp: new Date().toISOString()
      };

      setDemoData(data);
      controller.complete();
      
      // Store for offline use
      loadingStateService.storeOfflineData('list-data-cache', data, 30);
      
    } catch (error) {
      console.error('Failed to load data:', error);
      controller.error();
      
      // Try offline fallback
      const offlineData = loadingStateService.getOfflineData('list-data-cache');
      if (offlineData) {
        setDemoData(offlineData);
        console.log('Showing cached data due to network error');
      }
    }
  };

  const loadDetailData = async () => {
    const controller = loadingStateService.createLoadingController('detail-data');
    controller.start();

    try {
      await loadingStateService.simulateNetworkDelay(500, 1500);
      
      const detailData = {
        id: 1,
        title: 'Detailed Item Information',
        content: 'This is detailed content that takes longer to load...',
        metadata: {
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          views: Math.floor(Math.random() * 1000)
        }
      };

      controller.complete();
      console.log('Detail data loaded:', detailData);
      
    } catch (error) {
      controller.error();
      console.error('Failed to load detail data:', error);
    }
  };

  const retryLoad = () => {
    setRetryCount(prev => prev + 1);
    loadData();
  };

  const toggleNetworkStatus = () => {
    // Simulate network toggle for demo purposes
    const event = new Event(loadingStateService.getNetworkStatus() === 'online' ? 'offline' : 'online');
    window.dispatchEvent(event);
  };

  const LoadingSkeleton = () => (
    <div className="animate-pulse space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
          <div className="rounded-full bg-gray-200 h-12 w-12"></div>
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      ))}
    </div>
  );

  const ProgressBar = ({ value }: { value: number }) => (
    <div className="w-full bg-gray-200 rounded-full h-2.5">
      <div 
        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
        style={{ width: `${Math.min(value, 100)}%` }}
      ></div>
    </div>
  );

  const NetworkStatusIndicator = () => {
    const getStatusColor = () => {
      switch (networkStatus) {
        case 'online': return 'bg-green-500';
        case 'offline': return 'bg-red-500';
        case 'reconnecting': return 'bg-yellow-500';
        default: return 'bg-gray-500';
      }
    };

    const getStatusText = () => {
      switch (networkStatus) {
        case 'online': return 'Online';
        case 'offline': return 'Offline';
        case 'reconnecting': return 'Reconnecting...';
        default: return 'Unknown';
      }
    };

    return (
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${networkStatus === 'reconnecting' ? 'animate-pulse' : ''}`}></div>
        <span className="text-sm font-medium">{getStatusText()}</span>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header with Network Status */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Progressive Loading States</h1>
            <p className="text-gray-600 mt-1">Demonstration of advanced loading states and offline capabilities</p>
          </div>
          <div className="flex items-center space-x-4">
            <NetworkStatusIndicator />
            <button
              onClick={toggleNetworkStatus}
              className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Toggle Network
            </button>
          </div>
        </div>
      </div>

      {/* Loading State Demo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* List Loading Demo */}
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">List Data Loading</h2>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 text-xs rounded-full ${
                listLoadingState === 'loading' ? 'bg-blue-100 text-blue-800' :
                listLoadingState === 'loaded' ? 'bg-green-100 text-green-800' :
                listLoadingState === 'error' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {listLoadingState}
              </span>
              <button
                onClick={loadData}
                disabled={listLoadingState === 'loading'}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Reload
              </button>
            </div>
          </div>

          {listLoadingState === 'loading' && showSkeleton && (
            <div className="space-y-4">
              <LoadingSkeleton />
              <div className="pt-4">
                <ProgressBar value={progressValue} />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Loading data...</span>
                  <span>{Math.round(progressValue)}%</span>
                </div>
              </div>
            </div>
          )}

          {listLoadingState === 'error' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="font-medium text-red-800">Failed to load data</h3>
                  <p className="text-sm text-red-700 mt-1">
                    {networkStatus === 'offline' 
                      ? 'You are currently offline. Showing cached data if available.'
                      : 'Unable to connect to the server. Please try again.'}
                  </p>
                </div>
              </div>
              <button
                onClick={retryLoad}
                className="mt-3 px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700"
              >
                Retry ({retryCount})
              </button>
            </div>
          )}

          {listLoadingState === 'loaded' && demoData && (
            <div className="space-y-3">
              {demoData.items.map((item: { id: string; name: string; description: string; status: string }) => (
                <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium text-gray-900">{item.name}</h3>
                    <p className="text-sm text-gray-600">{item.description}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    item.status === 'active' ? 'bg-green-100 text-green-800' :
                    item.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {item.status}
                  </span>
                </div>
              ))}
              <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
                Last updated: {new Date(demoData.timestamp).toLocaleTimeString()}
                {loadingStateService.isAvailableOffline('list-data-cache') && (
                  <span className="ml-2 text-green-600">_cached</span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Detail Loading Demo */}
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Detail Data Loading</h2>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 text-xs rounded-full ${
                detailLoadingState === 'loading' ? 'bg-blue-100 text-blue-800' :
                detailLoadingState === 'loaded' ? 'bg-green-100 text-green-800' :
                detailLoadingState === 'error' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {detailLoadingState}
              </span>
              <button
                onClick={loadDetailData}
                disabled={detailLoadingState === 'loading'}
                className="px-3 py-1 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                Load Details
              </button>
            </div>
          </div>

          {detailLoadingState === 'loading' && (
            <div className="animate-pulse space-y-3">
              <div className="h-6 bg-gray-200 rounded w-2/3"></div>
              <div className="h-4 bg-gray-200 rounded w-full"></div>
              <div className="h-4 bg-gray-200 rounded w-4/5"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
          )}

          {detailLoadingState === 'loaded' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-medium text-green-800">Detail data loaded successfully!</h3>
              <p className="text-sm text-green-700 mt-1">
                This demonstrates successful loading of secondary content with proper state management.
              </p>
            </div>
          )}

          {detailLoadingState === 'error' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="font-medium text-red-800">Failed to load details</h3>
              <p className="text-sm text-red-700 mt-1">
                The detail request failed. This could be due to network issues or server problems.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Loading Configuration</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={showSkeleton}
                onChange={(e) => setShowSkeleton(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-gray-700">Show skeleton loading states</span>
            </label>
            <p className="text-sm text-gray-500 mt-1">
              Display animated skeleton screens during loading
            </p>
          </div>

          <div>
            <button
              onClick={() => {
                loadingStateService.storeOfflineData('demo-test', { test: 'data' }, 5);
                alert('Stored test data for offline use (5 minute TTL)');
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Store Offline Test Data
            </button>
            <p className="text-sm text-gray-500 mt-1">
              Manually store data that will be available when offline
            </p>
          </div>
        </div>
      </div>

      {/* Network Events Log */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Network Events</h2>
        <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm">
          {loadingStateService.getNetworkEvents().slice(-5).reverse().map((event, index) => (
            <div key={index} className="mb-2 last:mb-0">
              <span className="text-gray-500">[{new Date(event.timestamp).toLocaleTimeString()}]</span>
              <span className="ml-2 font-medium capitalize">{event.type}</span>
              {event.details && (
                <span className="ml-2 text-gray-600">
                  {JSON.stringify(event.details)}
                </span>
              )}
            </div>
          ))}
          {loadingStateService.getNetworkEvents().length === 0 && (
            <div className="text-gray-500 italic">No network events recorded</div>
          )}
        </div>
      </div>
    </div>
  );
}