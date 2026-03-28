"""
Architecture Visualization Service

Provides backend services for generating, storing, and managing architecture diagrams
and system topology visualizations for the ThetaAI platform.
"""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class NodeType(str, Enum):
    """Types of nodes in architecture diagrams."""
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    LOAD_BALANCER = "load_balancer"
    API_GATEWAY = "api_gateway"
    CONTAINER = "container"
    SERVER = "server"
    EXTERNAL_SERVICE = "external_service"


class RelationshipType(str, Enum):
    """Types of relationships between nodes."""
    DEPENDS_ON = "depends_on"
    COMMUNICATES_WITH = "communicates_with"
    STORES_IN = "stores_in"
    CACHES = "caches"
    LOAD_BALANCES = "load_balances"
    ROUTES_TO = "routes_to"


class DiagramType(str, Enum):
    """Types of architecture diagrams."""
    SYSTEM_OVERVIEW = "system_overview"
    DEPLOYMENT = "deployment"
    DATA_FLOW = "data_flow"
    NETWORK_TOPOLOGY = "network_topology"
    MICROSERVICES = "microservices"


@dataclass
class Node:
    """Represents a node in an architecture diagram."""
    id: str
    name: str
    type: NodeType
    x: float
    y: float
    width: float = 120
    height: float = 80
    status: str = "active"  # active, inactive, degraded, maintenance
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Relationship:
    """Represents a relationship between two nodes."""
    id: str
    source_id: str
    target_id: str
    type: RelationshipType
    label: str | None = None
    status: str = "active"  # active, inactive, degraded
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ArchitectureDiagram:
    """Represents a complete architecture diagram."""
    id: str
    name: str
    type: DiagramType
    nodes: list[Node]
    relationships: list[Relationship]
    created_at: str
    updated_at: str
    version: int = 1
    description: str | None = None
    layout_algorithm: str = "force_directed"
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ArchitectureVisualizationService:
    """Service for managing architecture visualization and diagrams."""

    def __init__(self):
        self.diagrams: dict[str, ArchitectureDiagram] = {}
        self.templates: dict[str, ArchitectureDiagram] = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize default architecture templates."""
        # System Overview Template
        system_nodes = [
            Node("web-client", "Web Client", NodeType.SERVICE, 100, 100),
            Node("api-gateway", "API Gateway", NodeType.API_GATEWAY, 300, 100),
            Node("auth-service", "Auth Service", NodeType.SERVICE, 500, 50),
            Node("project-service", "Project Service", NodeType.SERVICE, 500, 150),
            Node("postgres-main", "PostgreSQL", NodeType.DATABASE, 700, 100),
            Node("redis-cache", "Redis Cache", NodeType.CACHE, 700, 200),
        ]

        system_relationships = [
            Relationship("web-api", "web-client", "api-gateway", RelationshipType.COMMUNICATES_WITH),
            Relationship("api-auth", "api-gateway", "auth-service", RelationshipType.ROUTES_TO),
            Relationship("api-project", "api-gateway", "project-service", RelationshipType.ROUTES_TO),
            Relationship("auth-db", "auth-service", "postgres-main", RelationshipType.STORES_IN),
            Relationship("project-db", "project-service", "postgres-main", RelationshipType.STORES_IN),
            Relationship("auth-cache", "auth-service", "redis-cache", RelationshipType.CACHES),
        ]

        system_template = ArchitectureDiagram(
            id="template-system-overview",
            name="System Overview",
            type=DiagramType.SYSTEM_OVERVIEW,
            nodes=system_nodes,
            relationships=system_relationships,
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
            description="High-level system architecture overview",
            layout_algorithm="hierarchical"
        )

        self.templates["system-overview"] = system_template

        # Deployment Template
        deployment_nodes = [
            Node("nginx-lb", "NGINX LB", NodeType.LOAD_BALANCER, 100, 100),
            Node("backend-1", "Backend #1", NodeType.CONTAINER, 300, 50),
            Node("backend-2", "Backend #2", NodeType.CONTAINER, 300, 150),
            Node("postgres-master", "Postgres Master", NodeType.DATABASE, 500, 100),
            Node("postgres-slave", "Postgres Slave", NodeType.DATABASE, 500, 200),
        ]

        deployment_relationships = [
            Relationship("lb-be1", "nginx-lb", "backend-1", RelationshipType.LOAD_BALANCES),
            Relationship("lb-be2", "nginx-lb", "backend-2", RelationshipType.LOAD_BALANCES),
            Relationship("be-master", "backend-1", "postgres-master", RelationshipType.STORES_IN),
            Relationship("be-slave", "backend-2", "postgres-slave", RelationshipType.STORES_IN),
        ]

        deployment_template = ArchitectureDiagram(
            id="template-deployment",
            name="Deployment Architecture",
            type=DiagramType.DEPLOYMENT,
            nodes=deployment_nodes,
            relationships=deployment_relationships,
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
            description="Production deployment topology"
        )

        self.templates["deployment"] = deployment_template

    async def create_diagram(
        self,
        name: str,
        diagram_type: DiagramType,
        nodes: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        description: str | None = None
    ) -> ArchitectureDiagram:
        """Create a new architecture diagram."""
        try:
            # Convert dictionaries to Node objects
            node_objects = [
                Node(
                    id=node["id"],
                    name=node["name"],
                    type=NodeType(node["type"]),
                    x=float(node["x"]),
                    y=float(node["y"]),
                    width=float(node.get("width", 120)),
                    height=float(node.get("height", 80)),
                    status=node.get("status", "active"),
                    metadata=node.get("metadata", {})
                )
                for node in nodes
            ]

            # Convert dictionaries to Relationship objects
            relationship_objects = [
                Relationship(
                    id=rel["id"],
                    source_id=rel["source_id"],
                    target_id=rel["target_id"],
                    type=RelationshipType(rel["type"]),
                    label=rel.get("label"),
                    status=rel.get("status", "active"),
                    metadata=rel.get("metadata", {})
                )
                for rel in relationships
            ]

            diagram_id = f"diagram_{datetime.now().timestamp()}_{hash(name) % 10000}"

            diagram = ArchitectureDiagram(
                id=diagram_id,
                name=name,
                type=diagram_type,
                nodes=node_objects,
                relationships=relationship_objects,
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat(),
                description=description
            )

            self.diagrams[diagram_id] = diagram

            logger.info(f"Created architecture diagram: {name}", diagram_id=diagram_id)
            return diagram

        except Exception as e:
            logger.error("Failed to create diagram", error=str(e))
            raise

    async def get_diagram(self, diagram_id: str) -> ArchitectureDiagram | None:
        """Get a diagram by ID."""
        return self.diagrams.get(diagram_id)

    async def list_diagrams(self, diagram_type: DiagramType | None = None) -> list[ArchitectureDiagram]:
        """List all diagrams, optionally filtered by type."""
        diagrams = list(self.diagrams.values())

        if diagram_type:
            diagrams = [d for d in diagrams if d.type == diagram_type]

        return sorted(diagrams, key=lambda d: d.created_at, reverse=True)

    async def update_diagram(
        self,
        diagram_id: str,
        name: str | None = None,
        nodes: list[dict[str, Any]] | None = None,
        relationships: list[dict[str, Any]] | None = None,
        description: str | None = None
    ) -> ArchitectureDiagram | None:
        """Update an existing diagram."""
        diagram = self.diagrams.get(diagram_id)
        if not diagram:
            return None

        try:
            if name:
                diagram.name = name

            if nodes is not None:
                diagram.nodes = [
                    Node(
                        id=node["id"],
                        name=node["name"],
                        type=NodeType(node["type"]),
                        x=float(node["x"]),
                        y=float(node["y"]),
                        width=float(node.get("width", 120)),
                        height=float(node.get("height", 80)),
                        status=node.get("status", "active"),
                        metadata=node.get("metadata", {})
                    )
                    for node in nodes
                ]

            if relationships is not None:
                diagram.relationships = [
                    Relationship(
                        id=rel["id"],
                        source_id=rel["source_id"],
                        target_id=rel["target_id"],
                        type=RelationshipType(rel["type"]),
                        label=rel.get("label"),
                        status=rel.get("status", "active"),
                        metadata=rel.get("metadata", {})
                    )
                    for rel in relationships
                ]

            if description:
                diagram.description = description

            diagram.updated_at = datetime.now(UTC).isoformat()
            diagram.version += 1

            logger.info(f"Updated architecture diagram: {diagram.name}", diagram_id=diagram_id)
            return diagram

        except Exception as e:
            logger.error("Failed to update diagram", error=str(e), diagram_id=diagram_id)
            raise

    async def delete_diagram(self, diagram_id: str) -> bool:
        """Delete a diagram."""
        if diagram_id in self.diagrams:
            del self.diagrams[diagram_id]
            logger.info("Deleted architecture diagram", diagram_id=diagram_id)
            return True
        return False

    async def get_template(self, template_name: str) -> ArchitectureDiagram | None:
        """Get a template diagram."""
        return self.templates.get(template_name)

    async def list_templates(self) -> list[ArchitectureDiagram]:
        """List all available templates."""
        return list(self.templates.values())

    async def generate_system_diagram(self, system_info: dict[str, Any]) -> ArchitectureDiagram:
        """Generate a system architecture diagram from system information."""
        try:
            # Extract services from system info
            services = system_info.get("services", [])
            databases = system_info.get("databases", [])
            caches = system_info.get("caches", [])

            nodes = []
            relationships = []

            # Create service nodes
            for i, service in enumerate(services):
                node = Node(
                    id=f"service-{service['name'].lower().replace(' ', '-')}",
                    name=service["name"],
                    type=NodeType.SERVICE,
                    x=200 + (i * 150),
                    y=100,
                    metadata={
                        "version": service.get("version", "latest"),
                        "status": service.get("status", "active")
                    }
                )
                nodes.append(node)

            # Create database nodes
            for i, db in enumerate(databases):
                node = Node(
                    id=f"db-{db['name'].lower().replace(' ', '-')}",
                    name=db["name"],
                    type=NodeType.DATABASE,
                    x=200 + (i * 150),
                    y=300,
                    metadata={
                        "engine": db.get("engine", "postgresql"),
                        "size": db.get("size", "unknown")
                    }
                )
                nodes.append(node)

            # Create cache nodes
            for i, cache in enumerate(caches):
                node = Node(
                    id=f"cache-{cache['name'].lower().replace(' ', '-')}",
                    name=cache["name"],
                    type=NodeType.CACHE,
                    x=600 + (i * 150),
                    y=200,
                    metadata={
                        "type": cache.get("type", "redis"),
                        "size": cache.get("size", "unknown")
                    }
                )
                nodes.append(node)

            # Create relationships (simple service->database connections)
            for service_node in [n for n in nodes if n.type == NodeType.SERVICE]:
                for db_node in [n for n in nodes if n.type == NodeType.DATABASE]:
                    relationship = Relationship(
                        id=f"{service_node.id}-to-{db_node.id}",
                        source_id=service_node.id,
                        target_id=db_node.id,
                        type=RelationshipType.STORES_IN
                    )
                    relationships.append(relationship)

            diagram = ArchitectureDiagram(
                id=f"auto-generated-{datetime.now().timestamp()}",
                name="Auto-Generated System Diagram",
                type=DiagramType.SYSTEM_OVERVIEW,
                nodes=nodes,
                relationships=relationships,
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat(),
                description="Automatically generated from system information"
            )

            self.diagrams[diagram.id] = diagram
            logger.info("Generated system architecture diagram", diagram_id=diagram.id)
            return diagram

        except Exception as e:
            logger.error("Failed to generate system diagram", error=str(e))
            raise

    async def export_diagram(self, diagram_id: str, format: str = "json") -> str | bytes:
        """Export diagram in specified format."""
        diagram = await self.get_diagram(diagram_id)
        if not diagram:
            raise ValueError(f"Diagram {diagram_id} not found")

        if format.lower() == "json":
            return json.dumps(asdict(diagram), indent=2)
        elif format.lower() == "mermaid":
            return self._to_mermaid(diagram)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _to_mermaid(self, diagram: ArchitectureDiagram) -> str:
        """Convert diagram to Mermaid format."""
        lines = ["graph TD"]

        # Add nodes
        for node in diagram.nodes:
            node_type = node.type.value.replace("_", " ").title()
            lines.append(f"    {node.id}[\"{node.name}<br/>({node_type})\"]")

        # Add relationships
        for rel in diagram.relationships:
            arrow = "-->"
            if rel.type == RelationshipType.DEPENDS_ON:
                arrow = "-.->"
            elif rel.type == RelationshipType.CACHES:
                arrow = "==>"

            label = f"|{rel.label}|" if rel.label else ""
            lines.append(f"    {rel.source_id} {arrow} {label} {rel.target_id}")

        return "\n".join(lines)


# Global service instance
architecture_service = ArchitectureVisualizationService()
