'use client';

import { motion } from 'framer-motion';
import {
  Globe,
  Moon,
  Sun,
  Save,
  Key,
  Webhook,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useTheme } from 'next-themes';
import { useState, useEffect } from 'react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.25, 0, 1] as const,
    },
  },
};

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 0);
    return () => clearTimeout(timer);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Settings</h1>
          <p className="mt-1 text-slate-400">
            Manage your preferences and system configuration
          </p>
        </div>
        <Button className="bg-gradient-to-r from-violet-500 to-indigo-600 hover:from-violet-600 hover:to-indigo-700">
          <Save className="mr-2 h-4 w-4" />
          Save Changes
        </Button>
      </motion.div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="border-slate-800 bg-slate-900/50">
          <TabsTrigger value="general" className="data-[state=active]:bg-slate-800">
            General
          </TabsTrigger>
          <TabsTrigger value="profile" className="data-[state=active]:bg-slate-800">
            Profile
          </TabsTrigger>
          <TabsTrigger value="notifications" className="data-[state=active]:bg-slate-800">
            Notifications
          </TabsTrigger>
          <TabsTrigger value="ai" className="data-[state=active]:bg-slate-800">
            AI Configuration
          </TabsTrigger>
          <TabsTrigger value="api" className="data-[state=active]:bg-slate-800">
            API & Integrations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">Appearance</CardTitle>
                <CardDescription className="text-slate-400">
                  Customize how the dashboard looks
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {theme === 'dark' ? (
                      <Moon className="h-5 w-5 text-slate-400" />
                    ) : (
                      <Sun className="h-5 w-5 text-slate-400" />
                    )}
                    <div>
                      <p className="font-medium text-slate-200">Theme</p>
                      <p className="text-sm text-slate-500">Choose your preferred color scheme</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant={theme === 'light' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setTheme('light')}
                      className={theme === 'light' ? 'bg-violet-600' : 'border-slate-700 text-slate-300'}
                    >
                      <Sun className="mr-1.5 h-4 w-4" />
                      Light
                    </Button>
                    <Button
                      variant={theme === 'dark' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setTheme('dark')}
                      className={theme === 'dark' ? 'bg-violet-600' : 'border-slate-700 text-slate-300'}
                    >
                      <Moon className="mr-1.5 h-4 w-4" />
                      Dark
                    </Button>
                    <Button
                      variant={theme === 'system' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setTheme('system')}
                      className={theme === 'system' ? 'bg-violet-600' : 'border-slate-700 text-slate-300'}
                    >
                      <Globe className="mr-1.5 h-4 w-4" />
                      System
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">Language & Region</CardTitle>
                <CardDescription className="text-slate-400">
                  Set your language and regional preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label className="text-slate-300">Language</Label>
                    <select className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200">
                      <option>English (US)</option>
                      <option>English (UK)</option>
                      <option>Spanish</option>
                      <option>French</option>
                      <option>German</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate-300">Timezone</Label>
                    <select className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200">
                      <option>UTC (Coordinated Universal Time)</option>
                      <option>EST (Eastern Standard Time)</option>
                      <option>PST (Pacific Standard Time)</option>
                      <option>GMT (Greenwich Mean Time)</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="profile" className="space-y-6">
          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">Profile Information</CardTitle>
                <CardDescription className="text-slate-400">
                  Update your personal information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label className="text-slate-300">First Name</Label>
                    <Input
                      defaultValue="John"
                      className="border-slate-700 bg-slate-800 text-slate-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate-300">Last Name</Label>
                    <Input
                      defaultValue="Doe"
                      className="border-slate-700 bg-slate-800 text-slate-200"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Email</Label>
                  <Input
                    type="email"
                    defaultValue="john@example.com"
                    className="border-slate-700 bg-slate-800 text-slate-200"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Company</Label>
                  <Input
                    defaultValue="Acme Inc"
                    className="border-slate-700 bg-slate-800 text-slate-200"
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">Notification Preferences</CardTitle>
                <CardDescription className="text-slate-400">
                  Choose what notifications you want to receive
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { id: 'deployments', label: 'Deployment Updates', description: 'Get notified when deployments complete or fail' },
                  { id: 'agents', label: 'Agent Activity', description: 'Receive updates about AI agent tasks' },
                  { id: 'simulations', label: 'Simulation Results', description: 'Get notified when simulations complete' },
                  { id: 'system', label: 'System Alerts', description: 'Important system health notifications' },
                  { id: 'email', label: 'Email Notifications', description: 'Receive notifications via email' },
                ].map((item) => (
                  <div key={item.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-200">{item.label}</p>
                      <p className="text-sm text-slate-500">{item.description}</p>
                    </div>
                    <Switch defaultChecked={item.id !== 'email'} />
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="ai" className="space-y-6">
          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">AI Model Configuration</CardTitle>
                <CardDescription className="text-slate-400">
                  Configure AI model settings and providers
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Default LLM Provider</Label>
                  <select className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200">
                    <option>Ollama (Local)</option>
                    <option>OpenAI</option>
                    <option>Anthropic</option>
                    <option>Groq</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Default Model</Label>
                  <select className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200">
                    <option>llama3.2:latest</option>
                    <option>codellama:latest</option>
                    <option>mistral:latest</option>
                    <option>mixtral:latest</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Temperature</Label>
                  <Input
                    type="number"
                    defaultValue="0.7"
                    min="0"
                    max="2"
                    step="0.1"
                    className="border-slate-700 bg-slate-800 text-slate-200"
                  />
                  <p className="text-xs text-slate-500">Controls creativity vs consistency</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">Agent Behavior</CardTitle>
                <CardDescription className="text-slate-400">
                  Configure how AI agents work
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-200">Auto-approve Tasks</p>
                    <p className="text-sm text-slate-500">Allow agents to proceed without approval</p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-200">Parallel Execution</p>
                    <p className="text-sm text-slate-500">Run multiple agents simultaneously</p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="api" className="space-y-6">
          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">API Keys</CardTitle>
                <CardDescription className="text-slate-400">
                  Manage your API keys for external integrations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg border border-slate-800 bg-slate-800/30 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Key className="h-5 w-5 text-slate-400" />
                      <div>
                        <p className="font-medium text-slate-200">Production API Key</p>
                        <p className="text-xs text-slate-500">Use this for production deployments</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="border-slate-700 text-slate-300">
                      Regenerate
                    </Button>
                  </div>
                  <div className="mt-3 flex items-center gap-2">
                    <code className="flex-1 rounded bg-slate-900 px-3 py-2 text-sm text-slate-400">
                      af_prod_••••••••••••••••••••••••
                    </code>
                    <Button variant="ghost" size="sm" className="text-slate-400">
                      Show
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Card className="border-slate-800 bg-slate-900/50">
              <CardHeader>
                <CardTitle className="text-lg text-slate-100">Webhooks</CardTitle>
                <CardDescription className="text-slate-400">
                  Configure webhooks for external notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Webhook className="h-5 w-5 text-slate-400" />
                    <div>
                      <p className="font-medium text-slate-200">Deployment Webhook</p>
                      <p className="text-sm text-slate-500">Notify external systems on deployment</p>
                    </div>
                  </div>
                  <Switch />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Webhook URL</Label>
                  <Input
                    placeholder="https://api.example.com/webhook"
                    className="border-slate-700 bg-slate-800 text-slate-200"
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
