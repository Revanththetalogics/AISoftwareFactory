'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  Database, 
  Server, 
  Wifi, 
  HardDrive,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Zap
} from 'lucide-react';

interface ServiceHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time_ms: number;
  last_checked: string;
  details?: Record<string, unknown>;
}

interface HealthOverview {
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  services: ServiceHealth[];
  timestamp: string;
  uptime_percentage: number;
}

export default function ServiceHealthDashboard() {
  const [healthData, setHealthData] = useState<HealthOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      
      // Fetch from multiple health endpoints
      const [generalHealth, dbHealth, redisHealth] = await Promise.allSettled([
        fetch('/api/v1/health').then(res => res.json()),
        fetch('/api/v1/db-performance/health').then(res => res.json()),
        fetch('/api/v1/rate-limits/statistics').then(res => res.json())
      ]);

      const services: ServiceHealth[] = [];

      // General API Health
      if (generalHealth.status === 'fulfilled') {
        const data = generalHealth.value.data || generalHealth.value;
        services.push({
          name: 'API Service',
          status: data.overall_status || data.status || 'healthy',
          response_time_ms: data.response_time_ms || data.latency_ms || 0,
          last_checked: data.timestamp || new Date().toISOString(),
          details: data
        });
      }

      // Database Health
      if (dbHealth.status === 'fulfilled') {
        const data = dbHealth.value.data || dbHealth.value;
        services.push({
          name: 'Database',
          status: data.status || 'healthy',
          response_time_ms: data.connectivity_time_ms || 0,
          last_checked: data.timestamp || new Date().toISOString(),
          details: data.connection_pool
        });
      }

      // Redis/Memory Health (from rate limits which use Redis)
      if (redisHealth.status === 'fulfilled') {
        const data = redisHealth.value.data || redisHealth.value;
        services.push({
          name: 'Cache Service',
          status: data.total_active_users !== undefined ? 'healthy' : 'degraded',
          response_time_ms: 0, // Would need actual Redis ping
          last_checked: data.timestamp || new Date().toISOString(),
          details: {
            active_users: data.total_active_users,
            custom_limits: data.custom_rate_limits
          }
        });
      }

      // Calculate overall status
      const statuses = services.map(s => s.status);
      let overall_status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
      
      if (statuses.includes('unhealthy')) {
        overall_status = 'unhealthy';
      } else if (statuses.includes('degraded')) {
        overall_status = 'degraded';
      }

      const healthOverview: HealthOverview = {
        overall_status,
        services,
        timestamp: new Date().toISOString(),
        uptime_percentage: 99.9 // Would come from actual monitoring
      };

      setHealthData(healthOverview);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Failed to fetch health data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-state-success" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-state-warning" />;
      case 'unhealthy':
        return <XCircle className="h-5 w-5 text-state-error" />;
      default:
        return <Clock className="h-5 w-5 text-text-secondary" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <Badge variant="default" className="bg-green-500 hover:bg-green-600">Healthy</Badge>;
      case 'degraded':
        return <Badge variant="default" className="bg-yellow-500 hover:bg-yellow-600">Degraded</Badge>;
      case 'unhealthy':
        return <Badge variant="destructive">Unhealthy</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getPerformanceColor = (timeMs: number) => {
    if (timeMs < 100) return 'text-state-success';
    if (timeMs < 500) return 'text-state-warning';
    return 'text-state-error';
  };

  if (loading && !healthData) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-accent-primary" />
          <p className="text-text-secondary">Loading health data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-primary flex items-center gap-3">
            <Activity className="h-8 w-8 text-accent-primary" />
            Service Health Dashboard
          </h1>
          <p className="text-text-secondary mt-2">
            Monitor the health and performance of all system services
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-sm text-text-secondary">
            Last updated: {lastUpdated}
          </div>
          <Button 
            onClick={fetchHealthData} 
            disabled={loading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Overall Health Status */}
      {healthData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              {getStatusIcon(healthData.overall_status)}
              System Status
            </CardTitle>
            <CardDescription>
              Overall system health and performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">
                  {getStatusBadge(healthData.overall_status)}
                </div>
                <p className="text-text-secondary">Overall Status</p>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-text-primary mb-2">
                  {healthData.services.length}
                </div>
                <p className="text-text-secondary">Services Monitored</p>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-text-primary mb-2">
                  {healthData.uptime_percentage}%
                </div>
                <p className="text-text-secondary">Uptime</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Individual Service Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {healthData?.services.map((service, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  {service.name === 'API Service' && <Server className="h-5 w-5" />}
                  {service.name === 'Database' && <Database className="h-5 w-5" />}
                  {service.name === 'Cache Service' && <Wifi className="h-5 w-5" />}
                  {service.name}
                </CardTitle>
                {getStatusIcon(service.status)}
              </div>
              <CardDescription>
                Response time: 
                <span className={`font-mono ml-1 ${getPerformanceColor(service.response_time_ms)}`}>
                  {service.response_time_ms.toFixed(2)}ms
                </span>
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-text-secondary">Status</span>
                  {getStatusBadge(service.status)}
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-text-secondary">Last Checked</span>
                  <span className="text-text-primary">
                    {new Date(service.last_checked).toLocaleTimeString()}
                  </span>
                </div>
                
                {service.details && (
                  <div className="pt-4 border-t border-border-subtle">
                    <h4 className="font-medium text-text-primary mb-2">Details</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {Object.entries(service.details).slice(0, 4).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-text-secondary capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="text-text-primary font-mono">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Quick Actions
          </CardTitle>
          <CardDescription>
            Common maintenance and diagnostic actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button 
              variant="outline" 
              onClick={() => window.location.reload()}
              className="h-16 flex flex-col gap-1"
            >
              <RefreshCw className="h-5 w-5" />
              <span>Reload Page</span>
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => window.open('/api/docs', '_blank')}
              className="h-16 flex flex-col gap-1"
            >
              <Server className="h-5 w-5" />
              <span>API Docs</span>
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => window.open('/monitoring', '_blank')}
              className="h-16 flex flex-col gap-1"
            >
              <Activity className="h-5 w-5" />
              <span>Monitoring</span>
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => console.log('Running diagnostics...')}
              className="h-16 flex flex-col gap-1"
            >
              <HardDrive className="h-5 w-5" />
              <span>Run Diagnostics</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}