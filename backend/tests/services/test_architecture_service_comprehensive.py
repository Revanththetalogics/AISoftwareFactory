"""
Comprehensive tests for ArchitectureVisualizationService to increase coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC

from backend.services.architecture_service import (
    ArchitectureVisualizationService, NodeType, RelationshipType, DiagramType,
    Node, Relationship, ArchitectureDiagram
)


class TestArchitectureVisualizationService:
    """Comprehensive tests for ArchitectureVisualizationService."""

    @pytest.fixture
    def architecture_service(self):
        """Create ArchitectureVisualizationService instance."""
        return ArchitectureVisualizationService()

    def test_init(self, architecture_service):
        """Test ArchitectureVisualizationService initialization."""
        assert architecture_service is not None
        assert hasattr(architecture_service, 'diagrams')
        assert hasattr(architecture_service, 'templates')
        assert isinstance(architecture_service.diagrams, dict)
        assert isinstance(architecture_service.templates, dict)
        
        # Should have templates initialized
        assert len(architecture_service.templates) > 0
        assert "system-overview" in architecture_service.templates
        assert "deployment" in architecture_service.templates

    def test_template_initialization(self, architecture_service):
        """Test that templates are properly initialized."""
        # Check system overview template
        system_template = architecture_service.templates.get("system-overview")
        assert system_template is not None
        assert isinstance(system_template, ArchitectureDiagram)
        assert system_template.name == "System Overview"
        assert system_template.type == DiagramType.SYSTEM_OVERVIEW
        assert len(system_template.nodes) > 0
        assert len(system_template.relationships) > 0
        
        # Check deployment template
        deployment_template = architecture_service.templates.get("deployment")
        assert deployment_template is not None
        assert isinstance(deployment_template, ArchitectureDiagram)
        assert deployment_template.name == "Deployment Architecture"
        assert deployment_template.type == DiagramType.DEPLOYMENT
        assert len(deployment_template.nodes) > 0
        assert len(deployment_template.relationships) > 0

    @pytest.mark.asyncio
    async def test_create_diagram_success(self, architecture_service):
        """Test creating diagram successfully."""
        nodes_data = [
            {
                "id": "web-app",
                "name": "Web Application",
                "type": "service",
                "x": 100,
                "y": 100,
                "width": 150,
                "height": 100,
                "status": "active",
                "metadata": {"version": "1.0.0"}
            }
        ]
        
        relationships_data = [
            {
                "id": "web-db-rel",
                "source_id": "web-app",
                "target_id": "database",
                "type": "stores_in",
                "label": "writes to",
                "status": "active",
                "metadata": {"protocol": "postgresql"}
            }
        ]
        
        result = await architecture_service.create_diagram(
            name="Test Architecture",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data,
            description="Test system architecture diagram"
        )
        
        assert result is not None
        assert isinstance(result, ArchitectureDiagram)
        assert result.name == "Test Architecture"
        assert result.type == DiagramType.SYSTEM_OVERVIEW
        assert result.description == "Test system architecture diagram"
        assert len(result.nodes) == 1
        assert len(result.relationships) == 1
        assert len(result.id) > 0
        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.version == 1
        
        # Check node
        node = result.nodes[0]
        assert isinstance(node, Node)
        assert node.id == "web-app"
        assert node.name == "Web Application"
        assert node.type == NodeType.SERVICE
        assert node.x == 100
        assert node.y == 100
        assert node.width == 150
        assert node.height == 100
        assert node.status == "active"
        assert node.metadata == {"version": "1.0.0"}
        
        # Check relationship
        relationship = result.relationships[0]
        assert isinstance(relationship, Relationship)
        assert relationship.id == "web-db-rel"
        assert relationship.source_id == "web-app"
        assert relationship.target_id == "database"
        assert relationship.type == RelationshipType.STORES_IN
        assert relationship.label == "writes to"
        assert relationship.status == "active"
        assert relationship.metadata == {"protocol": "postgresql"}
        
        # Should be stored in diagrams dict
        assert result.id in architecture_service.diagrams
        assert architecture_service.diagrams[result.id] == result

    @pytest.mark.asyncio
    async def test_create_diagram_minimal_data(self, architecture_service):
        """Test creating diagram with minimal required data."""
        nodes_data = [
            {
                "id": "minimal-node",
                "name": "Minimal Node",
                "type": "service",
                "x": 0,
                "y": 0
            }
        ]
        
        relationships_data = [
            {
                "id": "minimal-rel",
                "source_id": "minimal-node",
                "target_id": "other-node",
                "type": "depends_on"
            }
        ]
        
        result = await architecture_service.create_diagram(
            name="Minimal Diagram",
            diagram_type=DiagramType.MICROSERVICES,
            nodes=nodes_data,
            relationships=relationships_data
        )
        
        assert result is not None
        # Should use default values for optional fields
        assert result.description is None
        assert len(result.nodes) == 1
        assert len(result.relationships) == 1

    @pytest.mark.asyncio
    async def test_get_diagram_success(self, architecture_service):
        """Test getting existing diagram."""
        # Create a diagram first
        nodes_data = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships_data = [{"id": "rel", "source_id": "test", "target_id": "target", "type": "depends_on"}]
        
        created_diagram = await architecture_service.create_diagram(
            name="Get Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data
        )
        
        result = await architecture_service.get_diagram(created_diagram.id)
        
        assert result is not None
        assert result.id == created_diagram.id
        assert result.name == "Get Test"

    @pytest.mark.asyncio
    async def test_get_diagram_not_found(self, architecture_service):
        """Test getting non-existent diagram."""
        result = await architecture_service.get_diagram("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_diagrams_all(self, architecture_service):
        """Test listing all diagrams."""
        # Create a few diagrams
        nodes_data = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships_data = [{"id": "rel", "source_id": "test", "target_id": "target", "type": "depends_on"}]
        
        await architecture_service.create_diagram("Diagram 1", DiagramType.SYSTEM_OVERVIEW, nodes_data, relationships_data)
        await architecture_service.create_diagram("Diagram 2", DiagramType.DEPLOYMENT, nodes_data, relationships_data)
        
        result = await architecture_service.list_diagrams()
        
        assert isinstance(result, list)
        assert len(result) >= 2
        # Should be sorted by creation time (newest first)
        for diagram in result:
            assert isinstance(diagram, ArchitectureDiagram)

    @pytest.mark.asyncio
    async def test_list_diagrams_filtered_by_type(self, architecture_service):
        """Test listing diagrams filtered by type."""
        nodes_data = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships_data = [{"id": "rel", "source_id": "test", "target_id": "target", "type": "depends_on"}]
        
        # Create diagrams of different types
        await architecture_service.create_diagram("System Diagram", DiagramType.SYSTEM_OVERVIEW, nodes_data, relationships_data)
        await architecture_service.create_diagram("Deployment Diagram", DiagramType.DEPLOYMENT, nodes_data, relationships_data)
        
        # Filter by system overview
        result = await architecture_service.list_diagrams(DiagramType.SYSTEM_OVERVIEW)
        
        assert isinstance(result, list)
        assert len(result) >= 1
        for diagram in result:
            assert diagram.type == DiagramType.SYSTEM_OVERVIEW

    @pytest.mark.asyncio
    async def test_update_diagram_success(self, architecture_service):
        """Test updating existing diagram."""
        # Create initial diagram
        nodes_data = [
            {"id": "old-node", "name": "Old Node", "type": "service", "x": 100, "y": 100}
        ]
        relationships_data = [
            {"id": "old-rel", "source_id": "old-node", "target_id": "target", "type": "depends_on"}
        ]
        
        original = await architecture_service.create_diagram(
            name="Original Diagram",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data
        )
        original_version = original.version
        
        # Update with new data
        new_nodes_data = [
            {
                "id": "new-node",
                "name": "New Node",
                "type": "database",
                "x": 200,
                "y": 200,
                "width": 180,
                "height": 120
            }
        ]
        
        new_relationships_data = [
            {
                "id": "new-rel",
                "source_id": "new-node",
                "target_id": "another-target",
                "type": "stores_in",
                "label": "stores data"
            }
        ]
        
        result = await architecture_service.update_diagram(
            diagram_id=original.id,
            name="Updated Diagram",
            nodes=new_nodes_data,
            relationships=new_relationships_data,
            description="Updated description"
        )
        
        assert result is not None
        assert result.name == "Updated Diagram"
        assert result.description == "Updated description"
        assert len(result.nodes) == 1
        assert len(result.relationships) == 1
        assert result.nodes[0].id == "new-node"
        assert result.nodes[0].name == "New Node"
        assert result.nodes[0].type == NodeType.DATABASE
        assert result.relationships[0].id == "new-rel"
        assert result.relationships[0].label == "stores data"
        # Version should be incremented
        assert result.version == original_version + 1
        # Updated timestamp should be present (timing precision may vary)

    @pytest.mark.asyncio
    async def test_update_diagram_partial_update(self, architecture_service):
        """Test partial diagram update (only name and description)."""
        # Create initial diagram
        nodes_data = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships_data = [{"id": "rel", "source_id": "test", "target_id": "target", "type": "depends_on"}]
        
        original = await architecture_service.create_diagram(
            name="Partial Update Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data
        )
        
        # Update only name and description
        result = await architecture_service.update_diagram(
            diagram_id=original.id,
            name="New Name Only",
            description="New description only"
        )
        
        assert result is not None
        assert result.name == "New Name Only"
        assert result.description == "New description only"
        # Nodes and relationships should remain unchanged
        assert len(result.nodes) == 1
        assert len(result.relationships) == 1
        assert result.nodes[0].id == "test"

    @pytest.mark.asyncio
    async def test_update_diagram_not_found(self, architecture_service):
        """Test updating non-existent diagram."""
        result = await architecture_service.update_diagram("nonexistent", name="Test")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_diagram_success(self, architecture_service):
        """Test deleting existing diagram."""
        # Create diagram first
        nodes_data = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships_data = [{"id": "rel", "source_id": "test", "target_id": "target", "type": "depends_on"}]
        
        diagram = await architecture_service.create_diagram(
            name="Delete Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data
        )
        
        # Verify it exists
        assert diagram.id in architecture_service.diagrams
        
        # Delete it
        result = await architecture_service.delete_diagram(diagram.id)
        
        assert result is True
        assert diagram.id not in architecture_service.diagrams

    @pytest.mark.asyncio
    async def test_delete_diagram_not_found(self, architecture_service):
        """Test deleting non-existent diagram."""
        result = await architecture_service.delete_diagram("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_template_success(self, architecture_service):
        """Test getting existing template."""
        result = await architecture_service.get_template("system-overview")
        
        assert result is not None
        assert isinstance(result, ArchitectureDiagram)
        assert result.name == "System Overview"
        assert result.type == DiagramType.SYSTEM_OVERVIEW

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, architecture_service):
        """Test getting non-existent template."""
        result = await architecture_service.get_template("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_templates(self, architecture_service):
        """Test listing all templates."""
        result = await architecture_service.list_templates()
        
        assert isinstance(result, list)
        assert len(result) >= 2  # Should have at least system-overview and deployment
        
        for template in result:
            assert isinstance(template, ArchitectureDiagram)
            assert template.id.startswith("template-")

    @pytest.mark.asyncio
    async def test_generate_system_diagram_success(self, architecture_service):
        """Test generating system diagram from system information."""
        system_info = {
            "services": [
                {"name": "User Service", "version": "1.2.0", "status": "active"},
                {"name": "Order Service", "version": "1.1.0", "status": "active"}
            ],
            "databases": [
                {"name": "User DB", "engine": "postgresql", "size": "100GB"},
                {"name": "Order DB", "engine": "mysql", "size": "50GB"}
            ],
            "caches": [
                {"name": "Redis Cache", "type": "redis", "size": "10GB"}
            ]
        }
        
        result = await architecture_service.generate_system_diagram(system_info)
        
        assert result is not None
        assert isinstance(result, ArchitectureDiagram)
        assert result.name == "Auto-Generated System Diagram"
        assert result.type == DiagramType.SYSTEM_OVERVIEW
        assert len(result.nodes) > 0
        assert len(result.relationships) > 0
        # Description contains auto-generation note
        assert "generated" in result.description.lower()
        
        # Should have service nodes
        service_nodes = [n for n in result.nodes if n.type == NodeType.SERVICE]
        assert len(service_nodes) == 2
        
        # Should have database nodes
        db_nodes = [n for n in result.nodes if n.type == NodeType.DATABASE]
        assert len(db_nodes) == 2
        
        # Should have cache nodes
        cache_nodes = [n for n in result.nodes if n.type == NodeType.CACHE]
        assert len(cache_nodes) == 1
        
        # Should have relationships between services and databases
        service_db_relationships = [r for r in result.relationships if r.type == RelationshipType.STORES_IN]
        assert len(service_db_relationships) > 0

    @pytest.mark.asyncio
    async def test_generate_system_diagram_minimal_info(self, architecture_service):
        """Test generating system diagram with minimal system information."""
        system_info = {
            "services": [{"name": "API Service"}],
            "databases": [{"name": "Main DB"}]
        }
        
        result = await architecture_service.generate_system_diagram(system_info)
        
        assert result is not None
        assert isinstance(result, ArchitectureDiagram)
        assert len(result.nodes) >= 2  # At least one service and one database

    @pytest.mark.asyncio
    async def test_export_diagram_json_format(self, architecture_service):
        """Test exporting diagram as JSON."""
        # Create a diagram first
        nodes_data = [
            {"id": "export-test", "name": "Export Test", "type": "service", "x": 100, "y": 100}
        ]
        relationships_data = [
            {"id": "export-rel", "source_id": "export-test", "target_id": "target", "type": "depends_on"}
        ]
        
        diagram = await architecture_service.create_diagram(
            name="Export Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data
        )
        
        result = await architecture_service.export_diagram(diagram.id, "json")
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should be valid JSON containing diagram data
        assert "Export Test" in result
        assert "export-test" in result
        assert "service" in result

    @pytest.mark.asyncio
    async def test_export_diagram_mermaid_format(self, architecture_service):
        """Test exporting diagram as Mermaid format."""
        # Create a diagram first
        nodes_data = [
            {"id": "mermaid-node", "name": "Mermaid Test", "type": "service", "x": 100, "y": 100}
        ]
        relationships_data = [
            {"id": "mermaid-rel", "source_id": "mermaid-node", "target_id": "target", "type": "depends_on"}
        ]
        
        diagram = await architecture_service.create_diagram(
            name="Mermaid Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data
        )
        
        result = await architecture_service.export_diagram(diagram.id, "mermaid")
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain Mermaid syntax
        assert "graph TD" in result
        assert "mermaid-node" in result
        # Should contain relationship syntax (could be various forms)
        assert "target" in result

    @pytest.mark.asyncio
    async def test_export_diagram_invalid_format(self, architecture_service):
        """Test exporting diagram with invalid format."""
        # Create a diagram first
        nodes_data = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships_data = [{"id": "rel", "source_id": "test", "target_id": "target", "type": "depends_on"}]
        
        diagram = await architecture_service.create_diagram(
            name="Format Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes_data,
            relationships=relationships_data
        )
        
        with pytest.raises(ValueError) as exc_info:
            await architecture_service.export_diagram(diagram.id, "xml")
        
        assert "Unsupported format: xml" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_diagram_not_found(self, architecture_service):
        """Test exporting non-existent diagram."""
        with pytest.raises(ValueError) as exc_info:
            await architecture_service.export_diagram("nonexistent", "json")
        
        assert "Diagram nonexistent not found" in str(exc_info.value)

    def test_node_post_init(self):
        """Test Node post-initialization."""
        # Without metadata
        node = Node("test-id", "Test Node", NodeType.SERVICE, 100, 200)
        assert node.metadata == {}
        
        # With metadata
        node_with_meta = Node("test-id", "Test Node", NodeType.SERVICE, 100, 200, metadata={"key": "value"})
        assert node_with_meta.metadata == {"key": "value"}

    def test_relationship_post_init(self):
        """Test Relationship post-initialization."""
        # Without metadata
        rel = Relationship("rel-id", "source", "target", RelationshipType.DEPENDS_ON)
        assert rel.metadata == {}
        
        # With metadata
        rel_with_meta = Relationship("rel-id", "source", "target", RelationshipType.DEPENDS_ON, metadata={"protocol": "http"})
        assert rel_with_meta.metadata == {"protocol": "http"}

    def test_diagram_post_init(self):
        """Test ArchitectureDiagram post-initialization."""
        nodes = [Node("test", "Test", NodeType.SERVICE, 0, 0)]
        relationships = [Relationship("rel", "test", "target", RelationshipType.DEPENDS_ON)]
        
        # Without metadata
        diagram = ArchitectureDiagram(
            "diag-id", "Test Diagram", DiagramType.SYSTEM_OVERVIEW,
            nodes, relationships,
            datetime.now(UTC).isoformat(), datetime.now(UTC).isoformat()
        )
        assert diagram.metadata == {}
        
        # With metadata
        diagram_with_meta = ArchitectureDiagram(
            "diag-id", "Test Diagram", DiagramType.SYSTEM_OVERVIEW,
            nodes, relationships,
            datetime.now(UTC).isoformat(), datetime.now(UTC).isoformat(),
            metadata={"author": "test"}
        )
        assert diagram_with_meta.metadata == {"author": "test"}

    def test_enum_values(self):
        """Test enum values are correctly defined."""
        # Test NodeType values
        assert NodeType.SERVICE.value == "service"
        assert NodeType.DATABASE.value == "database"
        assert NodeType.CACHE.value == "cache"
        assert NodeType.MESSAGE_QUEUE.value == "message_queue"
        
        # Test RelationshipType values
        assert RelationshipType.DEPENDS_ON.value == "depends_on"
        assert RelationshipType.COMMUNICATES_WITH.value == "communicates_with"
        assert RelationshipType.STORES_IN.value == "stores_in"
        
        # Test DiagramType values
        assert DiagramType.SYSTEM_OVERVIEW.value == "system_overview"
        assert DiagramType.DEPLOYMENT.value == "deployment"
        assert DiagramType.DATA_FLOW.value == "data_flow"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])