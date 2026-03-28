/**
 * Schema Management Service
 * 
 * Provides frontend interface for database schema management operations
 * including CRUD operations, migrations, and schema validation.
 */

import { useState, useEffect, useCallback } from 'react';

// Types matching backend models
export interface Column {
  id: string;
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
  default_value?: string;
  description?: string;
}

export interface Table {
  id: string;
  name: string;
  columns: Column[];
  description?: string;
}

export interface Schema {
  id: string;
  name: string;
  version: string;
  tables: Table[];
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Migration {
  id: string;
  name: string;
  version: string;
  sql_up: string;
  sql_down?: string;
  applied_at?: string;
  created_at: string;
  description?: string;
  status: 'pending' | 'applied' | 'failed';
}

export interface SchemaCreateRequest {
  name: string;
  tables: Table[];
  description?: string;
}

export interface MigrationGenerateRequest {
  schema_id: string;
  description?: string;
}

class SchemaManagementService {
  private baseUrl = '/api/v1/schema';

  /**
   * Create a new database schema
   */
  async createSchema(request: SchemaCreateRequest): Promise<Schema> {
    const response = await fetch(`${this.baseUrl}/schemas`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to create schema: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Get a specific schema by ID
   */
  async getSchema(schemaId: string): Promise<Schema> {
    const response = await fetch(`${this.baseUrl}/schemas/${schemaId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get schema: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * List all schemas
   */
  async listSchemas(): Promise<Schema[]> {
    const response = await fetch(`${this.baseUrl}/schemas`);
    
    if (!response.ok) {
      throw new Error(`Failed to list schemas: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Update an existing schema
   */
  async updateSchema(schemaId: string, updates: Partial<Schema>): Promise<Schema> {
    const response = await fetch(`${this.baseUrl}/schemas/${schemaId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error(`Failed to update schema: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Delete a schema
   */
  async deleteSchema(schemaId: string): Promise<boolean> {
    const response = await fetch(`${this.baseUrl}/schemas/${schemaId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete schema: ${response.statusText}`);
    }

    return true;
  }

  /**
   * Generate migration for a schema
   */
  async generateMigration(request: MigrationGenerateRequest): Promise<Migration> {
    const response = await fetch(`${this.baseUrl}/migrations/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate migration: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Apply a migration
   */
  async applyMigration(migrationId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/migrations/${migrationId}/apply`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to apply migration: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * List migrations
   */
  async listMigrations(appliedOnly: boolean = false): Promise<Migration[]> {
    const params = new URLSearchParams();
    if (appliedOnly) {
      params.append('applied_only', 'true');
    }

    const response = await fetch(`${this.baseUrl}/migrations?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to list migrations: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }

  /**
   * Export schema in specified format
   */
  async exportSchema(schemaId: string, format: 'sql' | 'json' = 'sql'): Promise<string> {
    const response = await fetch(`${this.baseUrl}/schemas/${schemaId}/export?format=${format}`);
    
    if (!response.ok) {
      throw new Error(`Failed to export schema: ${response.statusText}`);
    }

    if (format === 'json') {
      const data = await response.json();
      return JSON.stringify(data, null, 2);
    } else {
      return await response.text();
    }
  }

  /**
   * Validate schema structure
   */
  async validateSchema(schemaId: string): Promise<{ valid: boolean; errors: string[] }> {
    const response = await fetch(`${this.baseUrl}/schemas/${schemaId}/validate`);
    
    if (!response.ok) {
      throw new Error(`Failed to validate schema: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data;
  }
}

// Global service instance
export const schemaManagementService = new SchemaManagementService();

// React hooks for easy integration
export const useSchemaManagement = () => {
  const [schemas, setSchemas] = useState<Schema[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSchemas = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const schemaList = await schemaManagementService.listSchemas();
      setSchemas(schemaList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schemas');
    } finally {
      setLoading(false);
    }
  }, []);

  const createSchema = useCallback(async (request: SchemaCreateRequest) => {
    setLoading(true);
    setError(null);
    try {
      const newSchema = await schemaManagementService.createSchema(request);
      setSchemas(prev => [...prev, newSchema]);
      return newSchema;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create schema');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSchemas();
  }, [loadSchemas]);

  return {
    schemas,
    loading,
    error,
    loadSchemas,
    createSchema,
    updateSchema: schemaManagementService.updateSchema,
    deleteSchema: schemaManagementService.deleteSchema,
    generateMigration: schemaManagementService.generateMigration,
    applyMigration: schemaManagementService.applyMigration,
    listMigrations: schemaManagementService.listMigrations,
    exportSchema: schemaManagementService.exportSchema,
    validateSchema: schemaManagementService.validateSchema,
  };
};