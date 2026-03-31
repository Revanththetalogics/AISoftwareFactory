'use client';

import { useState } from 'react';
import { Trash2, Download, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';

interface BulkActionsProps {
  selectedIds: string[];
  onSelectAll: () => void;
  onClearSelection: () => void;
  onDelete: () => void;
  onExport: () => void;
  totalCount: number;
}

export function BulkActions({
  selectedIds,
  onSelectAll,
  onClearSelection,
  onDelete,
  onExport,
  totalCount,
}: BulkActionsProps) {
  const allSelected = selectedIds.length === totalCount && totalCount > 0;

  if (selectedIds.length === 0) {
    return (
      <Checkbox
        checked={allSelected}
        onCheckedChange={onSelectAll}
        aria-label="Select all"
      />
    );
  }

  return (
    <div className="flex items-center gap-2 bg-state-running-dim border border-state-running rounded-lg px-4 py-2">
      <Checkbox
        checked={allSelected}
        onCheckedChange={onSelectAll}
        aria-label="Select all"
      />
      <Badge variant="secondary" className="bg-state-running text-white">
        {selectedIds.length} selected
      </Badge>
      <div className="flex items-center gap-1 ml-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onExport}
          className="h-8 text-text-primary hover:bg-bg-hover"
        >
          <Download className="h-4 w-4 mr-1" />
          Export
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onDelete}
          className="h-8 text-state-error hover:bg-state-error/10"
        >
          <Trash2 className="h-4 w-4 mr-1" />
          Delete
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearSelection}
          className="h-8 text-text-secondary hover:bg-bg-hover"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
