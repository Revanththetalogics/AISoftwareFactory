"""
Comprehensive tests for ArchitectureVisualizationService to increase coverage.
"""

from datetime import datetime

import pytest
from backend.services.architecture_service import (
    ArchitectureDiagram,
    ArchitectureVisualizationService,
    DiagramType,
    Node,
    NodeType,
    Relationship,
    RelationshipType,
)


class TestArchitectureVisualizationService:
    """Comprehensive tests for ArchitectureVisualizationService."""

    @pytest.fixture
    def architecture_service(self):
        """Create ArchitectureVisualizationService instance."""
        return ArchitectureVisualizationService()

    def test_init_creates_templates(self, architecture_service):
        """Test that initialization creates default templates."""
        assert architecture_service is not None
        assert hasattr(architecture_service, 'diagrams')
        assert hasattr(architecture_service, 'templates')
        assert len(architecture_service.templates) > 0
        assert "system-overview" in architecture_service.templates
        assert "deployment" in architecture_service.templates

    @pytest.mark.asyncio
    async def test_create_diagram_success(self, architecture_service):
        """Test successful diagram creation."""
        nodes = [
            {
                "id": "web-client",
                "name": "Web Client",
                "type": "service",
                "x": 100,
                "y": 100
            },
            {
                "id": "api-server",
                "name": "API Server",
                "type": "service",
                "x": 300,
                "y": 100
            }
        ]

        relationships = [
            {
                "id": "client-to-api",
                "source_id": "web-client",
                "target_id": "api-server",
                "type": "communicates_with"
            }
        ]

        result = await architecture_service.create_diagram(
            name="Test Architecture",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships,
            description="A test architecture diagram"
        )

        assert isinstance(result, ArchitectureDiagram)
        assert result.name == "Test Architecture"
        assert result.type == DiagramType.SYSTEM_OVERVIEW
        assert len(result.nodes) == 2
        assert len(result.relationships) == 1
        assert result.id in architecture_service.diagrams

    @pytest.mark.asyncio
    async def test_create_diagram_with_defaults(self, architecture_service):
        """Test diagram creation with default values."""
        nodes = [
            {
                "id": "single-node",
                "name": "Single Node",
                "type": "service",
                "x": 100,
                "y": 100
            }
        ]
        relationships = []  # Empty relationships list

        # No relationships
        result = await architecture_service.create_diagram(
            name="Simple Diagram",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
        )

        assert isinstance(result, ArchitectureDiagram)
        assert result.name == "Simple Diagram"
        assert len(result.nodes) == 1
        assert len(result.relationships) == 0

    @pytest.mark.asyncio
    async def test_create_diagram_with_metadata(self, architecture_service):
        """Test diagram creation with node metadata."""
        nodes = [
            {
                "id": "node-with-meta",
                "name": "Node with Metadata",
                "type": "service",
                "x": 100,
                "y": 100,
                "width": 150,
                "height": 100,
                "status": "active",
                "metadata": {"version": "1.0", "team": "backend"}
            }
        ]

        relationships = [
            {
                "id": "rel-with-meta",
                "source_id": "node-with-meta",
                "target_id": "node-with-meta",
                "type": "depends_on",
                "label": "dependency",
                "status": "active",
                "metadata": {"priority": "high"}
            }
        ]

        result = await architecture_service.create_diagram(
            name="Metadata Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
        )

        assert result.nodes[0].width == 150
        assert result.nodes[0].height == 100
        assert result.nodes[0].status == "active"
        assert result.nodes[0].metadata["version"] == "1.0"
        assert result.relationships[0].label == "dependency"
        assert result.relationships[0].metadata["priority"] == "high"

    @pytest.mark.asyncio
    async def test_get_diagram_success(self, architecture_service):
        """Test getting existing diagram."""
        # First create a diagram
        nodes = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships = []
        created_diagram = await architecture_service.create_diagram(
            name="Get Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
        )

        # Then retrieve it
        retrieved_diagram = await architecture_service.get_diagram(created_diagram.id)

        assert retrieved_diagram is not None
        assert retrieved_diagram.id == created_diagram.id
        assert retrieved_diagram.name == "Get Test"

    @pytest.mark.asyncio
    async def test_get_diagram_not_found(self, architecture_service):
        """Test getting non-existent diagram."""
        result = await architecture_service.get_diagram("non-existent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_diagrams_all(self, architecture_service):
        """Test listing all diagrams."""
        # Create multiple diagrams
        nodes = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships = []

        diagram1 = await architecture_service.create_diagram(
            name="Diagram 1", diagram_type=DiagramType.SYSTEM_OVERVIEW, nodes=nodes, relationships=relationships
        )
        diagram2 = await architecture_service.create_diagram(
            name="Diagram 2", diagram_type=DiagramType.DEPLOYMENT, nodes=nodes, relationships=relationships
        )

        all_diagrams = await architecture_service.list_diagrams()

        assert len(all_diagrams) >= 2
        diagram_ids = [d.id for d in all_diagrams]
        assert diagram1.id in diagram_ids
        assert diagram2.id in diagram_ids

    @pytest.mark.asyncio
    async def test_list_diagrams_filtered(self, architecture_service):
        """Test listing diagrams filtered by type."""
        nodes = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships = []

        # Create diagrams of different types
        system_diag = await architecture_service.create_diagram(
            name="System Diagram", diagram_type=DiagramType.SYSTEM_OVERVIEW, nodes=nodes, relationships=relationships
        )
        deployment_diag = await architecture_service.create_diagram(
            name="Deployment Diagram", diagram_type=DiagramType.DEPLOYMENT, nodes=nodes, relationships=relationships
        )

        # Filter by system overview type
        system_diagrams = await architecture_service.list_diagrams(DiagramType.SYSTEM_OVERVIEW)

        assert len(system_diagrams) >= 1
        assert system_diag.id in [d.id for d in system_diagrams]
        assert deployment_diag.id not in [d.id for d in system_diagrams]

    @pytest.mark.asyncio
    async def test_update_diagram_success(self, architecture_service):
        """Test successful diagram update."""
        # Create initial diagram
        nodes = [{"id": "old-node", "name": "Old Node", "type": "service", "x": 0, "y": 0}]
        relationships = []
        diagram = await architecture_service.create_diagram(
            name="Original Name",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
        )

        # Update with new data
        new_nodes = [
            {"id": "new-node", "name": "New Node", "type": "service", "x": 100, "y": 100}
        ]
        new_relationships = [
            {"id": "new-rel", "source_id": "new-node", "target_id": "new-node", "type": "depends_on"}
        ]

        updated_diagram = await architecture_service.update_diagram(
            diagram_id=diagram.id,
            name="Updated Name",
            nodes=new_nodes,
            relationships=new_relationships,
            description="Updated description"
        )

        assert updated_diagram is not None
        assert updated_diagram.name == "Updated Name"
        assert updated_diagram.description == "Updated description"
        assert len(updated_diagram.nodes) == 1
        assert updated_diagram.nodes[0].name == "New Node"
        assert len(updated_diagram.relationships) == 1
        # Version should be incremented (could be 1 or 2 depending on implementation)
        assert updated_diagram.version >= diagram.version

    @pytest.mark.asyncio
    async def test_update_diagram_partial(self, architecture_service):
        """Test partial diagram update."""
        # Create initial diagram
        nodes = [{"id": "test-node", "name": "Test Node", "type": "service", "x": 0, "y": 0}]
        relationships = []
        diagram = await architecture_service.create_diagram(
            name="Original",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships,
            description="Original description"
        )

        # Update only the name
        updated_diagram = await architecture_service.update_diagram(
            diagram_id=diagram.id,
            name="New Name Only"
        )

        assert updated_diagram is not None
        assert updated_diagram.name == "New Name Only"
        # Other properties should remain unchanged
        assert updated_diagram.description == "Original description"
        assert len(updated_diagram.nodes) == 1

    @pytest.mark.asyncio
    async def test_update_diagram_not_found(self, architecture_service):
        """Test updating non-existent diagram."""
        result = await architecture_service.update_diagram(
            diagram_id="non-existent",
            name="New Name"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_diagram_success(self, architecture_service):
        """Test successful diagram deletion."""
        # Create a diagram
        nodes = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships = []
        diagram = await architecture_service.create_diagram(
            name="To Delete",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
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
        result = await architecture_service.delete_diagram("non-existent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_template_success(self, architecture_service):
        """Test getting existing template."""
        template = await architecture_service.get_template("system-overview")

        assert template is not None
        assert isinstance(template, ArchitectureDiagram)
        assert template.name == "System Overview"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, architecture_service):
        """Test getting non-existent template."""
        result = await architecture_service.get_template("non-existent-template")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_templates(self, architecture_service):
        """Test listing all templates."""
        templates = await architecture_service.list_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0

        # Check that we have the expected templates
        template_names = [t.name for t in templates]
        assert "System Overview" in template_names
        assert "Deployment Architecture" in template_names

    @pytest.mark.asyncio
    async def test_generate_system_diagram_success(self, architecture_service):
        """Test generating system diagram from system info."""
        system_info = {
            "services": [
                {"name": "User Service", "version": "1.0"},
                {"name": "Order Service", "version": "1.2"}
            ],
            "databases": [
                {"name": "User DB", "engine": "PostgreSQL"},
                {"name": "Order DB", "engine": "MySQL"}
            ],
            "caches": [
                {"name": "Redis Cache", "type": "redis"}
            ]
        }

        diagram = await architecture_service.generate_system_diagram(system_info)

        assert isinstance(diagram, ArchitectureDiagram)
        assert "Auto-Generated" in diagram.name
        assert diagram.type == DiagramType.SYSTEM_OVERVIEW
        assert len(diagram.nodes) > 0
        assert len(diagram.relationships) > 0

        # Check that nodes were created for each component
        node_names = [node.name for node in diagram.nodes]
        assert "User Service" in node_names
        assert "Order Service" in node_names
        assert "User DB" in node_names
        assert "Order DB" in node_names
        assert "Redis Cache" in node_names

    @pytest.mark.asyncio
    async def test_generate_system_diagram_minimal(self, architecture_service):
        """Test generating system diagram with minimal system info."""
        system_info = {
            "services": [{"name": "Simple Service"}]
        }

        diagram = await architecture_service.generate_system_diagram(system_info)

        assert isinstance(diagram, ArchitectureDiagram)
        assert len(diagram.nodes) >= 1
        assert diagram.nodes[0].name == "Simple Service"

    @pytest.mark.asyncio
    async def test_export_diagram_json_success(self, architecture_service):
        """Test exporting diagram as JSON."""
        nodes = [{"id": "test", "name": "Test Node", "type": "service", "x": 0, "y": 0}]
        relationships = []
        diagram = await architecture_service.create_diagram(
            name="Export Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
        )

        exported = await architecture_service.export_diagram(diagram.id, "json")

        assert isinstance(exported, str)
        assert "Export Test" in exported
        assert '"nodes"' in exported
        assert '"relationships"' in exported

    @pytest.mark.asyncio
    async def test_export_diagram_mermaid_success(self, architecture_service):
        """Test exporting diagram as Mermaid."""
        nodes = [
            {"id": "node1", "name": "Node 1", "type": "service", "x": 0, "y": 0},
            {"id": "node2", "name": "Node 2", "type": "database", "x": 100, "y": 100}
        ]
        relationships = [
            {"id": "rel1", "source_id": "node1", "target_id": "node2", "type": "stores_in"}
        ]

        diagram = await architecture_service.create_diagram(
            name="Mermaid Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
        )

        exported = await architecture_service.export_diagram(diagram.id, "mermaid")

        assert isinstance(exported, str)
        assert "graph TD" in exported
        assert "node1" in exported
        assert "node2" in exported
        assert "-->" in exported  # Relationship arrow

    @pytest.mark.asyncio
    async def test_export_diagram_not_found(self, architecture_service):
        """Test exporting non-existent diagram."""
        with pytest.raises(ValueError) as exc_info:
            await architecture_service.export_diagram("non-existent", "json")

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_diagram_unsupported_format(self, architecture_service):
        """Test exporting with unsupported format."""
        nodes = [{"id": "test", "name": "Test", "type": "service", "x": 0, "y": 0}]
        relationships = []
        diagram = await architecture_service.create_diagram(
            name="Format Test",
            diagram_type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships
        )

        with pytest.raises(ValueError) as exc_info:
            await architecture_service.export_diagram(diagram.id, "unsupported-format")

        assert "Unsupported format" in str(exc_info.value)

    def test_to_mermaid_conversion(self, architecture_service):
        """Test internal Mermaid conversion method."""
        nodes = [
            Node("service1", "Service 1", NodeType.SERVICE, 100, 100),
            Node("db1", "Database 1", NodeType.DATABASE, 200, 200)
        ]
        relationships = [
            Relationship("rel1", "service1", "db1", RelationshipType.STORES_IN, "stores data")
        ]

        diagram = ArchitectureDiagram(
            id="test-diagram",
            name="Test Diagram",
            type=DiagramType.SYSTEM_OVERVIEW,
            nodes=nodes,
            relationships=relationships,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        mermaid_output = architecture_service._to_mermaid(diagram)

        assert "graph TD" in mermaid_output
        assert "service1" in mermaid_output
        assert "db1" in mermaid_output
        assert "Service 1" in mermaid_output
        assert "Database 1" in mermaid_output
        assert "|stores data|" in mermaid_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
