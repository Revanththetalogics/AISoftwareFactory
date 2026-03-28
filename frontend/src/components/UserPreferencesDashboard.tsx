'use client';

import { useState, useEffect } from 'react';
import { 
  userPreferenceService, 
  PreferenceCategory,
  usePreference
} from '@/services/user-preference.service';

export default function UserPreferencesDashboard() {
  const [categories, setCategories] = useState<PreferenceCategory[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('appearance');
  const [isExporting, setIsExporting] = useState(false);

  // Theme preference
  const [theme, setTheme] = usePreference('appearance.theme', 'system');
  const [fontSize, setFontSize] = usePreference('appearance.fontSize', 'medium');
  const [compactMode, setCompactMode] = usePreference('appearance.compactMode', false);
  const [animations, setAnimations] = usePreference('appearance.animations', true);

  // Notification preferences
  const [emailNotifications, setEmailNotifications] = usePreference('notifications.email', true);
  const [pushNotifications, setPushNotifications] = usePreference('notifications.push', true);
  const [desktopNotifications, setDesktopNotifications] = usePreference('notifications.desktop', true);
  const [notificationFrequency, setNotificationFrequency] = usePreference('notifications.frequency', 'instant');

  // Privacy preferences
  const [analytics, setAnalytics] = usePreference('privacy.analytics', true);
  const [crashReports, setCrashReports] = usePreference('privacy.crashReports', true);
  const [usageTracking, setUsageTracking] = usePreference('privacy.usageTracking', true);

  // Workspace preferences
  const [defaultView, setDefaultView] = usePreference('workspace.defaultView', 'dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = usePreference('workspace.sidebarCollapsed', false);
  const [layout, setLayout] = usePreference('workspace.layout', 'grid');

  useEffect(() => {
    loadCategories();
    userPreferenceService.initialize();
  }, []);

  const loadCategories = () => {
    const allCategories = userPreferenceService.getAllCategories();
    setCategories(allCategories);
  };

  const filteredCategories = categories.filter(category =>
    category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    category.preferences.some(pref => 
      pref.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pref.label.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const exportPreferences = async () => {
    setIsExporting(true);
    try {
      const data = userPreferenceService.exportPreferences();
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `theta-ai-preferences-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export preferences:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const importPreferences = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      await userPreferenceService.importPreferences(text);
      loadCategories(); // Reload categories after import
      alert('Preferences imported successfully!');
    } catch (error) {
      console.error('Failed to import preferences:', error);
      alert('Failed to import preferences. Please check the file format.');
    }
  };

  const resetCategory = (categoryId: string) => {
    if (confirm(`Reset all ${categoryId} preferences to default values?`)) {
      userPreferenceService.resetCategory(categoryId);
      loadCategories();
    }
  };

  const getCategoryIcon = (categoryId: string) => {
    const category = categories.find(c => c.id === categoryId);
    return category?.icon || '⚙️';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">User Preferences</h1>
            <p className="text-gray-600 mt-1">
              Customize your experience and manage your settings
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={exportPreferences}
              disabled={isExporting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              {isExporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Exporting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Export Preferences
                </>
              )}
            </button>
            
            <label className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 cursor-pointer flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Import Preferences
              <input
                type="file"
                accept=".json"
                onChange={importPreferences}
                className="hidden"
              />
            </label>
          </div>
        </div>
      </div>

      {/* Search and Category Navigation */}
      <div className="bg-white rounded-xl shadow-sm border">
        <div className="p-6 border-b border-gray-200">
          <div className="relative">
            <input
              type="text"
              placeholder="Search preferences..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex overflow-x-auto">
            {filteredCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`flex items-center px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 ${
                  activeCategory === category.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{category.icon}</span>
                {category.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Preferences Content */}
        <div className="p-6">
          {filteredCategories
            .filter(category => category.id === activeCategory)
            .map(category => (
              <div key={category.id} className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2 flex items-center">
                    <span className="mr-2">{category.icon}</span>
                    {category.name}
                  </h2>
                  <p className="text-gray-600">{category.description}</p>
                </div>

                <div className="space-y-6">
                  {/* Appearance Preferences */}
                  {category.id === 'appearance' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Theme
                        </label>
                        <select
                          value={theme}
                          onChange={(e) => setTheme(e.target.value as any)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="light">Light</option>
                          <option value="dark">Dark</option>
                          <option value="system">System</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Font Size
                        </label>
                        <select
                          value={fontSize}
                          onChange={(e) => setFontSize(e.target.value as any)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="small">Small</option>
                          <option value="medium">Medium</option>
                          <option value="large">Large</option>
                        </select>
                      </div>

                      <div className="md:col-span-2">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="compactMode"
                            checked={compactMode}
                            onChange={(e) => setCompactMode(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor="compactMode" className="ml-2 block text-sm text-gray-700">
                            Compact Mode
                          </label>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          Reduce spacing and use more compact layouts
                        </p>
                      </div>

                      <div className="md:col-span-2">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="animations"
                            checked={animations}
                            onChange={(e) => setAnimations(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor="animations" className="ml-2 block text-sm text-gray-700">
                            Enable Animations
                          </label>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          Show smooth transitions and animations throughout the interface
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Notification Preferences */}
                  {category.id === 'notifications' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="emailNotifications"
                            checked={emailNotifications}
                            onChange={(e) => setEmailNotifications(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor="emailNotifications" className="ml-2 block text-sm text-gray-700">
                            Email Notifications
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="pushNotifications"
                            checked={pushNotifications}
                            onChange={(e) => setPushNotifications(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor="pushNotifications" className="ml-2 block text-sm text-gray-700">
                            Push Notifications
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="desktopNotifications"
                            checked={desktopNotifications}
                            onChange={(e) => setDesktopNotifications(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor="desktopNotifications" className="ml-2 block text-sm text-gray-700">
                            Desktop Notifications
                          </label>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Notification Frequency
                        </label>
                        <select
                          value={notificationFrequency}
                          onChange={(e) => setNotificationFrequency(e.target.value as any)}
                          className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="instant">Instant</option>
                          <option value="daily">Daily Digest</option>
                          <option value="weekly">Weekly Summary</option>
                        </select>
                      </div>
                    </div>
                  )}

                  {/* Privacy Preferences */}
                  {category.id === 'privacy' && (
                    <div className="space-y-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="analytics"
                          checked={analytics}
                          onChange={(e) => setAnalytics(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="analytics" className="ml-2 block text-sm text-gray-700">
                          Analytics Collection
                        </label>
                      </div>
                      <p className="text-xs text-gray-500 ml-6">
                        Help us improve by sharing anonymous usage data
                      </p>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="crashReports"
                          checked={crashReports}
                          onChange={(e) => setCrashReports(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="crashReports" className="ml-2 block text-sm text-gray-700">
                          Crash Reports
                        </label>
                      </div>
                      <p className="text-xs text-gray-500 ml-6">
                        Automatically send crash reports to help fix bugs
                      </p>

                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="usageTracking"
                          checked={usageTracking}
                          onChange={(e) => setUsageTracking(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="usageTracking" className="ml-2 block text-sm text-gray-700">
                          Usage Tracking
                        </label>
                      </div>
                      <p className="text-xs text-gray-500 ml-6">
                        Track feature usage to improve the product
                      </p>
                    </div>
                  )}

                  {/* Workspace Preferences */}
                  {category.id === 'workspace' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Default View
                        </label>
                        <select
                          value={defaultView}
                          onChange={(e) => setDefaultView(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="dashboard">Dashboard</option>
                          <option value="projects">Projects</option>
                          <option value="analytics">Analytics</option>
                          <option value="settings">Settings</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Layout Style
                        </label>
                        <select
                          value={layout}
                          onChange={(e) => setLayout(e.target.value as any)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="grid">Grid</option>
                          <option value="list">List</option>
                          <option value="kanban">Kanban</option>
                        </select>
                      </div>

                      <div className="md:col-span-2">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="sidebarCollapsed"
                            checked={sidebarCollapsed}
                            onChange={(e) => setSidebarCollapsed(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor="sidebarCollapsed" className="ml-2 block text-sm text-gray-700">
                            Collapsed Sidebar
                          </label>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          Start with sidebar collapsed by default
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Reset Button */}
                  <div className="pt-4 border-t border-gray-200">
                    <button
                      onClick={() => resetCategory(category.id)}
                      className="px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      Reset {category.name} Preferences
                    </button>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => {
              if (confirm('Reset all preferences to default values?')) {
                categories.forEach(cat => userPreferenceService.resetCategory(cat.id));
                loadCategories();
              }
            }}
            className="p-4 text-center border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mb-2">🔄</div>
            <div className="font-medium text-gray-900">Reset All</div>
            <div className="text-sm text-gray-500">Restore all default settings</div>
          </button>

          <button
            onClick={exportPreferences}
            className="p-4 text-center border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mb-2">📤</div>
            <div className="font-medium text-gray-900">Backup</div>
            <div className="text-sm text-gray-500">Export current preferences</div>
          </button>

          <div className="p-4 text-center border border-dashed border-gray-300 rounded-lg">
            <div className="text-2xl mb-2">📥</div>
            <div className="font-medium text-gray-900">Restore</div>
            <div className="text-sm text-gray-500">Import from backup file</div>
            <label className="mt-2 inline-block px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 cursor-pointer">
              Choose File
              <input
                type="file"
                accept=".json"
                onChange={importPreferences}
                className="hidden"
              />
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}