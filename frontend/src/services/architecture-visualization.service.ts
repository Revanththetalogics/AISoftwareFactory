// Architecture visualization service for frontend
// Communicates with backend API to manage architecture diagrams

export type NodeType = 
  | 'service'
  | 'database'
  | 'cache'
  | 'message_queue'
  | 'load_balancer'
  | 'api_gateway'
  | 'container'
  | 'server'
  | 'external_service';

export type RelationshipType = 
  | 'depends_on'
  | 'communicates_with'
  | 'stores_in'
  | 'caches'
  | 'load_balances'
  | 'routes_to';

export type DiagramType = 
  | 'system_overview'
  | 'deployment'
  | 'data_flow'
  | 'network_topology'
  | 'microservices';

export interface Node {
  id: string;
  name: string;
  type: NodeType;
  x: number;
  y: number;
  width?: number;
  height?: number;
  status?: 'active' | 'inactive' | 'degraded' | 'maintenance';
  metadata?: Record<string, unknown>;
}

export interface Relationship {
  id: string;
  source_id: string;
  target_id: string;
  type: RelationshipType;
  label?: string;
  status?: 'active' | 'inactive' | 'degraded';
  metadata?: Record<string, unknown>;
}

export interface ArchitectureDiagram {
  id: string;
  name: string;
  type: DiagramType;
  nodes: Node[];
  relationships: Relationship[];
  created_at: string;
  updated_at: string;
  version: number;
  description?: string;
  layout_algorithm?: string;
  metadata?: Record<string, unknown>;
}

export interface SystemInfo {
  services: Array<{
    name: string;
    version?: string;
    status?: string;
    [key: string]: unknown;
  }>;
  databases: Array<{
    name: string;
    engine?: string;
    size?: string;
    [key: string]: unknown;
  }>;
  caches: Array<{
    name: string;
    type?: string;
    size?: string;
    [key: string]: unknown;
  }>;
  message_queues?: Array<{
    name: string;
    type?: string;
    [key: string]: unknown;
  }>;
}

