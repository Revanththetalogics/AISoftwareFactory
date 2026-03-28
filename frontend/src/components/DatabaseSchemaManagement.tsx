'use client';

import { useState, useEffect } from 'react';
import { 
  schemaManagementService,
  Column,
  MigrationGenerateRequest,
  SchemaCreateRequest,
  Table,
  Schema,
  Migration
} from '@/services/schema-management.service';

export default function DatabaseSchemaManagement() {
  const [schemas, setSchemas] = useState<Schema[]>([]);
  const [selectedSchema, setSelectedSchema] = useState<Schema | null>(null);
  const [migrations, setMigrations] = useState<Migration[]>([]);
  const [activeTab, setActiveTab] = useState<'schemas' | 'migrations' | 'editor'>('schemas');
  const [isCreating, setIsCreating] = useState(false);
  const [newTableName, setNewTableName] = useState('');
  const [newColumnName, setNewColumnName] = useState('');
  const [newColumnType, setNewColumnType] = useState('VARCHAR');

  useEffect(() => {
    loadSchemas();
    loadMigrations();
  }, []);

  const loadSchemas = async () => {
    try {
      const schemaList = await schemaManagementService.listSchemas();
      setSchemas(schemaList);
    } catch (error) {
      console.error('Failed to load schemas:', error);
    }
  };

  const loadMigrations = async () => {
    try {
      const migrationList = await schemaManagementService.listMigrations();
      setMigrations(migrationList);
    } catch (error) {
      console.error('Failed to load migrations:', error);
    }
  };

  const createNewSchema = async () => {
    setIsCreating(true);
    try {
      const request: SchemaCreateRequest = {
        name: 'New Schema',
        tables: [],
        description: 'Auto-generated schema'
      };
      const newSchema = await schemaManagementService.createSchema(request);
      setSchemas(prev => [...prev, newSchema]);
      setSelectedSchema(newSchema);
      setActiveTab('editor');
    } catch (error) {
      console.error('Failed to create schema:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const loadSchema = async (schemaId: string) => {
    try {
      const schema = await schemaManagementService.getSchema(schemaId);
      setSelectedSchema(schema);
      setActiveTab('editor');
    } catch (error) {
      console.error('Failed to load schema:', error);
    }
  };

  const updateSchema = async (updates: Partial<Schema>) => {
    if (!selectedSchema) return;
    
    try {
      const updatedSchema = await schemaManagementService.updateSchema(
        selectedSchema.id,
        updates
      );
      setSelectedSchema(updatedSchema);
      setSchemas(prev => prev.map(s => s.id === updatedSchema.id ? updatedSchema : s));
    } catch (error) {
      console.error('Failed to update schema:', error);
    }
  };

  const addTable = () => {
    if (!selectedSchema || !newTableName.trim()) return;
    
    const newTable: Table = {
      id: `table_${Date.now()}`,
      name: newTableName.trim(),
      columns: [],
      description: ''
    };
    
    const updatedTables = [...selectedSchema.tables, newTable];
    updateSchema({ tables: updatedTables });
    setNewTableName('');
  };

  const addColumn = (tableId: string) => {
    if (!selectedSchema || !newColumnName.trim()) return;
    
    const newColumn: Column = {
      id: `col_${Date.now()}`,
      name: newColumnName.trim(),
      type: newColumnType,
      nullable: true,
      primary_key: false
    };
    
    const updatedTables = selectedSchema.tables.map((table: Table) => 
      table.id === tableId 
        ? { ...table, columns: [...table.columns, newColumn] }
        : table
    );
    
    updateSchema({ tables: updatedTables });
    setNewColumnName('');
  };

  const deleteTable = (tableId: string) => {
    if (!selectedSchema) return;
    
    const updatedTables = selectedSchema.tables.filter((table: Table) => table.id !== tableId);
    updateSchema({ tables: updatedTables });
  };

  const deleteColumn = (tableId: string, columnId: string) => {
    if (!selectedSchema) return;
    
    const updatedTables = selectedSchema.tables.map((table: Table) => 
      table.id === tableId 
        ? { ...table, columns: table.columns.filter((col: Column) => col.id !== columnId) }
        : table
    );
    
    updateSchema({ tables: updatedTables });
  };

  const generateMigration = async () => {
    if (!selectedSchema) return;
    
    try {
      const request: MigrationGenerateRequest = {
        schema_id: selectedSchema.id
      };
      const migration = await schemaManagementService.generateMigration(request);
      setMigrations(prev => [migration, ...prev]);
      console.log('Migration generated successfully');
    } catch (error) {
      console.error('Failed to generate migration:', error);
    }
  };

  const applyMigration = async (migrationId: string) => {
    try {
      const result = await schemaManagementService.applyMigration(migrationId);
      console.log('Migration applied:', result);
      loadMigrations(); // Refresh migration list
    } catch (error) {
      console.error('Failed to apply migration:', error);
    }
  };

  const exportSchema = async (format: 'sql' | 'json' = 'sql') => {
    if (!selectedSchema) return;
    
    try {
      const exportedData = await schemaManagementService.exportSchema(
        selectedSchema.id,
        format
      );
      
      // Download the exported data
      const blob = new Blob([exportedData], { type: format === 'sql' ? 'text/sql' : 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedSchema.name.replace(/\s+/g, '_')}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      console.log(`Schema exported as ${format}`);
    } catch (error) {
      console.error('Failed to export schema:', error);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Database Schema Management</h1>
            <p className="text-gray-600 mt-1">Manage database schemas and migrations</p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setActiveTab('schemas')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'schemas'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Schemas
            </button>
            <button
              onClick={() => setActiveTab('migrations')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'migrations'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Migrations
            </button>
            <button
              onClick={() => setActiveTab('editor')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'editor'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              disabled={!selectedSchema}
            >
              Editor
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          {activeTab === 'schemas' && (
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Schemas</h2>
                <button
                  onClick={createNewSchema}
                  disabled={isCreating}
                  className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  New Schema
                </button>
              </div>
              
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {schemas.map(schema => (
                  <div
                    key={schema.id}
                    onClick={() => loadSchema(schema.id)}
                    className={`p-3 rounded-lg border cursor-pointer ${
                      selectedSchema?.id === schema.id
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{schema.name}</div>
                    <div className="text-sm text-gray-600 mt-1">{schema.description}</div>
                    <div className="flex items-center text-xs text-gray-500 mt-2">
                      <span className="mr-3">📋 {schema.tables.length} tables</span>
                      <span>🔄 {schema.version}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'migrations' && (
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Migrations</h2>
              
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {migrations.map(migration => (
                  <div key={migration.id} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{migration.name}</div>
                        <div className="text-sm text-gray-600 mt-1">{migration.description}</div>
                        <div className="flex items-center text-xs text-gray-500 mt-2">
                          <span className="mr-3">Version: {migration.version}</span>
                          <span>Status: <span className={`capitalize ${migration.status === 'applied' ? 'text-green-600' : 'text-yellow-600'}`}>{migration.status}</span></span>
                        </div>
                      </div>
                      {migration.status !== 'applied' && (
                        <button
                          onClick={() => applyMigration(migration.id)}
                          className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Apply
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'editor' && selectedSchema && (
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Schema Editor</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Schema Name
                  </label>
                  <input
                    type="text"
                    value={selectedSchema.name}
                    onChange={(e) => updateSchema({ name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={selectedSchema.description || ''}
                    onChange={(e) => updateSchema({ description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Add Table</h3>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newTableName}
                      onChange={(e) => setNewTableName(e.target.value)}
                      placeholder="Table name"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    />
                    <button
                      onClick={addTable}
                      disabled={!newTableName.trim()}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
                    >
                      Add
                    </button>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Actions</h3>
                  <div className="space-y-2">
                    <button
                      onClick={generateMigration}
                      className="w-full px-3 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                    >
                      Generate Migration
                    </button>
                    <button
                      onClick={() => exportSchema('sql')}
                      className="w-full px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      Export as SQL
                    </button>
                    <button
                      onClick={() => exportSchema('json')}
                      className="w-full px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Export as JSON
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {activeTab === 'schemas' && (
            <div className="flex-1 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Database Schemas</h3>
                <p className="text-gray-500">Select a schema or create a new one to get started</p>
              </div>
            </div>
          )}

          {activeTab === 'migrations' && (
            <div className="flex-1 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Migrations</h3>
                <p className="text-gray-500">View and manage database migrations</p>
              </div>
            </div>
          )}

          {activeTab === 'editor' && selectedSchema && (
            <div className="flex-1 p-6 overflow-auto">
              <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="p-6 border-b border-gray-200">
                    <h2 className="text-xl font-semibold text-gray-900">{selectedSchema.name}</h2>
                    <p className="text-gray-600 mt-1">{selectedSchema.description}</p>
                    <div className="flex items-center text-sm text-gray-500 mt-2">
                      <span className="mr-4">Version: {selectedSchema.version}</span>
                      <span>{selectedSchema.tables.length} tables</span>
                    </div>
                  </div>

                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Tables</h3>
                    
                    {selectedSchema.tables.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>No tables defined yet</p>
                        <p className="text-sm mt-1">Add a table using the sidebar</p>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {selectedSchema.tables.map((table: Table) => (
                          <div key={table.id} className="border border-gray-200 rounded-lg">
                            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                              <h4 className="font-medium text-gray-900">{table.name}</h4>
                              <button
                                onClick={() => deleteTable(table.id)}
                                className="text-red-600 hover:text-red-800 text-sm"
                              >
                                Delete Table
                              </button>
                            </div>
                            
                            <div className="p-4">
                              <div className="mb-4">
                                <div className="flex space-x-2">
                                  <input
                                    type="text"
                                    value={newColumnName}
                                    onChange={(e) => setNewColumnName(e.target.value)}
                                    placeholder="Column name"
                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                                  />
                                  <select
                                    value={newColumnType}
                                    onChange={(e) => setNewColumnType(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                                  >
                                    <option value="VARCHAR">VARCHAR</option>
                                    <option value="INTEGER">INTEGER</option>
                                    <option value="TEXT">TEXT</option>
                                    <option value="BOOLEAN">BOOLEAN</option>
                                    <option value="TIMESTAMP">TIMESTAMP</option>
                                    <option value="JSON">JSON</option>
                                  </select>
                                  <button
                                    onClick={() => addColumn(table.id)}
                                    disabled={!newColumnName.trim()}
                                    className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
                                  >
                                    Add Column
                                  </button>
                                </div>
                              </div>

                              {table.columns.length === 0 ? (
                                <p className="text-gray-500 text-sm italic">No columns defined</p>
                              ) : (
                                <div className="overflow-x-auto">
                                  <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                      <tr>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nullable</th>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Primary Key</th>
                                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                      </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                      {table.columns.map((column: Column) => (
                                        <tr key={column.id}>
                                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">{column.name}</td>
                                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">{column.type}</td>
                                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                            {column.nullable ? 'Yes' : 'No'}
                                          </td>
                                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                            {column.primary_key ? 'Yes' : 'No'}
                                          </td>
                                          <td className="px-4 py-2 whitespace-nowrap text-sm">
                                            <button
                                              onClick={() => deleteColumn(table.id, column.id)}
                                              className="text-red-600 hover:text-red-900"
                                            >
                                              Delete
                                            </button>
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}