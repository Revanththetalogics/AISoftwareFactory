// Progressive loading states and offline capabilities service
// Manages loading states, offline detection, and progressive enhancement

// @ts-ignore - These will be imported in component files
import { useState, useEffect } from 'react';

export type LoadingState = 'idle' | 'loading' | 'loaded' | 'error' | 'retrying';
export type NetworkStatus = 'online' | 'offline' | 'reconnecting';

export interface LoadingConfig {
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  showSkeleton?: boolean;
  showProgress?: boolean;
  offlineFallback?: boolean;
}

export interface OfflineData {
  key: string;
  data: any;
  timestamp: string;
  expiresAt?: string;
}

export interface NetworkEvent {
  type: 'online' | 'offline' | 'reconnecting' | 'reconnected';
  timestamp: string;
  details?: Record<string, unknown>;
}

class LoadingStateService {
  private loadingStates: Map<string, LoadingState> = new Map();
  private networkStatus: NetworkStatus = 'online';
  private offlineStorage: Map<string, OfflineData> = new Map();
  private networkListeners: Set<(status: NetworkStatus) => void> = new Set();
  private loadingListeners: Map<string, Set<(state: LoadingState) => void>> = new Map();
  private networkEvents: NetworkEvent[] = [];
  private maxOfflineItems: number = 100;

  constructor() {
    this.initializeNetworkDetection();
    this.loadOfflineData();
  }

  // Initialize network detection
  private initializeNetworkDetection(): void {
    if (typeof window !== 'undefined') {
      // Check initial network status
      this.networkStatus = navigator.onLine ? 'online' : 'offline';
      
      // Listen for network changes
      window.addEventListener('online', this.handleOnline.bind(this));
      window.addEventListener('offline', this.handleOffline.bind(this));
    }
  }

  // Handle online event
  private handleOnline(): void {
    this.networkStatus = 'online';
    this.addNetworkEvent('online');
    this.notifyNetworkListeners();
    this.attemptReconnection();
  }

  // Handle offline event
  private handleOffline(): void {
    this.networkStatus = 'offline';
    this.addNetworkEvent('offline');
    this.notifyNetworkListeners();
  }

  // Attempt reconnection when coming back online
  private async attemptReconnection(): Promise<void> {
    this.networkStatus = 'reconnecting';
    this.addNetworkEvent('reconnecting');
    this.notifyNetworkListeners();

    // Simulate reconnection process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    this.networkStatus = 'online';
    this.addNetworkEvent('reconnected');
    this.notifyNetworkListeners();
    
    // Sync offline data
    await this.syncOfflineData();
  }

  // Set loading state for a component/action
  public setLoadingState(key: string, state: LoadingState): void {
    this.loadingStates.set(key, state);
    this.notifyLoadingListeners(key, state);
  }

  // Get current loading state
  public getLoadingState(key: string): LoadingState {
    return this.loadingStates.get(key) || 'idle';
  }

  // Create progressive loading controller
  public createLoadingController(key: string, config: LoadingConfig = {}) {
    const defaultConfig: LoadingConfig = {
      timeout: 10000,
      retryAttempts: 3,
      retryDelay: 1000,
      showSkeleton: true,
      showProgress: true,
      offlineFallback: true,
      ...config
    };

    return {
      start: () => this.setLoadingState(key, 'loading'),
      complete: () => this.setLoadingState(key, 'loaded'),
      error: () => this.setLoadingState(key, 'error'),
      retry: () => this.setLoadingState(key, 'retrying'),
      getState: () => this.getLoadingState(key),
      getConfig: () => defaultConfig
    };
  }

  // Subscribe to loading state changes
  public subscribeToLoading(key: string, callback: (state: LoadingState) => void): () => void {
    if (!this.loadingListeners.has(key)) {
      this.loadingListeners.set(key, new Set());
    }
    
    const listeners = this.loadingListeners.get(key)!;
    listeners.add(callback);
    
    return () => {
      listeners.delete(callback);
      if (listeners.size === 0) {
        this.loadingListeners.delete(key);
      }
    };
  }

  // Subscribe to network status changes
  public subscribeToNetwork(callback: (status: NetworkStatus) => void): () => void {
    this.networkListeners.add(callback);
    return () => {
      this.networkListeners.delete(callback);
    };
  }

  // Store data for offline use
  public storeOfflineData(key: string, data: any, ttlMinutes?: number): void {
    const timestamp = new Date().toISOString();
    const expiresAt = ttlMinutes 
      ? new Date(Date.now() + ttlMinutes * 60000).toISOString()
      : undefined;

    const offlineData: OfflineData = {
      key,
      data,
      timestamp,
      expiresAt
    };

    this.offlineStorage.set(key, offlineData);
    this.persistOfflineData();
    
    // Clean up old items if we exceed the limit
    if (this.offlineStorage.size > this.maxOfflineItems) {
      this.cleanupOldOfflineData();
    }
  }

  // Retrieve offline data
  public getOfflineData(key: string): any {
    const data = this.offlineStorage.get(key);
    
    if (!data) return null;
    
    // Check if data has expired
    if (data.expiresAt && new Date(data.expiresAt) < new Date()) {
      this.offlineStorage.delete(key);
      this.persistOfflineData();
      return null;
    }
    
    return data.data;
  }

  // Check if data is available offline
  public isAvailableOffline(key: string): boolean {
    return this.offlineStorage.has(key);
  }

