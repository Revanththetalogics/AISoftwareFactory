"""
Code Generator for AI Software Factory.

This module provides the code generation engine with templates for
various programming languages and frameworks.
"""

from dataclasses import dataclass, field
from enum import Enum
from string import Template
from typing import Any, Dict, List, Optional

from backend.core.logging import get_logger

logger = get_logger(__name__)


class CodeLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    DOCKERFILE = "dockerfile"
    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"


class CodeFramework(str, Enum):
    """Supported frameworks."""
    FASTAPI = "fastapi"
    REACT = "react"
    NEXTJS = "nextjs"
    DJANGO = "django"
    FLASK = "flask"
    EXPRESS = "express"


@dataclass
class GeneratedCode:
    """
    Result of code generation.

    Attributes:
        content: Generated code content
        language: Programming language
        framework: Framework used (if any)
        file_path: Suggested file path
        metadata: Additional metadata
        error: Error message if generation failed
    """
    content: str = ""
    language: CodeLanguage = CodeLanguage.PYTHON
    framework: Optional[CodeFramework] = None
    file_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if generation was successful."""
        return self.error is None and len(self.content) > 0


@dataclass
class CodeTemplate:
    """
    Template for code generation.

    Attributes:
        name: Template name
        template: Template string
        language: Target language
        framework: Target framework (optional)
        description: Template description
        variables: Required template variables
    """
    name: str
    template: str
    language: CodeLanguage
    framework: Optional[CodeFramework] = None
    description: str = ""
    variables: List[str] = field(default_factory=list)

    def render(self, **kwargs) -> str:
        """Render the template with variables."""
        try:
            t = Template(self.template)
            return t.substitute(**kwargs)
        except KeyError as exc:
            missing_var = str(exc).strip("'")
            raise ValueError(f"Missing required variable: {missing_var}")


class CodeGenerator:
    """
    Code generation engine for AI Software Factory.

    This class provides:
    - Multi-language code generation
    - Framework-specific templates
    - Code validation and formatting
    - Template management

    Example:
        >>> generator = CodeGenerator()
        >>> code = generator.generate(
        ...     template_name="fastapi_endpoint",
        ...     variables={"endpoint_name": "users", "model": "User"}
        ... )
    """

    def __init__(self):
        """Initialize the code generator."""
        self._templates: Dict[str, CodeTemplate] = {}
        self._logger = get_logger(__name__)

        # Initialize default templates
        self._init_default_templates()

    def _init_default_templates(self) -> None:
        """Initialize default code templates."""
        templates = [
            # FastAPI templates
            CodeTemplate(
                name="fastapi_endpoint",
                template='''@router.$method("$path")
async def $endpoint_name($parameters):
    """
    $description
    """
    try:
        $implementation
        return $return_value
    except Exception as exc:
        logger.error("Error in $endpoint_name", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
''',
                language=CodeLanguage.PYTHON,
                framework=CodeFramework.FASTAPI,
                description="FastAPI endpoint handler",
                variables=["method", "path", "endpoint_name", "parameters",
                          "description", "implementation", "return_value"],
            ),

            CodeTemplate(
                name="fastapi_model",
                template='''from pydantic import BaseModel, Field
from typing import Optional

class $model_name(BaseModel):
    """
    $description
    """
    $fields

    class Config:
        json_schema_extra = {
            "example": $example
        }
''',
                language=CodeLanguage.PYTHON,
                framework=CodeFramework.FASTAPI,
                description="Pydantic model for FastAPI",
                variables=["model_name", "description", "fields", "example"],
            ),

            # React component templates
            CodeTemplate(
                name="react_component",
                template='''import React from 'react';

interface $component_name$props_interface {
    $props
}

export const $component_name: React.FC<$component_name$props_interface> = ({ $prop_names }) => {
    return (
        $jsx_content
    );
};
''',
                language=CodeLanguage.TYPESCRIPT,
                framework=CodeFramework.REACT,
                description="React functional component",
                variables=["component_name", "props_interface", "props",
                          "prop_names", "jsx_content"],
            ),

            # Database templates
            CodeTemplate(
                name="sql_table",
                template='''CREATE TABLE $table_name (
    id SERIAL PRIMARY KEY,
    $columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

$indexes
''',
                language=CodeLanguage.SQL,
                description="SQL table creation",
                variables=["table_name", "columns", "indexes"],
            ),

            # Docker templates
            CodeTemplate(
                name="dockerfile_python",
                template='''FROM python:$python_version-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $port

CMD ["$command"]
''',
                language=CodeLanguage.DOCKERFILE,
                description="Dockerfile for Python app",
                variables=["python_version", "port", "command"],
            ),

            # Test templates
            CodeTemplate(
                name="pytest_test",
                template='''import pytest

class Test$class_name:
    """Test cases for $class_name."""

    def test_$test_name(self):
        """Test $test_description."""
        # Arrange
        $arrange

        # Act
        $act

        # Assert
        $assert
''',
                language=CodeLanguage.PYTHON,
                description="Pytest test class",
                variables=["class_name", "test_name", "test_description",
                          "arrange", "act", "assert"],
            ),

            # Configuration templates
            CodeTemplate(
                name="docker_compose",
                template='''version: '3.8'

services:
  $service_name:
    build: .
    ports:
      - "$host_port:$container_port"
    environment:
      $environment_vars
    depends_on:
      $dependencies
    volumes:
      $volumes

  $db_service:
    image: postgres:$postgres_version
    environment:
      POSTGRES_DB: $db_name
      POSTGRES_USER: $db_user
      POSTGRES_PASSWORD: $db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "$db_port:5432"

volumes:
  postgres_data:
''',
                language=CodeLanguage.YAML,
                description="Docker Compose configuration",
                variables=["service_name", "host_port", "container_port",
                          "environment_vars", "dependencies", "volumes",
                          "db_service", "postgres_version", "db_name",
                          "db_user", "db_password", "db_port"],
            ),
        ]

        for template in templates:
            self._templates[template.name] = template

        self._logger.info("Default templates initialized", count=len(templates))

    def register_template(self, template: CodeTemplate) -> None:
        """
        Register a code template.

        Args:
            template: Template to register
        """
        self._templates[template.name] = template
        self._logger.info("Template registered", template=template.name)

    def get_template(self, name: str) -> Optional[CodeTemplate]:
        """Get a template by name."""
        return self._templates.get(name)

    def generate(
        self,
        template_name: str,
        variables: Dict[str, str],
        file_path: str = "",
    ) -> GeneratedCode:
        """
        Generate code from a template.

        Args:
            template_name: Name of the template
            variables: Variables for template substitution
            file_path: Suggested file path

        Returns:
            GeneratedCode with content or error

        Example:
            >>> generator = CodeGenerator()
            >>> result = generator.generate(
            ...     "fastapi_endpoint",
            ...     {
            ...         "method": "get",
            ...         "path": "/users",
            ...         "endpoint_name": "get_users",
            ...         "parameters": "",
            ...         "description": "Get all users",
            ...         "implementation": "users = await get_users()",
            ...         "return_value": "users",
            ...     }
            ... )
        """
        template = self._templates.get(template_name)
        if not template:
            return GeneratedCode(
                error=f"Template '{template_name}' not found"
            )

        try:
            content = template.render(**variables)

            self._logger.info(
                "Code generated",
                template=template_name,
                language=template.language.value,
            )

            return GeneratedCode(
                content=content,
                language=template.language,
                framework=template.framework,
                file_path=file_path,
            )

        except ValueError as exc:
            self._logger.error(
                "Template rendering failed",
                template=template_name,
                error=str(exc),
            )
            return GeneratedCode(error=str(exc))
        except Exception as exc:
            self._logger.error(
                "Code generation failed",
                template=template_name,
                error=str(exc),
            )
            return GeneratedCode(error=str(exc))

    def generate_from_description(
        self,
        description: str,
        language: CodeLanguage,
        framework: Optional[CodeFramework] = None,
    ) -> GeneratedCode:
        """
        Generate code from a natural language description.

        This is a stub for future LLM integration. Currently returns
        a placeholder.

        Args:
            description: Natural language description
            language: Target language
            framework: Target framework (optional)

        Returns:
            GeneratedCode
        """
        # This would integrate with LLM in full implementation
        self._logger.info(
            "Code generation from description requested",
            language=language.value,
            description_length=len(description),
        )

        return GeneratedCode(
            content=f"# TODO: Implement based on description\n# {description[:100]}...",
            language=language,
            framework=framework,
            metadata={"source": "description", "description": description},
        )

    def list_templates(
        self,
        language: Optional[CodeLanguage] = None,
        framework: Optional[CodeFramework] = None,
    ) -> List[str]:
        """
        List available templates.

        Args:
            language: Filter by language
            framework: Filter by framework

        Returns:
            List of template names
        """
        templates = []
        for name, template in self._templates.items():
            if language and template.language != language:
                continue
            if framework and template.framework != framework:
                continue
            templates.append(name)
        return templates

    def validate_code(self, code: str, language: CodeLanguage) -> Dict[str, Any]:
        """
        Validate code syntax (basic checks).

        Args:
            code: Code to validate
            language: Programming language

        Returns:
            Validation results
        """
        issues = []

        if language == CodeLanguage.PYTHON:
            # Basic Python syntax check
            try:
                compile(code, "<string>", "exec")
            except SyntaxError as exc:
                issues.append({
                    "type": "syntax_error",
                    "message": str(exc),
                    "line": exc.lineno,
                })

        elif language == CodeLanguage.JSON:
            import json
            try:
                json.loads(code)
            except json.JSONDecodeError as exc:
                issues.append({
                    "type": "json_error",
                    "message": str(exc),
                })

        # Check for common issues
        if not code.strip():
            issues.append({"type": "empty", "message": "Code is empty"})

        if len(code) > 100000:
            issues.append({"type": "size", "message": "Code exceeds 100KB"})

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "language": language.value,
        }
