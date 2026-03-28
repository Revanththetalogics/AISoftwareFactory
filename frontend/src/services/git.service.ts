/**
 * Git Service
 * 
 * Provides client-side operations for Git repository management including
 * clone, pull, push operations and file management.
 */

import { API_BASE_URL } from '@/lib/config';
import { errorHandler, ErrorSeverity, ErrorType } from './error-handler.service';

interface CloneRepositoryRequest {
  repo_url: string;
  destination_name?: string;
  branch?: string;
}

interface PushChangesRequest {
  commit_message?: string;
  branch?: string;
}

interface WriteFileRequest {
  file_path: string;
  content: string;
  create_parents?: boolean;
}

interface RepositoryInfo {
  name: string;
  path: string;
  current_branch: string;
  remote_url?: string;
  commit_hash: string;
  status: string;
  local_path?: string;
  cloned_at?: string;
  last_pulled?: string;
}

interface FileInfo {
  name: string;
  type: 'file' | 'directory';
  size?: number;
  modified: string;
  path: string;
  is_binary: boolean;
}

interface FileContent {
  path: string;
  content: string | null;
  size: number;
  modified: string;
  is_binary: boolean;
  encoding: string;
}

interface APIResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

class GitService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/git`;
  }

  /**
   * Clone a Git repository
   */
  async cloneRepository(request: CloneRepositoryRequest): Promise<RepositoryInfo> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/clone`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            repo_url: request.repo_url,
            destination_name: request.destination_name,
            branch: request.branch || 'main'
          }),
        });
        
        const result: APIResponse<RepositoryInfo> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to clone repository');
        }
        
        return result.data!;
      },
      'GitService',
      'cloneRepository',
      {
        showToast: true,
        retryAttempts: 2,
        retryDelay: 2000,
        fallbackData: null
      }
    );
  }

  /**
   * Pull latest changes from a repository
   */
  async pullRepository(repoName: string): Promise<RepositoryInfo> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/${repoName}/pull`, {
          method: 'POST',
        });
        
        const result: APIResponse<RepositoryInfo> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to pull repository');
        }
        
        return result.data!;
      },
      'GitService',
      'pullRepository',
      {
        showToast: true,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: null
      }
    );
  }

  /**
   * Push changes to remote repository
   */
  async pushChanges(repoName: string, request: PushChangesRequest = {}): Promise<any> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/${repoName}/push`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            commit_message: request.commit_message || 'Auto-commit from ThetaAI',
            branch: request.branch || 'main'
          }),
        });
        
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to push changes');
        }
        
        return result.data!;
      },
      'GitService',
      'pushChanges',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 3000,
        fallbackData: { success: false, message: 'Push operation failed' }
      }
    );
  }

  /**
   * List files in a repository directory
   */
  async listFiles(repoName: string, path: string = '.'): Promise<FileInfo[]> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const params = new URLSearchParams({ path });
        const response = await fetch(`${this.baseUrl}/${repoName}/files?${params}`);
        const result: APIResponse<{ files: FileInfo[] }> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to list files');
        }
        
        return result.data!.files;
      },
      'GitService',
      'listFiles',
      {
        showToast: false,
        retryAttempts: 2,
        retryDelay: 1000,
        fallbackData: []
      }
    );
  }

  /**
   * Read file content from repository
   */
  async readFile(repoName: string, filePath: string): Promise<FileContent> {
    return errorHandler.wrapServiceMethod(
      async () => {
        // Encode the file path to handle special characters
        const encodedPath = encodeURIComponent(filePath);
        const response = await fetch(`${this.baseUrl}/${repoName}/files/${encodedPath}`);
        const result: APIResponse<FileContent> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to read file');
        }
        
        return result.data!;
      },
      'GitService',
      'readFile',
      {
        showToast: true,
        retryAttempts: 2,
        retryDelay: 1000,
        fallbackData: { 
          path: filePath, 
          content: null, 
          size: 0, 
          modified: new Date().toISOString(), 
          is_binary: true, 
          encoding: 'unknown' 
        }
      }
    );
  }

  /**
   * Write file content to repository
   */
  async writeFile(repoName: string, filePath: string, content: string, createParents: boolean = true): Promise<any> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const encodedPath = encodeURIComponent(filePath);
        const response = await fetch(`${this.baseUrl}/${repoName}/files/${encodedPath}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            file_path: filePath,
            content,
            create_parents: createParents
          }),
        });
        
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to write file');
        }
        
        return result.data!;
      },
      'GitService',
      'writeFile',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 1500,
        fallbackData: { success: false, message: 'Write operation failed' }
      }
    );
  }

  /**
   * Delete file from repository
   */
  async deleteFile(repoName: string, filePath: string): Promise<any> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const encodedPath = encodeURIComponent(filePath);
        const response = await fetch(`${this.baseUrl}/${repoName}/files/${encodedPath}`, {
          method: 'DELETE',
        });
        
        const result: APIResponse<any> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to delete file');
        }
        
        return result.data!;
      },
      'GitService',
      'deleteFile',
      {
        showToast: true,
        retryAttempts: 1,
        retryDelay: 1500,
        fallbackData: { success: false, message: 'Delete operation failed' }
      }
    );
  }

  /**
   * List all cloned repositories
   */
  async listRepositories(): Promise<RepositoryInfo[]> {
    return errorHandler.wrapServiceMethod(
      async () => {
        const response = await fetch(`${this.baseUrl}/repositories`);
        const result: APIResponse<{ repositories: RepositoryInfo[], count: number }> = await response.json();
        
        if (!result.success) {
          throw new Error(result.message || 'Failed to list repositories');
        }
        
        return result.data!.repositories;
      },
      'GitService',
      'listRepositories',
      {
        showToast: false,
        retryAttempts: 2,
        retryDelay: 1500,
        fallbackData: []
      }
    );
  }
}

// Export singleton instance
export const gitService = new GitService();

// Export types for convenience
export type {
  CloneRepositoryRequest,
  PushChangesRequest,
  WriteFileRequest,
  RepositoryInfo,
  FileInfo,
  FileContent,
};
