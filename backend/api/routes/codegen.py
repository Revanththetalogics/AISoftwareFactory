"""
Code Generation API Routes.

This module provides REST API endpoints for AI-powered code generation
using the LLM system. It includes endpoints for generating code,
validating generated code, and managing generation sessions.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# from backend.api.dependencies import get_current_user  # Temporarily disabled for testing
from backend.core.logging import get_logger
from backend.llm.router import get_llm_router

logger = get_logger(__name__)
router = APIRouter(prefix="/codegen", tags=["code-generation"])

# Create a mock user for development
class MockUser:
    def __init__(self):
        self.id = "test_user"
        self.username = "test"
        self.email = "test@example.com"

def get_current_user():
    """Mock authentication for development."""
    return MockUser()

# Request/Response Models
class CodeGenerationRequest(BaseModel):
    """Request model for code generation."""
    prompt: str = Field(..., min_length=10, description="Description of code to generate")
    language: str = Field("python", description="Target programming language")
    framework: str | None = Field(None, description="Framework/library to use")
    project_id: str | None = Field(None, description="Associated project ID")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")

class CodeGenerationResponse(BaseModel):
    """Response model for code generation."""
    generation_id: str
    code: str
    language: str
    files: list[dict[str, str]] = Field(default_factory=list)
    quality_score: float | None = None
    warnings: list[str] = Field(default_factory=list)
    execution_time_ms: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class CodeValidationRequest(BaseModel):
    """Request model for code validation."""
    code: str = Field(..., description="Code to validate")
    language: str = Field(..., description="Programming language of the code")
    requirements: list[str] = Field(default_factory=list, description="Validation requirements")

class CodeValidationResponse(BaseModel):
    """Response model for code validation."""
    is_valid: bool
    issues: list[dict[str, Any]]
    suggestions: list[str]
    quality_score: float
    complexity_score: float

class GenerationHistoryResponse(BaseModel):
    """Response model for generation history."""
    generations: list[CodeGenerationResponse]
    total_count: int

# Endpoints
@router.post(
    "/generate",
    response_model=CodeGenerationResponse,
    summary="Generate code from prompt",
    description="Generate code using AI based on natural language description"
)
async def generate_code(
    request: CodeGenerationRequest,
    # user=Depends(get_current_user)  # Temporarily disabled for testing
) -> CodeGenerationResponse:
    """
    Generate code from a natural language prompt.
    
    This endpoint uses the LLM system to generate code based on the provided
    description. It supports multiple programming languages and can incorporate
    framework-specific patterns.
    
    Example:
        >>> {
        ...     "prompt": "Create a FastAPI endpoint for user authentication",
        ...     "language": "python",
        ...     "framework": "fastapi"
        ... }
    """
    start_time = datetime.now(UTC)

    try:
        # Get LLM router
        llm_router = get_llm_router()

        # Prepare the prompt for code generation
        system_prompt = f"""You are an expert {request.language} developer.
