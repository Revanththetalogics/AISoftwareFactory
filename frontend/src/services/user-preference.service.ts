// User preference persistence service
// Manages user settings, preferences, and personalization across sessions

// @ts-ignore - These will be imported in component files
import { useState, useEffect, useCallback } from 'react';

export type PreferenceScope = 'user' | 'project' | 'global' | 'temporary';
export type PreferenceType = 'boolean' | 'string' | 'number' | 'array' | 'object';

export interface UserPreference<T = any> {
  key: string;
  value: T;
  type: PreferenceType;
  scope: PreferenceScope;
  category: string;
  label: string;
  description?: string;
  defaultValue: T;
  createdAt: string;
  updatedAt: string;
  synced: boolean;
  version: number;
}

export interface PreferenceCategory {
  id: string;
  name: string;
  icon: string;
  description: string;
  preferences: UserPreference[];
}

export interface UserPreferences {
  appearance: {
    theme: 'light' | 'dark' | 'system';
    fontSize: 'small' | 'medium' | 'large';
    fontFamily: string;
    compactMode: boolean;
    animations: boolean;
  };
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
    sound: boolean;
    frequency: 'instant' | 'daily' | 'weekly';
  };
  privacy: {
    analytics: boolean;
    crashReports: boolean;
    usageTracking: boolean;
    dataSharing: boolean;
  };
  workspace: {
    defaultView: string;
    sidebarCollapsed: boolean;
    recentProjects: string[];
    pinnedProjects: string[];
    layout: 'grid' | 'list' | 'kanban';
  };
  integrations: {
    github: boolean;
    gitlab: boolean;
    slack: boolean;
    discord: boolean;
    jira: boolean;
  };
  development: {
    debugMode: boolean;
    showBetaFeatures: boolean;
    experimentalFeatures: string[];
    codeEditor: 'vscode' | 'vim' | 'emacs' | 'default';
    terminalTheme: string;
  };
}

class UserPreferenceService {
  private preferences: Map<string, UserPreference> = new Map();
  private categories: Map<string, PreferenceCategory> = new Map();
  private storageKey = 'user_preferences';
  private syncInterval: NodeJS.Timeout | null = null;
  private isInitialized = false;

  constructor() {
    this.initializeCategories();
  }

  // Initialize preference categories
  private initializeCategories(): void {
    this.categories.set('appearance', {
      id: 'appearance',
      name: 'Appearance',
      icon: '🎨',
      description: 'Customize the look and feel of the application',
      preferences: []
    });

    this.categories.set('notifications', {
      id: 'notifications',
      name: 'Notifications',
      icon: '🔔',
      description: 'Manage how and when you receive notifications',
      preferences: []
    });

    this.categories.set('privacy', {
      id: 'privacy',
      name: 'Privacy',
      icon: '🔒',
      description: 'Control your privacy and data sharing settings',
      preferences: []
    });

    this.categories.set('workspace', {
      id: 'workspace',
      name: 'Workspace',
      icon: '💻',
      description: 'Configure your workspace and project settings',
      preferences: []
    });

    this.categories.set('integrations', {
      id: 'integrations',
      name: 'Integrations',
      icon: '🔌',
      description: 'Manage external service integrations',
      preferences: []
    });

    this.categories.set('development', {
      id: 'development',
      name: 'Development',
      icon: '⚙️',
      description: 'Developer tools and advanced settings',
      preferences: []
    });
  }

