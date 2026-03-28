"""
Architecture Visualization API Routes

Provides REST endpoints for managing architecture diagrams and visualizations.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.architecture_service import DiagramType, NodeType, RelationshipType, architecture_service

router = APIRouter(prefix="/architecture", tags=["Architecture Visualization"])
logger = get_logger(__name__)


class NodeCreate(BaseModel):
    """Node creation request model."""
    id: str
    name: str
    type: str
    x: float
    y: float
    width: float | None = 120
    height: float | None = 80
    status: str | None = "active"
    metadata: dict[str, Any] | None = None


class RelationshipCreate(BaseModel):
    """Relationship creation request model."""
    id: str
    source_id: str
    target_id: str
    type: str
    label: str | None = None
    status: str | None = "active"
    metadata: dict[str, Any] | None = None


class DiagramCreate(BaseModel):
    """Diagram creation request model."""
    name: str
    type: str
    nodes: list[NodeCreate]
    relationships: list[RelationshipCreate]
    description: str | None = None


class DiagramUpdate(BaseModel):
    """Diagram update request model."""
    name: str | None = None
    nodes: list[NodeCreate] | None = None
    relationships: list[RelationshipCreate] | None = None
    description: str | None = None


class SystemInfo(BaseModel):
    """System information for auto-generation."""
    services: list[dict[str, Any]]
    databases: list[dict[str, Any]]
    caches: list[dict[str, Any]]
    message_queues: list[dict[str, Any]] | None = None


@router.post("/", response_model=APIResponse)
async def create_diagram(diagram_data: DiagramCreate):
    """
    Create a new architecture diagram.
    
    Args:
        diagram_data: Diagram creation data
        
    Returns:
        APIResponse with created diagram
    """
    try:
        # Convert Pydantic models to dictionaries
        nodes_dict = [node.dict() for node in diagram_data.nodes]
        relationships_dict = [rel.dict() for rel in diagram_data.relationships]

        diagram = await architecture_service.create_diagram(
            name=diagram_data.name,
            diagram_type=DiagramType(diagram_data.type),
            nodes=nodes_dict,
            relationships=relationships_dict,
            description=diagram_data.description
        )

        return APIResponse(
            success=True,
            data=diagram.__dict__,
            message=f"Diagram '{diagram_data.name}' created successfully"
        )
    except Exception as e:
        logger.error("Failed to create diagram", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create diagram: {str(e)}")


@router.get("/", response_model=APIResponse)
async def list_diagrams(diagram_type: str | None = None):
    """
    List all architecture diagrams.
    
    Args:
        diagram_type: Optional filter by diagram type
        
    Returns:
        APIResponse with list of diagrams
    """
    try:
        diagram_type_enum = DiagramType(diagram_type) if diagram_type else None
        diagrams = await architecture_service.list_diagrams(diagram_type_enum)

        diagrams_data = []
        for diagram in diagrams:
            diagram_dict = diagram.__dict__.copy()
            diagram_dict["nodes"] = [node.__dict__ for node in diagram.nodes]
            diagram_dict["relationships"] = [rel.__dict__ for rel in diagram.relationships]
            diagrams_data.append(diagram_dict)

        return APIResponse(
            success=True,
            data=diagrams_data,
            message=f"Retrieved {len(diagrams_data)} diagrams"
        )
    except Exception as e:
        logger.error("Failed to list diagrams", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list diagrams: {str(e)}")


@router.get("/{diagram_id}", response_model=APIResponse)
async def get_diagram(diagram_id: str):
    """
    Get a specific architecture diagram.
    
    Args:
        diagram_id: ID of the diagram to retrieve
        
    Returns:
        APIResponse with diagram data
    """
    try:
        diagram = await architecture_service.get_diagram(diagram_id)

        if not diagram:
            raise HTTPException(status_code=404, detail=f"Diagram {diagram_id} not found")

        diagram_dict = diagram.__dict__.copy()
        diagram_dict["nodes"] = [node.__dict__ for node in diagram.nodes]
        diagram_dict["relationships"] = [rel.__dict__ for rel in diagram.relationships]

        return APIResponse(
            success=True,
            data=diagram_dict,
            message=f"Retrieved diagram '{diagram.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get diagram", error=str(e), diagram_id=diagram_id)
        raise HTTPException(status_code=500, detail=f"Failed to get diagram: {str(e)}")


@router.put("/{diagram_id}", response_model=APIResponse)
async def update_diagram(diagram_id: str, update_data: DiagramUpdate):
    """
    Update an existing architecture diagram.
    
    Args:
        diagram_id: ID of the diagram to update
        update_data: Update data
        
    Returns:
        APIResponse with updated diagram
    """
    try:
        # Convert Pydantic models to dictionaries if provided
        nodes_dict = [node.dict() for node in update_data.nodes] if update_data.nodes else None
        relationships_dict = [rel.dict() for rel in update_data.relationships] if update_data.relationships else None

        diagram = await architecture_service.update_diagram(
            diagram_id=diagram_id,
            name=update_data.name,
            nodes=nodes_dict,
            relationships=relationships_dict,
            description=update_data.description
        )

        if not diagram:
            raise HTTPException(status_code=404, detail=f"Diagram {diagram_id} not found")

        diagram_dict = diagram.__dict__.copy()
        diagram_dict["nodes"] = [node.__dict__ for node in diagram.nodes]
        diagram_dict["relationships"] = [rel.__dict__ for rel in diagram.relationships]

        return APIResponse(
            success=True,
            data=diagram_dict,
            message=f"Diagram '{diagram.name}' updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update diagram", error=str(e), diagram_id=diagram_id)
        raise HTTPException(status_code=500, detail=f"Failed to update diagram: {str(e)}")


@router.delete("/{diagram_id}", response_model=APIResponse)
async def delete_diagram(diagram_id: str):
    """
    Delete an architecture diagram.
    
    Args:
        diagram_id: ID of the diagram to delete
        
    Returns:
        APIResponse confirming deletion
    """
    try:
        success = await architecture_service.delete_diagram(diagram_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Diagram {diagram_id} not found")

        return APIResponse(
            success=True,
            message="Diagram deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete diagram", error=str(e), diagram_id=diagram_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete diagram: {str(e)}")


@router.get("/templates/", response_model=APIResponse)
async def list_templates():
    """
    List all available diagram templates.
    
    Returns:
        APIResponse with list of templates
    """
    try:
        templates = await architecture_service.list_templates()

        templates_data = []
        for template in templates:
            template_dict = template.__dict__.copy()
            template_dict["nodes"] = [node.__dict__ for node in template.nodes]
            template_dict["relationships"] = [rel.__dict__ for rel in template.relationships]
            templates_data.append(template_dict)

        return APIResponse(
            success=True,
            data=templates_data,
            message=f"Retrieved {len(templates_data)} templates"
        )
    except Exception as e:
        logger.error("Failed to list templates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.get("/templates/{template_name}", response_model=APIResponse)
async def get_template(template_name: str):
    """
    Get a specific diagram template.
    
    Args:
        template_name: Name of the template to retrieve
        
    Returns:
        APIResponse with template data
    """
    try:
        template = await architecture_service.get_template(template_name)

        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_name} not found")

        template_dict = template.__dict__.copy()
        template_dict["nodes"] = [node.__dict__ for node in template.nodes]
        template_dict["relationships"] = [rel.__dict__ for rel in template.relationships]

        return APIResponse(
            success=True,
            data=template_dict,
            message=f"Retrieved template '{template.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get template", error=str(e), template_name=template_name)
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.post("/generate", response_model=APIResponse)
async def generate_system_diagram(system_info: SystemInfo):
    """
    Generate an architecture diagram from system information.
    
    Args:
        system_info: System information for diagram generation
        
    Returns:
        APIResponse with generated diagram
    """
    try:
        diagram = await architecture_service.generate_system_diagram(system_info.dict())

        diagram_dict = diagram.__dict__.copy()
        diagram_dict["nodes"] = [node.__dict__ for node in diagram.nodes]
        diagram_dict["relationships"] = [rel.__dict__ for rel in diagram.relationships]

        return APIResponse(
            success=True,
            data=diagram_dict,
            message="System diagram generated successfully"
        )
    except Exception as e:
        logger.error("Failed to generate system diagram", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate system diagram: {str(e)}")


@router.get("/{diagram_id}/export/{format}", response_model=APIResponse)
async def export_diagram(diagram_id: str, format: str):
    """
    Export a diagram in specified format.
    
    Args:
        diagram_id: ID of the diagram to export
        format: Export format (json, mermaid)
        
    Returns:
        APIResponse with exported diagram data
    """
    try:
        exported_data = await architecture_service.export_diagram(diagram_id, format)

        return APIResponse(
            success=True,
            data={"format": format, "content": exported_data},
            message=f"Diagram exported in {format} format"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to export diagram", error=str(e), diagram_id=diagram_id, format=format)
        raise HTTPException(status_code=500, detail=f"Failed to export diagram: {str(e)}")


@router.get("/types/nodes", response_model=APIResponse)
async def get_node_types():
    """
    Get available node types.
    
    Returns:
        APIResponse with list of node types
    """
    try:
        node_types = [{"name": t.name, "value": t.value} for t in NodeType]

        return APIResponse(
            success=True,
            data=node_types,
            message="Retrieved node types"
        )
    except Exception as e:
        logger.error("Failed to get node types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get node types: {str(e)}")


@router.get("/types/relationships", response_model=APIResponse)
async def get_relationship_types():
    """
    Get available relationship types.
    
    Returns:
        APIResponse with list of relationship types
    """
    try:
        relationship_types = [{"name": t.name, "value": t.value} for t in RelationshipType]

        return APIResponse(
            success=True,
            data=relationship_types,
            message="Retrieved relationship types"
        )
    except Exception as e:
        logger.error("Failed to get relationship types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get relationship types: {str(e)}")


@router.get("/types/diagrams", response_model=APIResponse)
async def get_diagram_types():
    """
    Get available diagram types.
    
    Returns:
        APIResponse with list of diagram types
    """
    try:
        diagram_types = [{"name": t.name, "value": t.value} for t in DiagramType]

        return APIResponse(
            success=True,
            data=diagram_types,
            message="Retrieved diagram types"
        )
    except Exception as e:
        logger.error("Failed to get diagram types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get diagram types: {str(e)}")
