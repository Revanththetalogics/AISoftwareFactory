'use client';

import { useState, useEffect, useRef } from 'react';
import { 
  architectureVisualizationService,
  Node,
  Relationship,
  ArchitectureDiagram,
  NodeType,
  RelationshipType,
} from '@/services/architecture-visualization.service';

export default function ArchitectureVisualization() {
  const [diagrams, setDiagrams] = useState<ArchitectureDiagram[]>([]);
  const [selectedDiagram, setSelectedDiagram] = useState<ArchitectureDiagram | null>(null);
  const [templates, setTemplates] = useState<ArchitectureDiagram[]>([]);
  const [activeTab, setActiveTab] = useState<'library' | 'editor' | 'viewer'>('library');
  const [isCreating, setIsCreating] = useState(false);
  const [draggedNode, setDraggedNode] = useState<Node | null>(null);
  const [canvasOffset, setCanvasOffset] = useState({ x: 0, y: 0 });
  const canvasRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    loadDiagrams();
    loadTemplates();
  }, []);

  const loadDiagrams = async () => {
    try {
      const diagramList = await architectureVisualizationService.listDiagrams();
      setDiagrams(diagramList);
    } catch (error) {
      console.error('Failed to load diagrams:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const templateList = await architectureVisualizationService.listTemplates();
      setTemplates(templateList);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const createNewDiagram = async (templateName?: string) => {
    setIsCreating(true);
    try {
      let newDiagram: ArchitectureDiagram;
      
      if (templateName) {
        newDiagram = await architectureVisualizationService.createFromTemplate(templateName, {
          name: `New ${templateName} Diagram`,
          description: `Based on ${templateName} template`
        });
      } else {
        // Create empty diagram
        newDiagram = await architectureVisualizationService.createDiagram(
          'New Diagram',
          'system_overview',
          [],
          [],
          'Custom architecture diagram'
        );
      }
      
      setDiagrams(prev => [...prev, newDiagram]);
      setSelectedDiagram(newDiagram);
      setActiveTab('editor');
    } catch (error) {
      console.error('Failed to create diagram:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const loadDiagram = async (diagramId: string) => {
    try {
      const diagram = await architectureVisualizationService.getDiagram(diagramId);
      setSelectedDiagram(diagram);
      setActiveTab('viewer');
    } catch (error) {
      console.error('Failed to load diagram:', error);
    }
  };

  const updateDiagram = async (updates: Partial<ArchitectureDiagram>) => {
    if (!selectedDiagram) return;
    
    try {
      const updatedDiagram = await architectureVisualizationService.updateDiagram(
        selectedDiagram.id,
        updates
      );
      setSelectedDiagram(updatedDiagram);
      setDiagrams(prev => prev.map(d => d.id === updatedDiagram.id ? updatedDiagram : d));
    } catch (error) {
      console.error('Failed to update diagram:', error);
    }
  };

  const exportDiagram = async (format: 'json' | 'mermaid' = 'json') => {
    if (!selectedDiagram) return;
    
    try {
      const exportedData = await architectureVisualizationService.exportDiagram(
        selectedDiagram.id,
        format
      );
      
      // Download the exported data
      const blob = new Blob([exportedData], { type: format === 'json' ? 'application/json' : 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedDiagram.name.replace(/\s+/g, '_')}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      console.log(`Diagram exported as ${format}`);
    } catch (error) {
      console.error('Failed to export diagram:', error);
    }
  };

  const handleNodeDrag = (node: Node, e: React.MouseEvent) => {
    setDraggedNode(node);
    setCanvasOffset({
      x: e.clientX - node.x,
      y: e.clientY - node.y
    });
  };

  const handleCanvasDrop = (e: React.MouseEvent) => {
    if (!draggedNode || !selectedDiagram) return;
    
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const newX = e.clientX - rect.left - canvasOffset.x;
    const newY = e.clientY - rect.top - canvasOffset.y;
    
    // Update node position
    const updatedNodes = selectedDiagram.nodes.map(node => 
      node.id === draggedNode.id 
        ? { ...node, x: Math.max(0, newX), y: Math.max(0, newY) }
        : node
    );
    
    updateDiagram({ nodes: updatedNodes });
    setDraggedNode(null);
  };

  const addNode = (type: NodeType, x: number, y: number) => {
    if (!selectedDiagram) return;
    
    const newNode: Node = {
      id: `node_${Date.now()}`,
      name: `${type.charAt(0).toUpperCase() + type.slice(1)} Node`,
      type,
      x,
      y,
      width: 120,
      height: 80
    };
    
    const updatedNodes = [...selectedDiagram.nodes, newNode];
    updateDiagram({ nodes: updatedNodes });
  };

  const deleteNode = (nodeId: string) => {
    if (!selectedDiagram) return;
    
    const updatedNodes = selectedDiagram.nodes.filter(node => node.id !== nodeId);
    const updatedRelationships = selectedDiagram.relationships.filter(
      rel => rel.source_id !== nodeId && rel.target_id !== nodeId
    );
    
    updateDiagram({ 
      nodes: updatedNodes,
      relationships: updatedRelationships
    });
  };

// const addRelationship = (sourceId: string, targetId: string, type: RelationshipType) => {
//   if (!selectedDiagram) return;
//   
//   const newRelationship: Relationship = {
//     id: `rel_${Date.now()}`,
//     source_id: sourceId,
//     target_id: targetId,
//     type,
//     label: type.replace('_', ' ')
//   };
//   
//   const updatedRelationships = [...selectedDiagram.relationships, newRelationship];
//   updateDiagram({ relationships: updatedRelationships });
// };

  const getNodeColor = (type: NodeType) => {
    const colors: Record<NodeType, string> = {
      'service': '#3B82F6',
      'database': '#10B981',
      'cache': '#F59E0B',
      'message_queue': '#8B5CF6',
      'load_balancer': '#EF4444',
      'api_gateway': '#06B6D4',
      'container': '#6366F1',
      'server': '#84CC16',
      'external_service': '#F97316'
    };
    return colors[type] || '#6B7280';
  };

  const getRelationshipPath = (source: Node, target: Node) => {
    const sourceWidth = source.width || 120;
    const sourceHeight = source.height || 80;
    const targetWidth = target.width || 120;
    const targetHeight = target.height || 80;
    const midX = (source.x + target.x) / 2;
    const midY = (source.y + target.y) / 2;
    return `M ${source.x + sourceWidth/2} ${source.y + sourceHeight/2} Q ${midX} ${midY} ${target.x + targetWidth/2} ${target.y + targetHeight/2}`;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Architecture Visualization</h1>
            <p className="text-gray-600 mt-1">Design and visualize system architectures</p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setActiveTab('library')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'library'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Library
            </button>
            <button
              onClick={() => setActiveTab('editor')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'editor'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              disabled={!selectedDiagram}
            >
              Editor
            </button>
            <button
              onClick={() => setActiveTab('viewer')}
              className={`px-4 py-2 rounded-lg font-medium ${
                activeTab === 'viewer'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              disabled={!selectedDiagram}
            >
              Viewer
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          {activeTab === 'library' && (
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Diagram Library</h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Create New</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => createNewDiagram()}
                      disabled={isCreating}
                      className="w-full px-3 py-2 text-left text-sm bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 flex items-center"
                    >
                      <span className="mr-2">➕</span>
                      Blank Diagram
                    </button>
                    
                    {templates.map(template => (
                      <button
                        key={template.id}
                        onClick={() => createNewDiagram(template.name.toLowerCase().replace(/\s+/g, '-'))}
                        disabled={isCreating}
                        className="w-full px-3 py-2 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 flex items-center"
                      >
                        <span className="mr-2">📄</span>
                        {template.name}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Existing Diagrams</h3>
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {diagrams.map(diagram => (
                      <button
                        key={diagram.id}
                        onClick={() => loadDiagram(diagram.id)}
                        className={`w-full px-3 py-2 text-left text-sm rounded-lg flex items-center ${
                          selectedDiagram?.id === diagram.id
                            ? 'bg-blue-100 text-blue-800 border border-blue-200'
                            : 'hover:bg-gray-100'
                        }`}
                      >
                        <span className="mr-2">📊</span>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{diagram.name}</div>
                          <div className="text-xs text-gray-500 truncate">{diagram.description}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'editor' && selectedDiagram && (
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Diagram Editor</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Diagram Name
                  </label>
                  <input
                    type="text"
                    value={selectedDiagram.name}
                    onChange={(e) => updateDiagram({ name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={selectedDiagram.description || ''}
                    onChange={(e) => updateDiagram({ description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Add Node</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {(['service', 'database', 'cache', 'api_gateway'] as NodeType[]).map(type => (
                      <button
                        key={type}
                        onClick={() => {
                          const rect = canvasRef.current?.getBoundingClientRect();
                          if (rect) {
                            addNode(type, rect.width / 2, rect.height / 2);
                          }
                        }}
                        className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded border border-gray-300 flex items-center"
                      >
                        <div 
                          className="w-3 h-3 rounded mr-1" 
                          style={{ backgroundColor: getNodeColor(type) }}
                        ></div>
                        {type.replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Export</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => exportDiagram('json')}
                      className="w-full px-3 py-2 text-sm bg-green-100 hover:bg-green-200 text-green-800 rounded-lg border border-green-200"
                    >
                      Export as JSON
                    </button>
                    <button
                      onClick={() => exportDiagram('mermaid')}
                      className="w-full px-3 py-2 text-sm bg-purple-100 hover:bg-purple-200 text-purple-800 rounded-lg border border-purple-200"
                    >
                      Export as Mermaid
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'viewer' && selectedDiagram && (
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Diagram Viewer</h2>
              
              <div className="space-y-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <h3 className="font-medium text-gray-900">{selectedDiagram.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{selectedDiagram.description}</p>
                  <div className="flex items-center text-xs text-gray-500 mt-2">
                    <span className="mr-3">📊 {selectedDiagram.nodes.length} nodes</span>
                    <span>🔗 {selectedDiagram.relationships.length} relationships</span>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Legend</h3>
                  <div className="space-y-1">
                    {Array.from(new Set(selectedDiagram.nodes.map(n => n.type))).map(type => (
                      <div key={type} className="flex items-center text-xs">
                        <div 
                          className="w-3 h-3 rounded mr-2" 
                          style={{ backgroundColor: getNodeColor(type as NodeType) }}
                        ></div>
                        <span className="capitalize">{type.replace('_', ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Canvas Area */}
        <div className="flex-1 flex flex-col">
          {activeTab === 'library' && (
            <div className="flex-1 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Architecture Library</h3>
                <p className="text-gray-500">Select or create a diagram to get started</p>
              </div>
            </div>
          )}

          {(activeTab === 'editor' || activeTab === 'viewer') && selectedDiagram && (
            <div 
              ref={canvasRef}
              className="flex-1 relative bg-white overflow-hidden"
              onMouseUp={handleCanvasDrop}
            >
              <svg 
                ref={svgRef}
                className="absolute inset-0 w-full h-full"
                style={{ minHeight: '100%', minWidth: '100%' }}
              >
                {/* Relationships */}
                {selectedDiagram.relationships.map(relationship => {
                  const sourceNode = selectedDiagram.nodes.find(n => n.id === relationship.source_id);
                  const targetNode = selectedDiagram.nodes.find(n => n.id === relationship.target_id);
                  
                  if (!sourceNode || !targetNode) return null;
                  
                  return (
                    <g key={relationship.id}>
                      <path
                        d={getRelationshipPath(sourceNode, targetNode)}
                        stroke="#9CA3AF"
                        strokeWidth="2"
                        fill="none"
                        markerEnd="url(#arrowhead)"
                      />
                      {relationship.label && (
                        <text
                          x={(sourceNode.x + targetNode.x + (sourceNode.width || 120) + (targetNode.width || 120)) / 2}
                          y={(sourceNode.y + targetNode.y + (sourceNode.height || 80) + (targetNode.height || 80)) / 2}
                          textAnchor="middle"
                          className="text-xs fill-gray-600"
                        >
                          {relationship.label}
                        </text>
                      )}
                    </g>
                  );
                })}
                
                {/* Arrow marker definition */}
                <defs>
                  <marker
                    id="arrowhead"
                    markerWidth="10"
                    markerHeight="7"
                    refX="9"
                    refY="3.5"
                    orient="auto"
                  >
                    <polygon points="0 0, 10 3.5, 0 7" fill="#9CA3AF" />
                  </marker>
                </defs>
              </svg>

              {/* Nodes */}
              {selectedDiagram.nodes.map(node => (
                <div
                  key={node.id}
                  className="absolute cursor-move group"
                  style={{
                    left: `${node.x}px`,
                    top: `${node.y}px`,
                    width: `${node.width}px`,
                    height: `${node.height}px`
                  }}
                  onMouseDown={(e) => handleNodeDrag(node, e)}
                >
                  <div 
                    className="w-full h-full rounded-lg border-2 border-gray-300 bg-white shadow-sm flex flex-col items-center justify-center p-2 hover:shadow-md transition-shadow"
                    style={{ borderColor: getNodeColor(node.type) }}
                  >
                    <div 
                      className="w-6 h-6 rounded mb-1" 
                      style={{ backgroundColor: getNodeColor(node.type) }}
                    ></div>
                    <div className="text-xs font-medium text-center text-gray-800 truncate w-full">
                      {node.name}
                    </div>
                    <div className="text-[10px] text-gray-500 capitalize truncate w-full">
                      {node.type.replace('_', ' ')}
                    </div>
                  </div>
                  
                  {activeTab === 'editor' && (
                    <button
                      onClick={() => deleteNode(node.id)}
                      className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}

              {/* Canvas controls */}
              {activeTab === 'editor' && (
                <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg border border-gray-200 p-2">
                  <div className="text-xs text-gray-500 space-y-1">
                    <div>🖱️ Drag nodes to move</div>
                    <div>➕ Use sidebar to add nodes</div>
                    <div>🗑️ Click × to delete nodes</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}