  // Initialize the service
  public async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      await this.loadPreferences();
      this.setupAutoSync();
      this.isInitialized = true;
      console.log('User preference service initialized');
    } catch (error) {
      console.error('Failed to initialize preference service:', error);
    }
  }

  // Load preferences from storage
  private async loadPreferences(): Promise<void> {
    try {
      let storedData: string | null = null;
      
      // Try localStorage first
      if (typeof localStorage !== 'undefined') {
        storedData = localStorage.getItem(this.storageKey);
      }

      if (storedData) {
        const parsed = JSON.parse(storedData);
        Object.entries(parsed).forEach(([key, pref]: [string, any]) => {
          this.preferences.set(key, pref);
        });
      } else {
        // Initialize with default preferences
        this.initializeDefaultPreferences();
      }
    } catch (error) {
      console.error('Failed to load preferences:', error);
      this.initializeDefaultPreferences();
    }
  }

  // Initialize default preferences
  private initializeDefaultPreferences(): void {
    const defaults: Partial<UserPreferences> = {
      appearance: {
        theme: 'system',
        fontSize: 'medium',
        fontFamily: 'Inter, sans-serif',
        compactMode: false,
        animations: true
      },
      notifications: {
        email: true,
        push: true,
        desktop: true,
        sound: true,
        frequency: 'instant'
      },
      privacy: {
        analytics: true,
        crashReports: true,
        usageTracking: true,
        dataSharing: false
      },
      workspace: {
        defaultView: 'dashboard',
        sidebarCollapsed: false,
        recentProjects: [],
        pinnedProjects: [],
        layout: 'grid'
      },
      integrations: {
        github: false,
        gitlab: false,
        slack: false,
        discord: false,
        jira: false
      },
      development: {
        debugMode: false,
        showBetaFeatures: false,
        experimentalFeatures: [],
        codeEditor: 'default',
        terminalTheme: 'default'
      }
    };

    // Register all default preferences
    Object.entries(defaults).forEach(([category, prefs]) => {
      if (prefs) {
        Object.entries(prefs).forEach(([key, value]) => {
          const fullKey = `${category}.${key}`;
          this.setPreference(fullKey, value, category, typeof value as PreferenceType);
        });
      }
    });
  }

  // Set a preference value
  public setPreference<T>(
    key: string,
    value: T,
    category: string,
    type: PreferenceType = this.inferType(value),
    scope: PreferenceScope = 'user'
  ): void {
    const preference: UserPreference<T> = {
      key,
      value,
      type,
      scope,
      category,
      label: this.formatLabel(key),
      defaultValue: value,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      synced: false,
      version: 1
    };

    this.preferences.set(key, preference as UserPreference);
    this.persistPreferences();
    
    // Update category
    const categoryObj = this.categories.get(category);
    if (categoryObj) {
      const existingIndex = categoryObj.preferences.findIndex(p => p.key === key);
      if (existingIndex >= 0) {
        categoryObj.preferences[existingIndex] = preference as UserPreference;
      } else {
        categoryObj.preferences.push(preference as UserPreference);
      }
    }
  }

  // Get a preference value
  public getPreference<T>(key: string, defaultValue?: T): T {
    const preference = this.preferences.get(key);
    if (preference) {
      return preference.value as T;
    }
    return defaultValue as T;
  }

  // Get all preferences in a category
  public getCategoryPreferences(category: string): UserPreference[] {
    return Array.from(this.preferences.values()).filter(pref => pref.category === category);
  }

  // Get all categories with their preferences
  public getAllCategories(): PreferenceCategory[] {
    return Array.from(this.categories.values());
  }

  // Reset a preference to its default value
  public resetPreference(key: string): void {
    const preference = this.preferences.get(key);
    if (preference) {
      preference.value = preference.defaultValue;
      preference.updatedAt = new Date().toISOString();
      preference.version += 1;
      this.persistPreferences();
    }
  }

  // Reset all preferences in a category
  public resetCategory(category: string): void {
    const preferences = this.getCategoryPreferences(category);
    preferences.forEach(pref => {
      pref.value = pref.defaultValue;
      pref.updatedAt = new Date().toISOString();
      pref.version += 1;
    });
    this.persistPreferences();
  }

  // Export preferences
  public exportPreferences(): string {
    const exportData = {
      preferences: Object.fromEntries(this.preferences),
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
    return JSON.stringify(exportData, null, 2);
  }

  // Import preferences
  public async importPreferences(data: string): Promise<void> {
    try {
      const importData = JSON.parse(data);
      if (importData.preferences) {
        Object.entries(importData.preferences).forEach(([key, pref]: [string, any]) => {
          this.preferences.set(key, pref);
        });
        this.persistPreferences();
        console.log('Preferences imported successfully');
      }
    } catch (error) {
      console.error('Failed to import preferences:', error);
      throw error;
    }
  }

  // Watch for preference changes
  public watchPreference<T>(key: string, callback: (newValue: T, oldValue: T) => void): () => void {
    const watcher = (pref: UserPreference) => {
      if (pref.key === key) {
        callback(pref.value as T, this.getPreference<T>(key));
      }
    };

    // In a real implementation, you'd have an event system
    // For now, we'll just return a cleanup function
    return () => {
      // Cleanup logic would go here
    };
  }

  // Bulk update preferences
  public bulkUpdate(updates: Record<string, any>): void {
    Object.entries(updates).forEach(([key, value]) => {
      this.setPreference(key, value, key.split('.')[0]);
    });
  }

  // Search preferences
  public searchPreferences(query: string): UserPreference[] {
    const searchTerm = query.toLowerCase();
    return Array.from(this.preferences.values()).filter(pref =>
      pref.key.toLowerCase().includes(searchTerm) ||
      pref.label.toLowerCase().includes(searchTerm) ||
      pref.description?.toLowerCase().includes(searchTerm)
    );
  }

  // Private helper methods
  private inferType(value: any): PreferenceType {
    if (typeof value === 'boolean') return 'boolean';
    if (typeof value === 'string') return 'string';
    if (typeof value === 'number') return 'number';
    if (Array.isArray(value)) return 'array';
    return 'object';
  }

  private formatLabel(key: string): string {
    return key
      .split('.')
      .pop()!
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase());
  }

  private persistPreferences(): void {
    try {
      if (typeof localStorage !== 'undefined') {
        const data = Object.fromEntries(this.preferences);
        localStorage.setItem(this.storageKey, JSON.stringify(data));
      }
    } catch (error) {
      console.error('Failed to persist preferences:', error);
    }
  }

  private setupAutoSync(): void {
    // Set up periodic sync (every 5 minutes)
    this.syncInterval = setInterval(() => {
      this.syncPreferences();
    }, 5 * 60 * 1000);
  }

  private async syncPreferences(): Promise<void> {
    // In a real implementation, this would sync with backend
    const unsynced = Array.from(this.preferences.values()).filter(pref => !pref.synced);
    
    if (unsynced.length > 0) {
      console.log(`Syncing ${unsynced.length} preferences...`);
      // Mark as synced
      unsynced.forEach(pref => {
        pref.synced = true;
      });
      this.persistPreferences();
    }
  }

  // Cleanup
  public destroy(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    this.isInitialized = false;
  }
}

// Singleton instance
export const userPreferenceService = new UserPreferenceService();

// React hook for preferences
export const usePreference = <T>(key: string, defaultValue?: T): [T, (value: T) => void] => {
  // @ts-ignore - These will be imported in the component file
  const [value, setValue] = useState<T>(() => 
    userPreferenceService.getPreference(key, defaultValue)
  );

  useEffect(() => {
    const newValue = userPreferenceService.getPreference(key, defaultValue);
    setValue(newValue);
  }, [key, defaultValue]);

  const setPrefValue = useCallback((newValue: T) => {
    userPreferenceService.setPreference(key, newValue, key.split('.')[0]);
    setValue(newValue);
  }, [key]);

  return [value, setPrefValue];
};

// Hook for watching preference changes
export const useWatchPreference = <T>(key: string, callback: (newValue: T, oldValue: T) => void) => {
  useEffect(() => {
    return userPreferenceService.watchPreference(key, callback);
  }, [key, callback]);
};