class ArchitectureVisualizationService {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  // Create a new diagram
  public async createDiagram(
    name: string,
    diagramType: DiagramType,
    nodes: Node[],
    relationships: Relationship[],
    description?: string
  ): Promise<ArchitectureDiagram> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          type: diagramType,
          nodes,
          relationships,
          description
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create diagram: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as ArchitectureDiagram;
    } catch (error) {
      console.error('Failed to create diagram:', error);
      throw error;
    }
  }

  // Get all diagrams
  public async listDiagrams(diagramType?: DiagramType): Promise<ArchitectureDiagram[]> {
    try {
      const url = diagramType 
        ? `${this.baseUrl}/api/v1/architecture/?diagram_type=${diagramType}`
        : `${this.baseUrl}/api/v1/architecture/`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to list diagrams: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as ArchitectureDiagram[];
    } catch (error) {
      console.error('Failed to list diagrams:', error);
      throw error;
    }
  }

  // Get a specific diagram
  public async getDiagram(diagramId: string): Promise<ArchitectureDiagram> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/${diagramId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get diagram: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as ArchitectureDiagram;
    } catch (error) {
      console.error('Failed to get diagram:', error);
      throw error;
    }
  }

  // Update a diagram
  public async updateDiagram(
    diagramId: string,
    updates: {
      name?: string;
      nodes?: Node[];
      relationships?: Relationship[];
      description?: string;
    }
  ): Promise<ArchitectureDiagram> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/${diagramId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update diagram: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as ArchitectureDiagram;
    } catch (error) {
      console.error('Failed to update diagram:', error);
      throw error;
    }
  }

  // Delete a diagram
  public async deleteDiagram(diagramId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/${diagramId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete diagram: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(data.message);
    } catch (error) {
      console.error('Failed to delete diagram:', error);
      throw error;
    }
  }

  // Get available templates
  public async listTemplates(): Promise<ArchitectureDiagram[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/templates/`);
      
      if (!response.ok) {
        throw new Error(`Failed to list templates: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as ArchitectureDiagram[];
    } catch (error) {
      console.error('Failed to list templates:', error);
      throw error;
    }
  }

  // Get a specific template
  public async getTemplate(templateName: string): Promise<ArchitectureDiagram> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/templates/${templateName}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get template: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as ArchitectureDiagram;
    } catch (error) {
      console.error('Failed to get template:', error);
      throw error;
    }
  }

  // Generate system diagram from system info
  public async generateSystemDiagram(systemInfo: SystemInfo): Promise<ArchitectureDiagram> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(systemInfo),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate system diagram: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as ArchitectureDiagram;
    } catch (error) {
      console.error('Failed to generate system diagram:', error);
      throw error;
    }
  }

  // Export diagram in specified format
  public async exportDiagram(diagramId: string, format: 'json' | 'mermaid'): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/${diagramId}/export/${format}`);
      
      if (!response.ok) {
        throw new Error(`Failed to export diagram: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data.content as string;
    } catch (error) {
      console.error('Failed to export diagram:', error);
      throw error;
    }
  }

  // Get available node types
  public async getNodeTypes(): Promise<Array<{name: string; value: NodeType}>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/types/nodes`);
      
      if (!response.ok) {
        throw new Error(`Failed to get node types: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as Array<{name: string; value: NodeType}>;
    } catch (error) {
      console.error('Failed to get node types:', error);
      throw error;
    }
  }

  // Get available relationship types
  public async getRelationshipTypes(): Promise<Array<{name: string; value: RelationshipType}>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/types/relationships`);
      
      if (!response.ok) {
        throw new Error(`Failed to get relationship types: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as Array<{name: string; value: RelationshipType}>;
    } catch (error) {
      console.error('Failed to get relationship types:', error);
      throw error;
    }
  }

  // Get available diagram types
  public async getDiagramTypes(): Promise<Array<{name: string; value: DiagramType}>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/architecture/types/diagrams`);
      
      if (!response.ok) {
        throw new Error(`Failed to get diagram types: ${response.statusText}`);
      }

      const data = await response.json();
      return data.data as Array<{name: string; value: DiagramType}>;
    } catch (error) {
      console.error('Failed to get diagram types:', error);
      throw error;
    }
  }

  // Create diagram from template
  public async createFromTemplate(templateName: string, customizations?: {
    name?: string;
    description?: string;
  }): Promise<ArchitectureDiagram> {
    try {
      const template = await this.getTemplate(templateName);
      
      const diagramName = customizations?.name || `Copy of ${template.name}`;
      const description = customizations?.description || template.description;
      
      return await this.createDiagram(
        diagramName,
        template.type,
        template.nodes,
        template.relationships,
        description
      );
    } catch (error) {
      console.error('Failed to create diagram from template:', error);
      throw error;
    }
  }

  // Auto-layout diagram nodes
  public autoLayoutNodes(nodes: Node[], algorithm: string = 'force_directed'): Node[] {
    // Simple force-directed layout simulation
    if (algorithm === 'force_directed') {
      // This is a simplified version - in practice, you'd use a proper layout library
      const centerX = 400;
      const centerY = 300;
      const radius = 200;
      
      return nodes.map((node, index) => ({
        ...node,
        x: centerX + radius * Math.cos((2 * Math.PI * index) / nodes.length),
        y: centerY + radius * Math.sin((2 * Math.PI * index) / nodes.length)
      }));
    }
    
    return nodes;
  }

  // Validate diagram structure
  public validateDiagram(diagram: ArchitectureDiagram): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Check for duplicate node IDs
    const nodeIds = diagram.nodes.map(node => node.id);
    const duplicateIds = nodeIds.filter((id, index) => nodeIds.indexOf(id) !== index);
    if (duplicateIds.length > 0) {
      errors.push(`Duplicate node IDs found: ${[...new Set(duplicateIds)].join(', ')}`);
    }
    
    // Check for orphaned relationships
    const validNodeIds = new Set(nodeIds);
    for (const rel of diagram.relationships) {
      if (!validNodeIds.has(rel.source_id)) {
        errors.push(`Relationship ${rel.id} references non-existent source node: ${rel.source_id}`);
      }
      if (!validNodeIds.has(rel.target_id)) {
        errors.push(`Relationship ${rel.id} references non-existent target node: ${rel.target_id}`);
      }
    }
    
    // Check for circular dependencies (simple check)
    const dependencies = new Map<string, string[]>();
    for (const rel of diagram.relationships) {
      if (!dependencies.has(rel.source_id)) {
        dependencies.set(rel.source_id, []);
      }
      dependencies.get(rel.source_id)!.push(rel.target_id);
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// Singleton instance
export const architectureVisualizationService = new ArchitectureVisualizationService();