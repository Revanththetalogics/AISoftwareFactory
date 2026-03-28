/**
 * Knowledge Base Service
 * 
 * Provides client-side operations for knowledge base management including
 * CRUD operations for documents and search functionality.
 */

import { API_BASE_URL } from '@/lib/config';
import { errorHandler } from './error-handler.service';

interface DocumentCreateRequest {
  content: string;
  title: string;
  tags?: string[];
  source?: string;
  metadata?: Record<string, any>;
}

interface DocumentUpdateRequest {
  content?: string;
  title?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

interface SearchRequest {
  query: string;
  top_k?: number;
  filter_tags?: string[];
}

interface DocumentResponse {
  id: string;
  title: string;
  content_preview: string;
  tags: string[];
  source?: string;
  created_at: string;
  updated_at?: string;
  chunk_count: number;
}

interface SearchResponse {
  results: Array<{
    id: string;
    score: number;
    content: string;
    title: string;
    tags: string[];
  }>;
  total_results: number;
  query: string;
}

interface KnowledgeStats {
  name: string;
  document_count: number;
  vector_count: number;
}

interface APIResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

class KnowledgeService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/knowledge`;
  }

  /**
   * Get knowledge base statistics
   */
  async getStats(): Promise<KnowledgeStats> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/stats`);
        const result: APIResponse<KnowledgeStats> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to get knowledge stats');
        }
        
        return result.data!;
      },
      'KnowledgeService',
      'getStats',
      {
        showToast: false,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: { name: 'Knowledge Base', document_count: 0, vector_count: 0 }
      }
    );
  }

  /**
   * Add a new document to the knowledge base
   */
  async addDocument(request: DocumentCreateRequest): Promise<string> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/documents`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        });
        
        const result: APIResponse<{ document_id: string }> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to add document');
        }
        
        return result.data!.document_id;
      },
      'KnowledgeService',
      'addDocument',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 2000,
        fallbackData: null
      }
    );
  }

  /**
   * Get a specific document by ID
   */
  async getDocument(docId: string): Promise<DocumentResponse> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/documents/${docId}`);
        const result: APIResponse<DocumentResponse> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to get document');
        }
        
        return result.data!;
      },
      'KnowledgeService',
      'getDocument',
      {
        showToast: true,
        retryAttempts: 2,
        retryDelay: 1000,
        fallbackData: {
          id: docId,
          title: 'Document Not Found',
          content_preview: 'This document could not be retrieved.',
          tags: [],
          created_at: new Date().toISOString(),
          chunk_count: 0
        }
      }
    );
  }

  /**
   * Update an existing document
   */
  async updateDocument(docId: string, request: DocumentUpdateRequest): Promise<void> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/documents/${docId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        });
        
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to update document');
        }
      },
      'KnowledgeService',
      'updateDocument',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 2000,
        fallbackData: undefined
      }
    );
  }

  /**
   * Delete a document from the knowledge base
   */
  async deleteDocument(docId: string): Promise<void> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/documents/${docId}`, {
          method: 'DELETE',
        });
        
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to delete document');
        }
      },
      'KnowledgeService',
      'deleteDocument',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 1500,
        fallbackData: undefined
      }
    );
  }

  /**
   * Search documents in the knowledge base
   */
  async searchDocuments(request: SearchRequest): Promise<SearchResponse> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        });
        
        const result: APIResponse<SearchResponse> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Search failed');
        }
        
        return result.data!;
      },
      'KnowledgeService',
      'searchDocuments',
      {
        showToast: false,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: {
          results: [],
          total_results: 0,
          query: request.query
        }
      }
    );
  }

  /**
   * List all documents with pagination and filtering
   */
  async listDocuments(skip: number = 0, limit: number = 50, tags?: string[]): Promise<{
    documents: DocumentResponse[];
    total_count: number;
    skip: number;
    limit: number;
  }> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
        });
        
        if (tags && tags.length > 0) {
          params.append('tags', tags.join(','));
        }
        
        const response = await fetch(`${this.baseUrl}/documents?${params}`);
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to list documents');
        }
        
        return result.data!;
      },
      'KnowledgeService',
      'listDocuments',
      {
        showToast: false,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: {
          documents: [],
          total_count: 0,
          skip: skip,
          limit: limit
        }
      }
    );
  }
}

// Export singleton instance
export const knowledgeService = new KnowledgeService();

// Export types for convenience
export type {
  DocumentCreateRequest,
  DocumentUpdateRequest,
  SearchRequest,
  DocumentResponse,
  SearchResponse,
  KnowledgeStats,
};