  // Execute operation with offline fallback
  public async executeWithOfflineFallback<T>(
    operation: () => Promise<T>,
    fallbackOperation: () => Promise<T>,
    cacheKey?: string
  ): Promise<T> {
    try {
      // Try primary operation
      const result = await operation();
      
      // Cache successful result if cache key provided
      if (cacheKey) {
        this.storeOfflineData(cacheKey, result, 60); // Cache for 1 hour
      }
      
      return result;
    } catch (error) {
      console.warn('Primary operation failed, attempting offline fallback:', error);
      
      // If we're offline and have cached data, use it
      if (this.networkStatus === 'offline' && cacheKey) {
        const cachedData = this.getOfflineData(cacheKey);
        if (cachedData !== null) {
          return cachedData;
        }
      }
      
      // Try fallback operation
      try {
        return await fallbackOperation();
      } catch (fallbackError) {
        console.error('Both primary and fallback operations failed:', fallbackError);
        throw fallbackError;
      }
    }
  }

  // Get network status
  public getNetworkStatus(): NetworkStatus {
    return this.networkStatus;
  }

  // Get recent network events
  public getNetworkEvents(limit: number = 10): NetworkEvent[] {
    return this.networkEvents.slice(-limit);
  }

  // Simulate network delay for testing
  public async simulateNetworkDelay(minMs: number = 1000, maxMs: number = 3000): Promise<void> {
    const delay = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  // Private helper methods
  private notifyLoadingListeners(key: string, state: LoadingState): void {
    const listeners = this.loadingListeners.get(key);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(state);
        } catch (error) {
          console.error('Error in loading state listener:', error);
        }
      });
    }
  }

  private notifyNetworkListeners(): void {
    this.networkListeners.forEach(callback => {
      try {
        callback(this.networkStatus);
      } catch (error) {
        console.error('Error in network status listener:', error);
      }
    });
  }

  private addNetworkEvent(type: NetworkEvent['type'], details?: Record<string, unknown>): void {
    const event: NetworkEvent = {
      type,
      timestamp: new Date().toISOString(),
      details
    };
    
    this.networkEvents.push(event);
    
    // Keep only last 50 events
    if (this.networkEvents.length > 50) {
      this.networkEvents = this.networkEvents.slice(-50);
    }
  }

  private async syncOfflineData(): Promise<void> {
    // In a real implementation, this would sync pending offline operations
    console.log('Syncing offline data...');
    
    // Example: sync any pending mutations
    for (const [key, data] of this.offlineStorage.entries()) {
      if (key.startsWith('pending_')) {
        try {
          // Attempt to sync the pending operation
          console.log(`Syncing pending operation: ${key}`);
          this.offlineStorage.delete(key);
        } catch (error) {
          console.error(`Failed to sync ${key}:`, error);
        }
      }
    }
    
    this.persistOfflineData();
  }

  private loadOfflineData(): void {
    if (typeof localStorage !== 'undefined') {
      try {
        const stored = localStorage.getItem('offline_data');
        if (stored) {
          const parsed = JSON.parse(stored);
          Object.entries(parsed).forEach(([key, data]) => {
            this.offlineStorage.set(key, data as OfflineData);
          });
        }
      } catch (error) {
        console.error('Failed to load offline data:', error);
      }
    }
  }

  private persistOfflineData(): void {
    if (typeof localStorage !== 'undefined') {
      try {
        const data = Object.fromEntries(this.offlineStorage);
        localStorage.setItem('offline_data', JSON.stringify(data));
      } catch (error) {
        console.error('Failed to persist offline data:', error);
      }
    }
  }

  private cleanupOldOfflineData(): void {
    const now = new Date();
    let deletedCount = 0;
    
    for (const [key, data] of this.offlineStorage.entries()) {
      // Delete expired items
      if (data.expiresAt && new Date(data.expiresAt) < now) {
        this.offlineStorage.delete(key);
        deletedCount++;
      }
    }
    
    // If still over limit, delete oldest items
    if (this.offlineStorage.size > this.maxOfflineItems) {
      const sortedEntries = Array.from(this.offlineStorage.entries())
        .sort(([, a], [, b]) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      
      const excess = this.offlineStorage.size - this.maxOfflineItems;
      for (let i = 0; i < excess; i++) {
        this.offlineStorage.delete(sortedEntries[i][0]);
        deletedCount++;
      }
    }
    
    if (deletedCount > 0) {
      this.persistOfflineData();
      console.log(`Cleaned up ${deletedCount} old offline items`);
    }
  }
}

// Singleton instance
export const loadingStateService = new LoadingStateService();

// Hook for React components
export const useLoadingState = (key: string) => {
  // @ts-ignore - These will be imported in the component file
  const [state, setState] = useState<LoadingState>('idle');
  
  useEffect(() => {
    const unsubscribe = loadingStateService.subscribeToLoading(key, setState);
    setState(loadingStateService.getLoadingState(key));
    return unsubscribe;
  }, [key]);
  
  return state;
};

// Hook for network status
export const useNetworkStatus = () => {
  // @ts-ignore - These will be imported in the component file
  const [status, setStatus] = useState<NetworkStatus>('online');
  
  useEffect(() => {
    const unsubscribe = loadingStateService.subscribeToNetwork(setStatus);
    setStatus(loadingStateService.getNetworkStatus());
    return unsubscribe;
  }, []);
  
  return status;
};