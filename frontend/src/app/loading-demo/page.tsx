'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Skeleton,
  CardSkeleton,
  ListSkeleton,
  TableSkeleton,
  FormSkeleton,
  DashboardSkeleton,
  ProfileSkeleton
} from '@/components/ui/loading';
import {
  LoadingOverlay,
  ProgressBar,
  PulseLoader,
  WaveLoader
} from '@/components/ui/loading';

export default function LoadingDemo() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const simulateLoading = () => {
    setIsLoading(true);
    setProgress(0);
    
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setIsLoading(false), 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-text-primary mb-2">Loading Components Demo</h1>
        <p className="text-text-secondary">Showcase of various loading skeleton components</p>
      </div>

      {/* Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Controls</CardTitle>
          <CardDescription>Test the loading states</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Button onClick={simulateLoading}>Simulate Loading</Button>
          <Button 
            variant="outline" 
            onClick={() => setIsLoading(!isLoading)}
          >
            Toggle Loading
          </Button>
        </CardContent>
      </Card>

      {/* Progress Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Progress Bar</CardTitle>
        </CardHeader>
        <CardContent>
          <ProgressBar isLoading={isLoading} progress={progress} />
        </CardContent>
      </Card>

      {/* Basic Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Skeleton</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-10 w-full rounded" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Animated Loaders</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <p className="text-sm text-text-secondary mb-2">Pulse Loader</p>
              <PulseLoader />
            </div>
            <div>
              <p className="text-sm text-text-secondary mb-2">Wave Loader</p>
              <WaveLoader />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Card Skeletons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CardSkeleton showHeader={true} showContent={true} showFooter={true} />
        <CardSkeleton showHeader={false} showContent={true} showFooter={false} />
      </div>

      {/* List and Table Skeletons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>User List</CardTitle>
          </CardHeader>
          <CardContent>
            <ListSkeleton itemCount={3} showAvatar={true} showSecondaryText={true} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Table</CardTitle>
          </CardHeader>
          <CardContent>
            <TableSkeleton rowCount={3} columnCount={3} showHeader={true} />
          </CardContent>
        </Card>
      </div>

      {/* Form and Profile Skeletons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Form</CardTitle>
          </CardHeader>
          <CardContent>
            <FormSkeleton fieldCount={3} showButtons={true} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <ProfileSkeleton showAvatar={true} showDetails={true} showActions={true} />
          </CardContent>
        </Card>
      </div>

      {/* Dashboard Skeleton */}
      <Card>
        <CardHeader>
          <CardTitle>Dashboard Layout</CardTitle>
        </CardHeader>
        <CardContent>
          <DashboardSkeleton 
            showStats={true} 
            showCharts={true} 
            showRecentItems={true} 
          />
        </CardContent>
      </Card>

      {/* Loading Overlay Demo */}
      <Card>
        <CardHeader>
          <CardTitle>Loading Overlay</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative h-64 border border-border-default rounded-lg">
            <LoadingOverlay 
              isLoading={isLoading} 
              message="Loading content..."
              variant="component"
            >
              <div className="h-full flex items-center justify-center">
                <p className="text-text-secondary">Component content here</p>
              </div>
            </LoadingOverlay>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}