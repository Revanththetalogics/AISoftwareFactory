"""
Git File Synchronization API Routes.

Provides RESTful endpoints for Git repository management including
clone, pull, push operations and file management.
"""


from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.git_service import GitService

router = APIRouter(prefix="/git", tags=["Git Operations"])
logger = get_logger(__name__)

# Global Git service instance (in production, use dependency injection)
git_service = GitService()

class CloneRepositoryRequest(BaseModel):
    """Request model for cloning a repository."""
    repo_url: str
    destination_name: str | None = None
    branch: str = "main"

class PushChangesRequest(BaseModel):
    """Request model for pushing changes."""
    commit_message: str = "Auto-commit from ThetaAI"
    branch: str = "main"

class WriteFileRequest(BaseModel):
    """Request model for writing a file."""
    file_path: str
    content: str
    create_parents: bool = True

class RepositoryInfo(BaseModel):
    """Repository information model."""
    name: str
    path: str
    current_branch: str
    remote_url: str | None
    commit_hash: str
    status: str
    local_path: str | None = None
    cloned_at: str | None = None
    last_pulled: str | None = None

@router.post("/clone", response_model=APIResponse)
async def clone_repository(request: CloneRepositoryRequest):
    """
    Clone a Git repository.

    Args:
        request: Clone repository request

    Returns:
        APIResponse with repository information
    """
    try:
        repo_info = await git_service.clone_repository(
            repo_url=request.repo_url,
            destination_name=request.destination_name,
            branch=request.branch
        )

        logger.info(
            "Repository cloned successfully",
            repo_url=request.repo_url,
            local_path=repo_info["local_path"]
        )

        return APIResponse(
            success=True,
            data=repo_info,
            message=f"Repository '{repo_info['name']}' cloned successfully"
        )
    except Exception as e:
        logger.error("Failed to clone repository", error=str(e), repo_url=request.repo_url)
        raise HTTPException(status_code=500, detail=f"Failed to clone repository: {str(e)}")

@router.post("/{repo_name}/pull", response_model=APIResponse)
async def pull_repository(repo_name: str):
    """
    Pull latest changes from a repository.

    Args:
        repo_name: Repository name/directory

    Returns:
        APIResponse with updated repository information
    """
    try:
        repo_path = f"./repositories/{repo_name}"
        repo_info = await git_service.pull_repository(repo_path)

        logger.info("Repository pulled successfully", repo_name=repo_name)

        return APIResponse(
            success=True,
            data=repo_info,
            message=f"Repository '{repo_name}' pulled successfully"
        )
    except Exception as e:
        logger.error("Failed to pull repository", error=str(e), repo_name=repo_name)
        raise HTTPException(status_code=500, detail=f"Failed to pull repository: {str(e)}")

@router.post("/{repo_name}/push", response_model=APIResponse)
async def push_changes(repo_name: str, request: PushChangesRequest):
    """
    Push changes to remote repository.

    Args:
        repo_name: Repository name/directory
        request: Push changes request

    Returns:
        APIResponse with push result
    """
    try:
        repo_path = f"./repositories/{repo_name}"
        result = await git_service.push_changes(
            repo_path=repo_path,
            commit_message=request.commit_message,
            branch=request.branch
        )

        logger.info("Changes pushed successfully", repo_name=repo_name)

        return APIResponse(
            success=True,
            data=result,
            message=f"Changes pushed to '{repo_name}' successfully"
        )
    except Exception as e:
        logger.error("Failed to push changes", error=str(e), repo_name=repo_name)
        raise HTTPException(status_code=500, detail=f"Failed to push changes: {str(e)}")

@router.get("/{repo_name}/files", response_model=APIResponse)
async def list_files(
    repo_name: str,
    path: str = Query(".", description="Relative path within repository")
):
    """
    List files in a repository directory.

    Args:
        repo_name: Repository name/directory
        path: Relative path within repository

    Returns:
        APIResponse with file list
    """
    try:
        repo_path = f"./repositories/{repo_name}"
        files = await git_service.list_files(repo_path, path)

        return APIResponse(
            success=True,
            data={
                "files": files,
                "repository": repo_name,
                "path": path
            },
            message=f"Listed {len(files)} files in '{path}'"
        )
    except Exception as e:
        logger.error("Failed to list files", error=str(e), repo_name=repo_name, path=path)
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.get("/{repo_name}/files/{file_path:path}", response_model=APIResponse)
async def read_file(repo_name: str, file_path: str):
    """
    Read file content from repository.

    Args:
        repo_name: Repository name/directory
        file_path: Path to file within repository

    Returns:
        APIResponse with file content
    """
    try:
        repo_path = f"./repositories/{repo_name}"
        file_data = await git_service.read_file(repo_path, file_path)

        return APIResponse(
            success=True,
            data=file_data,
            message=f"File '{file_path}' read successfully"
        )
    except Exception as e:
        logger.error("Failed to read file", error=str(e), repo_name=repo_name, file_path=file_path)
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

@router.post("/{repo_name}/files/{file_path:path}", response_model=APIResponse)
async def write_file(repo_name: str, file_path: str, request: WriteFileRequest):
    """
    Write file content to repository.

    Args:
        repo_name: Repository name/directory
        file_path: Path to file within repository
        request: Write file request

    Returns:
        APIResponse confirming write operation
    """
    try:
        repo_path = f"./repositories/{repo_name}"
        result = await git_service.write_file(
            repo_path=repo_path,
            file_path=file_path,
            content=request.content,
            create_parents=request.create_parents
        )

        logger.info("File written successfully", repo_name=repo_name, file_path=file_path)

        return APIResponse(
            success=True,
            data=result,
            message=f"File '{file_path}' written successfully"
        )
    except Exception as e:
        logger.error("Failed to write file", error=str(e), repo_name=repo_name, file_path=file_path)
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")

@router.delete("/{repo_name}/files/{file_path:path}", response_model=APIResponse)
async def delete_file(repo_name: str, file_path: str):
    """
    Delete file from repository.

    Args:
        repo_name: Repository name/directory
        file_path: Path to file within repository

    Returns:
        APIResponse confirming delete operation
    """
    try:
        repo_path = f"./repositories/{repo_name}"
        result = await git_service.delete_file(repo_path, file_path)

        logger.info("File deleted successfully", repo_name=repo_name, file_path=file_path)

        return APIResponse(
            success=True,
            data=result,
            message=f"File '{file_path}' deleted successfully"
        )
    except Exception as e:
        logger.error("Failed to delete file", error=str(e), repo_name=repo_name, file_path=file_path)
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/repositories", response_model=APIResponse)
async def list_repositories():
    """
    List all cloned repositories.

    Returns:
        APIResponse with repository list
    """
    try:
        import os
        repos_dir = "./repositories"
        repositories = []

        if os.path.exists(repos_dir):
            for item in os.listdir(repos_dir):
                item_path = os.path.join(repos_dir, item)
                if os.path.isdir(item_path):
                    # Try to get basic repo info
                    try:
                        repo_info = await git_service._get_repo_info(item_path)
                        repositories.append(repo_info)
                    except Exception:
                        # If we can't get repo info, create basic entry
                        repositories.append({
                            "name": item,
                            "path": item_path,
                            "current_branch": "unknown",
                            "remote_url": None,
                            "commit_hash": "unknown",
                            "status": "unknown"
                        })

        return APIResponse(
            success=True,
            data={
                "repositories": repositories,
                "count": len(repositories)
            },
            message=f"Found {len(repositories)} repositories"
        )
    except Exception as e:
        logger.error("Failed to list repositories", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list repositories: {str(e)}")