Generate clean, efficient, well-documented code based on the following requirements.
Use best practices and follow {request.framework or request.language} conventions.
Return only the code without any explanations."""

        full_prompt = f"{system_prompt}\n\nRequirements: {request.prompt}"

        # Generate code using LLM
        from backend.llm.providers.base import LLMRequest

        llm_request = LLMRequest(
            prompt=full_prompt,
            model="deepseek-coder-v2",  # Use code-specialized model
            max_tokens=2048,
            temperature=0.2,  # Lower temperature for more deterministic code
        )

        llm_response = await llm_router.generate(llm_request)

        if not llm_response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Code generation failed: {llm_response.error}"
            )

        generated_code = llm_response.text.strip()

        # Validate the generated code (basic validation)
        validation_result = await validate_generated_code(generated_code, request.language)

        # Calculate execution time
        execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

        response = CodeGenerationResponse(
            generation_id=f"gen_{datetime.now(UTC).timestamp()}",
            code=generated_code,
            language=request.language,
            files=[{"filename": f"generated_code.{get_file_extension(request.language)}", "content": generated_code}],
            quality_score=validation_result.quality_score if validation_result else None,
            warnings=validation_result.issues if validation_result else [],
            execution_time_ms=execution_time,
        )

        logger.info(
            "Code generation completed",
            user_id=user.id,
            language=request.language,
            execution_time_ms=execution_time
        )

        return response

    except Exception as e:
        logger.error("Code generation failed", error=str(e), user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate code: {str(e)}"
        )

@router.post(
    "/validate",
    response_model=CodeValidationResponse,
    summary="Validate generated code",
    description="Validate code for syntax, best practices, and quality"
)
async def validate_code(
    request: CodeValidationRequest,
    # user=Depends(get_current_user)  # Temporarily disabled for testing
) -> CodeValidationResponse:
    """
    Validate generated code for quality and correctness.
    
    This endpoint performs static analysis on the provided code to check
    for syntax errors, best practices violations, and code quality issues.
    """
    return await validate_generated_code(request.code, request.language)

@router.get(
    "/history",
    response_model=GenerationHistoryResponse,
    summary="Get generation history",
    description="Retrieve history of code generation requests"
)
async def get_generation_history(
    # user=Depends(get_current_user),  # Temporarily disabled for testing
    limit: int = 50,
    offset: int = 0
) -> GenerationHistoryResponse:
    """
    Get history of code generation requests for the current user.
    
    Returns paginated list of previous generation requests with their results.
    """
    # TODO: Implement actual history storage
    # This would typically query a database of generation records
    return GenerationHistoryResponse(
        generations=[],
        total_count=0
    )

@router.get(
    "/languages",
    summary="Get supported languages",
    description="Get list of supported programming languages"
)
async def get_supported_languages(
    # user=Depends(get_current_user)  # Temporarily disabled for testing
) -> dict[str, Any]:
    """
    Get list of programming languages supported for code generation.
    
    Returns available languages with their capabilities and framework support.
    """
    languages = {
        "python": {
            "name": "Python",
            "frameworks": ["fastapi", "django", "flask", "streamlit"],
            "extensions": [".py"]
        },
        "javascript": {
            "name": "JavaScript",
            "frameworks": ["react", "vue", "angular", "nextjs", "express"],
            "extensions": [".js", ".jsx"]
        },
        "typescript": {
            "name": "TypeScript",
            "frameworks": ["react", "vue", "angular", "nextjs", "nestjs"],
            "extensions": [".ts", ".tsx"]
        },
        "java": {
            "name": "Java",
            "frameworks": ["spring-boot", "quarkus", "micronaut"],
            "extensions": [".java"]
        },
        "go": {
            "name": "Go",
            "frameworks": ["gin", "echo", "fiber"],
            "extensions": [".go"]
        }
    }

    return {"supported_languages": languages}

# Helper functions
async def validate_generated_code(code: str, language: str) -> CodeValidationResponse:
    """Validate generated code and return quality metrics."""
    issues = []
    suggestions = []

    # Basic validation based on language
    if language.lower() == "python":
        # Check for common Python issues
        if "import" not in code:
            suggestions.append("Consider adding import statements for required modules")

        if "def " not in code and "class " not in code:
            issues.append({"type": "structure", "message": "No functions or classes defined"})
            suggestions.append("Define functions or classes to encapsulate functionality")

        # Check for basic syntax (simplified)
        if code.count("(") != code.count(")"):
            issues.append({"type": "syntax", "message": "Mismatched parentheses"})

    elif language.lower() in ["javascript", "typescript"]:
        if "function" not in code and "=>" not in code and "class" not in code:
            issues.append({"type": "structure", "message": "No functions or classes defined"})

    # Calculate quality score (simplified)
    quality_score = 1.0 - (len(issues) * 0.1)
    quality_score = max(0.0, quality_score)

    # Complexity estimation (very simplified)
    complexity_score = min(1.0, len(code.split('\n')) / 100.0)

    return CodeValidationResponse(
        is_valid=len(issues) == 0,
        issues=issues,
        suggestions=suggestions,
        quality_score=quality_score,
        complexity_score=complexity_score
    )

def get_file_extension(language: str) -> str:
    """Get appropriate file extension for a programming language."""
    extensions = {
        "python": "py",
        "javascript": "js",
        "typescript": "ts",
        "java": "java",
        "go": "go",
        "rust": "rs",
        "cpp": "cpp",
        "c": "c"
    }
    return extensions.get(language.lower(), "txt")
