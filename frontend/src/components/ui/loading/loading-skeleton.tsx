'use client';

import { cn } from '@/lib/utils';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  isLoading?: boolean;
  children?: React.ReactNode;
}

const Skeleton = ({ 
  className, 
  isLoading = true, 
  children,
  ...props 
}: SkeletonProps) => {
  if (!isLoading) return children;

  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-bg-surface',
        className
      )}
      {...props}
    />
  );
};

interface CardSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  showHeader?: boolean;
  showContent?: boolean;
  showFooter?: boolean;
}

const CardSkeleton = ({ 
  className, 
  showHeader = true, 
  showContent = true, 
  showFooter = false,
  ...props 
}: CardSkeletonProps) => {
  return (
    <div 
      className={cn(
        'rounded-xl border border-border-default bg-bg-base p-6',
        className
      )}
      {...props}
    >
      {showHeader && (
        <div className="mb-4">
          <Skeleton className="h-6 w-3/4 mb-2" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      )}
      
      {showContent && (
        <div className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      )}
      
      {showFooter && (
        <div className="mt-6 pt-4 border-t border-border-subtle">
          <Skeleton className="h-10 w-32" />
        </div>
      )}
    </div>
  );
};

interface ListSkeletonProps {
  itemCount?: number;
  showAvatar?: boolean;
  showSecondaryText?: boolean;
  className?: string;
}

const ListSkeleton = ({ 
  itemCount = 5, 
  showAvatar = true, 
  showSecondaryText = true,
  className 
}: ListSkeletonProps) => {
  return (
    <div className={className}>
      {Array.from({ length: itemCount }).map((_, index) => (
        <div 
          key={index} 
          className="flex items-center gap-4 p-4 border-b border-border-subtle last:border-b-0"
        >
          {showAvatar && (
            <Skeleton className="h-10 w-10 rounded-full" />
          )}
          
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-3/4" />
            {showSecondaryText && (
              <Skeleton className="h-4 w-1/2" />
            )}
          </div>
          
          <Skeleton className="h-8 w-16 rounded" />
        </div>
      ))}
    </div>
  );
};

interface TableSkeletonProps {
  rowCount?: number;
  columnCount?: number;
  showHeader?: boolean;
  className?: string;
}

const TableSkeleton = ({ 
  rowCount = 5, 
  columnCount = 4, 
  showHeader = true,
  className 
}: TableSkeletonProps) => {
  return (
    <div className={cn('overflow-hidden rounded-lg border border-border-default', className)}>
      {showHeader && (
        <div className="border-b border-border-subtle bg-bg-surface">
          <div className="flex">
            {Array.from({ length: columnCount }).map((_, index) => (
              <div key={index} className="flex-1 p-4">
                <Skeleton className="h-4 w-3/4" />
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="divide-y divide-border-subtle">
        {Array.from({ length: rowCount }).map((_, rowIndex) => (
          <div key={rowIndex} className="flex animate-pulse">
            {Array.from({ length: columnCount }).map((_, colIndex) => (
              <div key={colIndex} className="flex-1 p-4">
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

interface FormSkeletonProps {
  fieldCount?: number;
  showButtons?: boolean;
  className?: string;
}

const FormSkeleton = ({ 
  fieldCount = 3, 
  showButtons = true,
  className 
}: FormSkeletonProps) => {
  return (
    <div className={cn('space-y-6', className)}>
      {Array.from({ length: fieldCount }).map((_, index) => (
        <div key={index} className="space-y-2">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-10 w-full rounded-lg" />
        </div>
      ))}
      
      {showButtons && (
        <div className="flex gap-3 pt-4">
          <Skeleton className="h-10 w-24 rounded-lg" />
          <Skeleton className="h-10 w-20 rounded-lg" />
        </div>
      )}
    </div>
  );
};

interface DashboardSkeletonProps {
  showStats?: boolean;
  showCharts?: boolean;
  showRecentItems?: boolean;
  className?: string;
}

const DashboardSkeleton = ({ 
  showStats = true, 
  showCharts = true, 
  showRecentItems = true,
  className 
}: DashboardSkeletonProps) => {
  return (
    <div className={cn('space-y-8', className)}>
      {showStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, index) => (
            <CardSkeleton 
              key={index} 
              showHeader={false} 
              showContent={false}
              className="p-5"
            >
              <div className="space-y-3">
                <Skeleton className="h-6 w-1/2" />
                <Skeleton className="h-8 w-3/4" />
                <Skeleton className="h-4 w-1/3" />
              </div>
            </CardSkeleton>
          ))}
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {showCharts && (
          <>
            <CardSkeleton className="p-6">
              <div className="mb-4">
                <Skeleton className="h-6 w-1/3" />
              </div>
              <Skeleton className="h-64 w-full rounded" />
            </CardSkeleton>
            
            <CardSkeleton className="p-6">
              <div className="mb-4">
                <Skeleton className="h-6 w-2/5" />
              </div>
              <Skeleton className="h-64 w-full rounded" />
            </CardSkeleton>
          </>
        )}
      </div>
      
      {showRecentItems && (
        <CardSkeleton>
          <div className="mb-4">
            <Skeleton className="h-6 w-1/2" />
          </div>
          <ListSkeleton itemCount={5} showAvatar={false} showSecondaryText={true} />
        </CardSkeleton>
      )}
    </div>
  );
};

interface ProfileSkeletonProps {
  showAvatar?: boolean;
  showDetails?: boolean;
  showActions?: boolean;
  className?: string;
}

const ProfileSkeleton = ({ 
  showAvatar = true, 
  showDetails = true, 
  showActions = true,
  className 
}: ProfileSkeletonProps) => {
  return (
    <div className={cn('flex flex-col md:flex-row gap-8', className)}>
      {showAvatar && (
        <div className="flex-shrink-0">
          <Skeleton className="h-32 w-32 rounded-full" />
        </div>
      )}
      
      <div className="flex-1 space-y-6">
        {showDetails && (
          <>
            <div className="space-y-3">
              <Skeleton className="h-8 w-1/2" />
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-2/3" />
            </div>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Skeleton className="h-4 w-1/4" />
                <Skeleton className="h-10 w-full rounded-lg" />
              </div>
              
              <div className="space-y-2">
                <Skeleton className="h-4 w-1/4" />
                <Skeleton className="h-10 w-full rounded-lg" />
              </div>
            </div>
          </>
        )}
        
        {showActions && (
          <div className="flex gap-3 pt-4">
            <Skeleton className="h-10 w-28 rounded-lg" />
            <Skeleton className="h-10 w-24 rounded-lg" />
          </div>
        )}
      </div>
    </div>
  );
};

export {
  Skeleton,
  CardSkeleton,
  ListSkeleton,
  TableSkeleton,
  FormSkeleton,
  DashboardSkeleton,
  ProfileSkeleton
};