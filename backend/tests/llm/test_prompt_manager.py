"""
Tests for Prompt Manager.
"""

import pytest

from backend.llm.prompt_manager import PromptManager, PromptTemplate


class TestPromptTemplate:
    """Test cases for PromptTemplate."""
    
    def test_template_creation(self):
        """Test creating a template."""
        template = PromptTemplate(
            name="test",
            template="Hello, $name!",
            variables=["name"],
        )
        
        assert template.name == "test"
        assert template.template == "Hello, $name!"
        assert template.variables == ["name"]
    
    def test_template_render(self):
        """Test rendering a template."""
        template = PromptTemplate(
            name="greeting",
            template="Hello, $name!",
            variables=["name"],
        )
        
        result = template.render(name="World")
        
        assert result == "Hello, World!"
    
    def test_template_render_missing_variable(self):
        """Test rendering with missing variable."""
        template = PromptTemplate(
            name="test",
            template="Hello, $name!",
            variables=["name"],
        )
        
        with pytest.raises(ValueError):
            template.render()  # Missing 'name'
    
    def test_validate_variables(self):
        """Test variable validation."""
        template = PromptTemplate(
            name="test",
            template="Hello, $name! You are $age years old.",
            variables=["name", "age"],
        )
        
        missing = template.validate_variables(name="John")
        
        assert "age" in missing
        assert "name" not in missing


class TestPromptManager:
    """Test cases for PromptManager."""
    
    def setup_method(self):
        """Create fresh manager for each test."""
        self.manager = PromptManager()
    
    def test_manager_initialization(self):
        """Test manager initializes with default templates."""
        templates = self.manager.list_templates()
        
        assert "code_generation" in templates
        assert "code_review" in templates
        assert "architecture_design" in templates
    
    def test_register_template(self):
        """Test registering a template."""
        template = self.manager.register_template(
            name="custom",
            template="Custom: $value",
            variables=["value"],
        )
        
        assert template.name == "custom"
        assert "custom" in self.manager.list_templates()
    
    def test_get_template(self):
        """Test getting a template."""
        template = self.manager.get_template("code_generation")
        
        assert template is not None
        assert template.name == "code_generation"
    
    def test_get_template_not_found(self):
        """Test getting non-existent template."""
        template = self.manager.get_template("nonexistent")
        
        assert template is None
    
    def test_render(self):
        """Test rendering a template."""
        result = self.manager.render(
            "requirements_analysis",
            idea="Build a todo app",
        )
        
        assert "todo app" in result
        assert "Problem statement" in result
    
    def test_render_not_found(self):
        """Test rendering non-existent template."""
        with pytest.raises(ValueError):
            self.manager.render("nonexistent", value="test")
    
    def test_render_missing_variables(self):
        """Test rendering with missing variables."""
        with pytest.raises(ValueError):
            self.manager.render("code_generation")  # Missing required variables
    
    def test_list_templates(self):
        """Test listing all templates."""
        templates = self.manager.list_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        code_templates = self.manager.get_templates_by_category("code")
        
        assert len(code_templates) > 0
        # Should include code_generation and code_review
        template_names = [t.name for t in code_templates]
        assert "code_generation" in template_names
    
    def test_optimize_prompt(self):
        """Test prompt optimization."""
        long_prompt = "x" * 5000
        
        optimized = self.manager.optimize_prompt(long_prompt, max_length=100)
        
        assert len(optimized) <= 120  # Allow for "... [truncated]"
        assert "[truncated]" in optimized
    
    def test_optimize_prompt_short(self):
        """Test optimization of short prompt (no change)."""
        short_prompt = "Hello, world!"
        
        optimized = self.manager.optimize_prompt(short_prompt, max_length=1000)
        
        assert optimized == short_prompt
