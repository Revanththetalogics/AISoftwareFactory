'use client';

import { motion } from 'framer-motion';
import { FileCode, Folder, File, MoreVertical, Upload } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const fileTree = [
  {
    name: 'backend',
    type: 'folder',
    children: [
      { name: 'api', type: 'folder', children: [] },
      { name: 'services', type: 'folder', children: [{ name: 'auth_service.py', type: 'file' }] },
      { name: 'main.py', type: 'file' },
    ],
  },
  {
    name: 'frontend',
    type: 'folder',
    children: [
      { name: 'src', type: 'folder', children: [] },
      { name: 'package.json', type: 'file' },
    ],
  },
];

export default function FilesPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">File Manager</h1>
          <p className="text-slate-400">Browse and manage generated files</p>
        </div>
        <Button className="bg-emerald-500 hover:bg-emerald-600">
          <Upload className="mr-2 h-4 w-4" />
          Upload
        </Button>
      </div>

      <Card className="border-slate-800 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="text-slate-100">Project Files</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {fileTree.map((item, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-800/50 cursor-pointer">
                  <Folder className="h-5 w-5 text-amber-400" />
                  <span className="text-slate-200">{item.name}</span>
                </div>
                {item.children?.map((child, childIdx) => (
                  <div
                    key={childIdx}
                    className="flex items-center gap-2 p-2 pl-8 rounded-lg hover:bg-slate-800/50 cursor-pointer"
                  >
                    {child.type === 'folder' ? (
                      <Folder className="h-4 w-4 text-amber-400" />
                    ) : (
                      <File className="h-4 w-4 text-blue-400" />
                    )}
                    <span className="text-slate-300 text-sm">{child.name}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
