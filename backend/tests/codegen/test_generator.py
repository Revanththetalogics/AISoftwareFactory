"""
Tests for Code Generator.
"""

import pytest

from backend.codegen.generator import (
    CodeGenerator,
    CodeLanguage,
    CodeTemplate,
    GeneratedCode,
)


class TestCodeTemplate:
    """Test cases for CodeTemplate."""

    def test_template_creation(self):
        """Test creating a template."""
        template = CodeTemplate(
            name="test",
            template="Hello, $name!",
            language=CodeLanguage.PYTHON,
            variables=["name"],
        )

        assert template.name == "test"
        assert template.language == CodeLanguage.PYTHON

    def test_template_render(self):
        """Test rendering a template."""
        template = CodeTemplate(
            name="greeting",
            template="Hello, $name!",
            language=CodeLanguage.PYTHON,
            variables=["name"],
        )

        result = template.render(name="World")

        assert result == "Hello, World!"

    def test_template_render_missing_variable(self):
        """Test rendering with missing variable."""
        template = CodeTemplate(
            name="test",
            template="Hello, $name!",
            language=CodeLanguage.PYTHON,
            variables=["name"],
        )

        with pytest.raises(ValueError):
            template.render()


class TestGeneratedCode:
    """Test cases for GeneratedCode."""

    def test_code_creation(self):
        """Test creating generated code."""
        code = GeneratedCode(
            content="print('hello')",
            language=CodeLanguage.PYTHON,
            file_path="test.py",
        )

        assert code.content == "print('hello')"
        assert code.language == CodeLanguage.PYTHON
        assert code.success is True

    def test_code_error(self):
        """Test generated code with error."""
        code = GeneratedCode(error="Generation failed")

        assert code.success is False
        assert code.error == "Generation failed"


class TestCodeGenerator:
    """Test cases for CodeGenerator."""

    def setup_method(self):
        """Create fresh generator for each test."""
        self.generator = CodeGenerator()

    def test_generator_initialization(self):
        """Test generator initializes with templates."""
        templates = self.generator.list_templates()

        assert len(templates) > 0
        assert "fastapi_endpoint" in templates

    def test_get_template(self):
        """Test getting a template."""
        template = self.generator.get_template("fastapi_endpoint")

        assert template is not None
        assert template.name == "fastapi_endpoint"

    def test_get_template_not_found(self):
        """Test getting non-existent template."""
        template = self.generator.get_template("nonexistent")

        assert template is None

    def test_generate_fastapi_endpoint(self):
        """Test generating FastAPI endpoint."""
        result = self.generator.generate(
            template_name="fastapi_endpoint",
            variables={
                "method": "get",
                "path": "/users",
                "endpoint_name": "get_users",
                "parameters": "",
                "description": "Get all users",
                "implementation": "users = []",
                "return_value": "users",
            },
        )

        assert result.success is True
        assert "@router.get" in result.content
        assert "get_users" in result.content

    def test_generate_missing_template(self):
        """Test generation with missing template."""
        result = self.generator.generate(
            template_name="nonexistent",
            variables={},
        )

        assert result.success is False
        assert "not found" in result.error

    def test_generate_missing_variables(self):
        """Test generation with missing variables."""
        result = self.generator.generate(
            template_name="fastapi_endpoint",
            variables={},
        )

        assert result.success is False

    def test_list_templates_by_language(self):
        """Test listing templates filtered by language."""
        templates = self.generator.list_templates(language=CodeLanguage.PYTHON)

        assert len(templates) > 0
        # All returned templates should be Python
        for name in templates:
            template = self.generator.get_template(name)
            assert template.language == CodeLanguage.PYTHON

    def test_validate_python_code(self):
        """Test validating Python code."""
        code = "print('hello')"

        result = self.generator.validate_code(code, CodeLanguage.PYTHON)

        assert result["valid"] is True
        assert result["language"] == "python"

    def test_validate_invalid_python(self):
        """Test validating invalid Python code."""
        code = "def foo(  # incomplete"

        result = self.generator.validate_code(code, CodeLanguage.PYTHON)

        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_json(self):
        """Test validating JSON."""
        code = '{"key": "value"}'

        result = self.generator.validate_code(code, CodeLanguage.JSON)

        assert result["valid"] is True

    def test_validate_invalid_json(self):
        """Test validating invalid JSON."""
        code = '{"key": invalid}'

        result = self.generator.validate_code(code, CodeLanguage.JSON)

        assert result["valid"] is False

    def test_register_template(self):
        """Test registering a custom template."""
        template = CodeTemplate(
            name="custom",
            template="Custom: $value",
            language=CodeLanguage.PYTHON,
            variables=["value"],
        )

        self.generator.register_template(template)

        assert "custom" in self.generator.list_templates()
