"""
Tests for Code Generator.
"""

import pytest

from backend.codegen.generator import (
    CodeFramework,
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


class TestCodeGeneratorExtendedCoverage:
    """Tests for extended coverage - lines 376-382, 405-411, 438, 478, 481."""

    def setup_method(self):
        """Create fresh generator for each test."""
        from backend.codegen.generator import CodeGenerator

        self.generator = CodeGenerator()

    def test_generate_from_template_generic_exception_lines_376_382(self):
        """Test lines 376-382: generic Exception handling in generate."""
        from unittest.mock import patch

        # Create a template
        bad_template = CodeTemplate(
            name="bad_template",
            template="$value",
            language=CodeLanguage.PYTHON,
            variables=["value"],
        )
        self.generator.register_template(bad_template)

        # Mock the template's render to raise a RuntimeError (not ValueError)
        def raise_runtime_error(**kwargs):
            raise RuntimeError("Unexpected error during rendering")

        # Patch the template directly in the generator's templates dict
        with patch.object(self.generator._templates["bad_template"], "render", side_effect=raise_runtime_error):
            result = self.generator.generate(
                "bad_template",
                {"value": "test"},  # Variables as dict
            )

            # Lines 376-382: should catch exception and return error
            assert result.success is False
            assert "Unexpected error" in result.error

    def test_generate_from_description_lines_405_411(self):
        """Test lines 405-411: generate_from_description method."""
        result = self.generator.generate_from_description(
            description="A function that adds two numbers",
            language=CodeLanguage.PYTHON,
            framework=CodeFramework.FASTAPI,
        )

        # Lines 405-411: should return placeholder code
        assert result.success is True
        assert "TODO" in result.content
        assert result.language == CodeLanguage.PYTHON
        assert result.framework == CodeFramework.FASTAPI
        assert result.metadata["source"] == "description"

    def test_generate_from_description_without_framework(self):
        """Test generate_from_description without framework."""
        result = self.generator.generate_from_description(
            description="A simple utility function",
            language=CodeLanguage.TYPESCRIPT,
        )

        assert result.success is True
        assert result.language == CodeLanguage.TYPESCRIPT
        assert result.framework is None

    def test_list_templates_filter_by_framework_line_438(self):
        """Test line 438: list_templates with framework filter."""
        # Register a template with a specific framework
        template = CodeTemplate(
            name="fastapi_custom",
            template="# FastAPI custom",
            language=CodeLanguage.PYTHON,
            framework=CodeFramework.FASTAPI,
            variables=[],
        )
        self.generator.register_template(template)

        # Filter by framework (line 437-438)
        templates = self.generator.list_templates(framework=CodeFramework.FASTAPI)

        assert "fastapi_custom" in templates
        assert "fastapi_endpoint" in templates  # Built-in

        # Filter by different framework
        templates_react = self.generator.list_templates(framework=CodeFramework.REACT)

        # fastapi_custom should not be in React templates
        assert "fastapi_custom" not in templates_react

    def test_validate_code_empty_line_478(self):
        """Test line 478: empty code validation."""
        result = self.generator.validate_code("", CodeLanguage.PYTHON)

        # Lines 477-478: empty code should report issue
        assert result["valid"] is False
        assert any(issue["type"] == "empty" for issue in result["issues"])

    def test_validate_code_whitespace_only(self):
        """Test validation with whitespace only code."""
        result = self.generator.validate_code("   \n\t\n   ", CodeLanguage.PYTHON)

        # Should also be considered empty after strip
        assert result["valid"] is False

    def test_validate_code_too_large_line_481(self):
        """Test lines 480-481: code size validation."""
        # Create code that exceeds 100KB
        large_code = "x = 1\n" * 20001  # About 140KB

        result = self.generator.validate_code(large_code, CodeLanguage.PYTHON)

        # Lines 480-481: should report size issue
        assert result["valid"] is False
        assert any(issue["type"] == "size" for issue in result["issues"])
