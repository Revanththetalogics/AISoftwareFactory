'use client';

import { motion } from 'framer-motion';
import { Brain, Search, Plus, FileText, Database, Trash2, Edit, Eye } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useState, useEffect } from 'react';
import { knowledgeService, type DocumentResponse } from '@/services/knowledge.service';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newDocContent, setNewDocContent] = useState('');
  const [newDocTags, setNewDocTags] = useState('');

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const result = await knowledgeService.listDocuments(0, 50);
      setDocuments(result.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddDocument = async () => {
    if (!newDocTitle.trim() || !newDocContent.trim()) return;
    
    try {
      const tags = newDocTags.split(',').map(tag => tag.trim()).filter(tag => tag);
      await knowledgeService.addDocument({
        title: newDocTitle,
        content: newDocContent,
        tags
      });
      
      // Reset form and close dialog
      setNewDocTitle('');
      setNewDocContent('');
      setNewDocTags('');
      setIsAddDialogOpen(false);
      
      // Reload documents
      await loadDocuments();
    } catch (error) {
      console.error('Failed to add document:', error);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await knowledgeService.deleteDocument(docId);
      await loadDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Knowledge Base</h1>
          <p className="text-text-secondary">RAG-powered knowledge management for AI agents</p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger>
            <Button className="bg-state-queued hover:bg-state-queued">
              <Plus className="mr-2 h-4 w-4" />
              Add Knowledge
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Add New Document</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="title" className="text-right">
                  Title
                </Label>
                <Input
                  id="title"
                  value={newDocTitle}
                  onChange={(e) => setNewDocTitle(e.target.value)}
                  className="col-span-3"
                  placeholder="Document title"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="tags" className="text-right">
                  Tags
                </Label>
                <Input
                  id="tags"
                  value={newDocTags}
                  onChange={(e) => setNewDocTags(e.target.value)}
                  className="col-span-3"
                  placeholder="tag1, tag2, tag3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="content" className="text-right">
                  Content
                </Label>
                <Input
                  id="content"
                  value={newDocContent}
                  onChange={(e) => setNewDocContent(e.target.value)}
                  className="col-span-3"
                  placeholder="Document content..."
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddDocument} disabled={!newDocTitle.trim() || !newDocContent.trim()}>
                Add Document
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary" />
          <Input
            placeholder="Search knowledge base..."
            className="pl-10 bg-bg-base border-border-default"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-state-queued"></div>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {documents.map((kb) => (
            <Card key={kb.id} className="border-border-default bg-bg-base/50">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="rounded-lg bg-state-queued-dim p-3">
                    <Brain className="h-6 w-6 text-state-queued" />
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleDeleteDocument(kb.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <h3 className="mt-4 font-semibold text-text-primary">{kb.title}</h3>
                <p className="mt-2 text-sm text-text-secondary line-clamp-2">
                  {kb.content_preview}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {kb.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary">{tag}</Badge>
                  ))}
                </div>
                <div className="mt-3 flex items-center gap-4 text-sm text-text-secondary">
                  <span className="flex items-center gap-1">
                    <FileText className="h-4 w-4" />
                    {kb.chunk_count} chunks
                  </span>
                  <span className="flex items-center gap-1">
                    <Database className="h-4 w-4" />
                    Updated {new Date(kb.created_at).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
          
          {documents.length === 0 && (
            <div className="col-span-full text-center py-12">
              <Brain className="mx-auto h-12 w-12 text-text-tertiary mb-4" />
              <h3 className="text-lg font-medium text-text-primary mb-2">No documents yet</h3>
              <p className="text-text-secondary mb-4">Add your first document to get started</p>
              <Button onClick={() => setIsAddDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Document
              </Button>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}
