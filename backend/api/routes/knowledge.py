"""
Knowledge Base API Routes.

Provides RESTful endpoints for knowledge base management including
CRUD operations for documents and search functionality.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.brain.knowledge_base import KnowledgeBase
from backend.core.logging import get_logger

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])
logger = get_logger(__name__)

# Global knowledge base instance (in production, use dependency injection)
knowledge_base = KnowledgeBase("main_kb")


class DocumentCreateRequest(BaseModel):
    """Request model for creating a document."""

    content: str
    title: str
    tags: list[str] | None = None
    source: str | None = None
    metadata: dict[str, Any] | None = None


class DocumentUpdateRequest(BaseModel):
    """Request model for updating a document."""

    content: str | None = None
    title: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class SearchRequest(BaseModel):
    """Request model for searching documents."""

    query: str
    top_k: int = 5
    filter_tags: list[str] | None = None


class DocumentResponse(BaseModel):
    """Response model for document operations."""

    id: str
    title: str
    content_preview: str
    tags: list[str]
    source: str | None
    created_at: str
    updated_at: str | None
    chunk_count: int


@router.get("/stats", response_model=APIResponse)
async def get_knowledge_stats():
    """
    Get knowledge base statistics.

    Returns:
        APIResponse containing knowledge base stats
    """
    try:
        stats = knowledge_base.get_stats()
        return APIResponse(success=True, data=stats, message="Knowledge base statistics retrieved successfully")
    except Exception as e:
        logger.error("Failed to get knowledge stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.post("/documents", response_model=APIResponse)
async def add_document(request: DocumentCreateRequest):
    """
    Add a new document to the knowledge base.

    Args:
        request: Document creation request

    Returns:
        APIResponse with document ID
    """
    try:
        # Prepare metadata
        metadata = request.metadata or {}
        metadata.update({"title": request.title, "tags": request.tags or [], "source": request.source})

        # Add document to knowledge base
        doc_id = await knowledge_base.add_document(content=request.content, metadata=metadata)

        logger.info("Document added successfully", doc_id=doc_id, title=request.title)

        return APIResponse(
            success=True, data={"document_id": doc_id}, message=f"Document '{request.title}' added successfully"
        )
    except Exception as e:
        logger.error("Failed to add document", error=str(e), title=request.title)
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


@router.get("/documents/{doc_id}", response_model=APIResponse)
async def get_document(doc_id: str):
    """
    Get a specific document by ID.

    Args:
        doc_id: Document ID

    Returns:
        APIResponse with document data
    """
    try:
        # This would require storing full documents separately
        # For now, return basic info from stored metadata
        if doc_id in knowledge_base._documents:
            doc_data = knowledge_base._documents[doc_id]
            # In a real implementation, you'd fetch the full content
            # This is a simplified version
            response_data = {
                "id": doc_id,
                "title": doc_data["metadata"].get("title", "Untitled"),
                "content_preview": f"[Content preview not implemented - document has {doc_data['chunk_count']} chunks]",
                "tags": doc_data["metadata"].get("tags", []),
                "source": doc_data["metadata"].get("source"),
                "created_at": doc_data["created_at"],
                "chunk_count": doc_data["chunk_count"],
            }

            return APIResponse(success=True, data=response_data, message="Document retrieved successfully")
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get document", error=str(e), doc_id=doc_id)
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.put("/documents/{doc_id}", response_model=APIResponse)
async def update_document(doc_id: str, request: DocumentUpdateRequest):
    """
    Update an existing document.

    Args:
        doc_id: Document ID
        request: Update request data

    Returns:
        APIResponse confirming update
    """
    try:
        # Check if document exists
        if doc_id not in knowledge_base._documents:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete existing document
        await knowledge_base.delete_document(doc_id)

        # Add updated document
        existing_doc = knowledge_base._documents.get(doc_id, {})
        metadata = existing_doc.get("metadata", {})

        # Update metadata with new values
        if request.title is not None:
            metadata["title"] = request.title
        if request.tags is not None:
            metadata["tags"] = request.tags
        if request.metadata is not None:
            metadata.update(request.metadata)

        # Use existing content if not provided
        content = request.content or "[Content update not implemented in this version]"

        new_doc_id = await knowledge_base.add_document(
            content=content,
            metadata=metadata,
            doc_id=doc_id,  # Reuse same ID
        )

        logger.info("Document updated successfully", doc_id=doc_id)

        return APIResponse(success=True, data={"document_id": new_doc_id}, message="Document updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update document", error=str(e), doc_id=doc_id)
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")


@router.delete("/documents/{doc_id}", response_model=APIResponse)
async def delete_document(doc_id: str):
    """
    Delete a document from the knowledge base.

    Args:
        doc_id: Document ID

    Returns:
        APIResponse confirming deletion
    """
    try:
        success = await knowledge_base.delete_document(doc_id)
        if success:
            logger.info("Document deleted successfully", doc_id=doc_id)
            return APIResponse(success=True, message="Document deleted successfully")
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete document", error=str(e), doc_id=doc_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.post("/search", response_model=APIResponse)
async def search_documents(request: SearchRequest):
    """
    Search documents in the knowledge base.

    Args:
        request: Search request with query and parameters

    Returns:
        APIResponse with search results
    """
    try:
        # Prepare filter metadata if tags are specified
        filter_metadata = None
        if request.filter_tags:
            filter_metadata = {"tags": {"$in": request.filter_tags}}

        # Perform search
        results = await knowledge_base.search(query=request.query, top_k=request.top_k, filter_metadata=filter_metadata)

        # Format results for response
        formatted_results = []
        for result in results:
            # Extract document info from metadata
            metadata = result.get("metadata", {})
            formatted_results.append(
                {
                    "id": metadata.get("doc_id", "unknown"),
                    "score": result.get("score", 0),
                    "content": result.get("text", "")[:200] + "..."
                    if len(result.get("text", "")) > 200
                    else result.get("text", ""),
                    "title": metadata.get("title", "Untitled"),
                    "tags": metadata.get("tags", []),
                }
            )

        logger.info("Search completed", query=request.query, results_count=len(formatted_results))

        return APIResponse(
            success=True,
            data={"results": formatted_results, "total_results": len(formatted_results), "query": request.query},
            message=f"Found {len(formatted_results)} results for query: {request.query}",
        )
    except Exception as e:
        logger.error("Search failed", error=str(e), query=request.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/documents", response_model=APIResponse)
async def list_documents(
    skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), tags: str | None = Query(None)
):
    """
    List all documents in the knowledge base.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        tags: Comma-separated tags to filter by

    Returns:
        APIResponse with list of documents
    """
    try:
        # Convert tags string to list if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]

        # Get all documents and apply filters
        all_docs = []
        for doc_id, doc_data in knowledge_base._documents.items():
            # Apply tag filter if specified
            if tag_list:
                doc_tags = doc_data["metadata"].get("tags", [])
                if not any(tag in doc_tags for tag in tag_list):
                    continue

            all_docs.append(
                {
                    "id": doc_id,
                    "title": doc_data["metadata"].get("title", "Untitled"),
                    "tags": doc_data["metadata"].get("tags", []),
                    "source": doc_data["metadata"].get("source"),
                    "created_at": doc_data["created_at"],
                    "chunk_count": doc_data["chunk_count"],
                }
            )

        # Apply pagination
        paginated_docs = all_docs[skip : skip + limit]

        logger.info("Documents listed", count=len(paginated_docs), total=len(all_docs))

        return APIResponse(
            success=True,
            data={"documents": paginated_docs, "total_count": len(all_docs), "skip": skip, "limit": limit},
            message=f"Retrieved {len(paginated_docs)} documents",
        )
    except Exception as e:
        logger.error("Failed to list documents", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")
