'use client';

import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

// Network status types
type NetworkStatus = 'online' | 'offline' | 'checking' | 'reconnecting';

// Service status types
interface ServiceStatus {
  name: string;
  status: 'online' | 'offline' | 'degraded';
  responseTime?: number;
  lastChecked: Date;
  error?: string;
}

// Network monitoring hook
export function useNetworkStatus() {
  const [status, setStatus] = useState<NetworkStatus>('checking');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastCheck, setLastCheck] = useState<Date>(new Date());

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setStatus('online');
      setLastCheck(new Date());
    };

    const handleOffline = () => {
      setIsOnline(false);
      setStatus('offline');
      setLastCheck(new Date());
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial check
    setIsOnline(navigator.onLine);
    setStatus(navigator.onLine ? 'online' : 'offline');

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const reconnect = () => {
    setStatus('reconnecting');
    // Force a network check
    fetch('/api/health')
      .then(() => {
        setStatus('online');
        setIsOnline(true);
      })
      .catch(() => {
        setStatus('offline');
        setIsOnline(false);
      })
      .finally(() => {
        setLastCheck(new Date());
      });
  };

  return {
    status,
    isOnline,
    lastCheck,
    reconnect
  };
}

// Service monitoring hook
export function useServiceMonitor(services: string[]) {
  const [serviceStatuses, setServiceStatuses] = useState<Record<string, ServiceStatus>>({});
  const [isMonitoring, setIsMonitoring] = useState(false);

  useEffect(() => {
    // Initialize service statuses
    const initialStatuses: Record<string, ServiceStatus> = {};
    services.forEach(service => {
      initialStatuses[service] = {
        name: service,
        status: 'offline',
        lastChecked: new Date()
      };
    });
    setServiceStatuses(initialStatuses);
  }, [services]);

  const checkService = async (serviceName: string, endpoint: string): Promise<ServiceStatus> => {
    const startTime = Date.now();
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(endpoint, { 
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      const responseTime = Date.now() - startTime;
      
      return {
        name: serviceName,
        status: response.ok ? 'online' : 'degraded',
        responseTime,
        lastChecked: new Date(),
        error: response.ok ? undefined : `HTTP ${response.status}`
      };
    } catch (error) {
      return {
        name: serviceName,
        status: 'offline',
        lastChecked: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  };

  const startMonitoring = () => {
    setIsMonitoring(true);
    
    const monitorServices = async () => {
      const promises = services.map(async (service) => {
        // Map service names to endpoints
        const endpoints: Record<string, string> = {
          'api': '/api/v1/health',
          'database': '/api/v1/health/database',
          'redis': '/api/v1/health/redis',
          'git': '/api/v1/git/repositories',
          'knowledge': '/api/v1/knowledge/stats',
          'simulation': '/api/v1/simulations/stats'
        };
        
        const endpoint = endpoints[service] || `/api/v1/health/${service}`;
        return checkService(service, endpoint);
      });
      
      const results = await Promise.all(promises);
      
      const newStatuses: Record<string, ServiceStatus> = {};
      results.forEach(result => {
        newStatuses[result.name] = result;
      });
      
      setServiceStatuses(newStatuses);
    };
    
    // Check immediately
    monitorServices();
    
    // Set up periodic checking every 30 seconds
    const interval = setInterval(monitorServices, 30000);
    
    return () => {
      clearInterval(interval);
      setIsMonitoring(false);
    };
  };

  const stopMonitoring = () => {
    setIsMonitoring(false);
  };

  return {
    serviceStatuses,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    checkService
  };
}

// Disconnected UI Component
export const DisconnectedUI: React.FC<{
  onRetry?: () => void;
  showServices?: boolean;
  className?: string;
}> = ({ onRetry, showServices = true, className }) => {
  const { status, isOnline, reconnect } = useNetworkStatus();
  const services = ['api', 'database', 'redis', 'git', 'knowledge', 'simulation'];
  const { serviceStatuses, startMonitoring, stopMonitoring, isMonitoring } = useServiceMonitor(services);

  useEffect(() => {
    if (showServices) {
      const cleanup = startMonitoring();
      return cleanup;
    }
  }, [showServices, startMonitoring]);

  const getStatusColor = (status: 'online' | 'offline' | 'degraded') => {
    switch (status) {
      case 'online': return 'bg-state-success';
      case 'degraded': return 'bg-state-warning';
      case 'offline': return 'bg-state-error';
    }
  };

  const getStatusIcon = (status: 'online' | 'offline' | 'degraded') => {
    switch (status) {
      case 'online': return <CheckCircle className="w-4 h-4 text-white" />;
      case 'degraded': return <AlertTriangle className="w-4 h-4 text-white" />;
      case 'offline': return <WifiOff className="w-4 h-4 text-white" />;
    }
  };

  return (
    <div className={`min-h-screen bg-bg-base flex items-center justify-center p-4 ${className}`}>
      <Card className="w-full max-w-2xl border-border-warning bg-bg-warning-dim">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 rounded-full bg-state-warning-dim flex items-center justify-center mb-4">
            {isOnline ? (
              <Wifi className="w-8 h-8 text-state-warning" />
            ) : (
              <WifiOff className="w-8 h-8 text-state-error" />
            )}
          </div>
          <CardTitle className="text-2xl text-text-primary">
            {isOnline ? 'Limited Connectivity' : 'No Internet Connection'}
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <div className="text-center">
            <p className="text-text-secondary mb-4">
              {isOnline 
                ? 'Some services are temporarily unavailable.' 
                : 'Please check your internet connection and try again.'
              }
            </p>
            
            {!isOnline && (
              <Badge variant="destructive" className="mb-4">
                <WifiOff className="w-3 h-3 mr-1" />
                Offline
              </Badge>
            )}
          </div>

          {showServices && (
            <div className="space-y-3">
              <h3 className="font-medium text-text-primary">Service Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {services.map((service) => {
                  const serviceStatus = serviceStatuses[service];
                  return (
                    <div 
                      key={service}
                      className="flex items-center justify-between p-3 bg-bg-overlay rounded-lg border border-border-default"
                    >
                      <span className="text-text-secondary capitalize">{service}</span>
                      <div className="flex items-center gap-2">
                        {serviceStatus && (
                          <span className="text-xs text-text-tertiary">
                            {serviceStatus.responseTime ? `${serviceStatus.responseTime}ms` : ''}
                          </span>
                        )}
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(serviceStatus?.status || 'offline')} flex items-center justify-center`}>
                          {getStatusIcon(serviceStatus?.status || 'offline')}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {isMonitoring && (
            <div className="text-center text-sm text-text-tertiary">
              Monitoring services... Last checked: {new Date().toLocaleTimeString()}
            </div>
          )}
        </CardContent>
        
        <CardFooter className="flex justify-center gap-3">
          <Button 
            onClick={reconnect}
            className="bg-state-queued hover:bg-state-queued"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            {isOnline ? 'Retry Services' : 'Check Connection'}
          </Button>
          
          {onRetry && (
            <Button 
              variant="outline"
              onClick={onRetry}
            >
              Continue Offline
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
};

// Offline indicator component
export const OfflineIndicator: React.FC<{
  className?: string;
}> = ({ className }) => {
  const { isOnline } = useNetworkStatus();
  
  if (isOnline) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`fixed top-4 right-4 z-50 ${className}`}
    >
      <Badge variant="destructive" className="gap-2 px-3 py-2">
        <WifiOff className="w-4 h-4" />
        Offline
      </Badge>
    </motion.div>
  );
};

// Service status badge
export const ServiceStatusBadge: React.FC<{
  service: string;
  status: 'online' | 'offline' | 'degraded';
  responseTime?: number;
  className?: string;
}> = ({ service, status, responseTime, className }) => {
  const getStatusVariant = () => {
    switch (status) {
      case 'online': return 'default';
      case 'degraded': return 'secondary'; // Using secondary for degraded state
      case 'offline': return 'destructive';
    }
  };

  return (
    <Badge variant={getStatusVariant()} className={className}>
      <span className="capitalize">{service}</span>
      {responseTime && (
        <span className="ml-1 text-xs opacity-75">
          {responseTime}ms
        </span>
      )}
    </Badge>
  );
};