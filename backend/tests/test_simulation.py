"""
Tests for Simulation components.
"""

import pytest

from backend.simulation.security_scanner import SecurityScanner, SecurityIssue
from backend.simulation.sandbox import Sandbox
from backend.simulation.validation_engine import ValidationEngine, ValidationStatus


class TestSecurityScanner:
    """Tests for SecurityScanner."""
    
    @pytest.mark.asyncio
    async def test_scan_safe_code(self):
        """Test scanning safe code."""
        scanner = SecurityScanner()
        
        safe_code = """
def hello():
    return "Hello, World!"
"""
        
        issues = await scanner.scan_code(safe_code)
        
        # Should have no critical issues
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0
    
    @pytest.mark.asyncio
    async def test_detect_eval(self):
        """Test detecting eval usage."""
        scanner = SecurityScanner()
        
        dangerous_code = """
result = eval(user_input)
"""
        
        issues = await scanner.scan_code(dangerous_code)
        
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) > 0
    
    @pytest.mark.asyncio
    async def test_scan_dependencies(self):
        """Test scanning dependencies."""
        scanner = SecurityScanner()
        
        requirements = ["requests==2.19.0", "django==2.0"]
        
        issues = await scanner.scan_dependencies(requirements)
        
        # Should detect vulnerable packages
        assert len(issues) > 0


class TestValidationEngine:
    """Tests for ValidationEngine."""
    
    @pytest.mark.asyncio
    async def test_validate_valid_code(self):
        """Test validating valid code."""
        engine = ValidationEngine()
        
        valid_code = """
def hello():
    return "Hello"
"""
        
        result = await engine.validate(valid_code)
        
        assert result["overall_status"] == "pass"
    
    @pytest.mark.asyncio
    async def test_validate_syntax_error(self):
        """Test validating code with syntax error."""
        engine = ValidationEngine()
        
        invalid_code = """
def hello(
    return "Hello"
"""
        
        result = await engine.validate(invalid_code)
        
        assert result["overall_status"] == "fail"
        
        syntax_results = [r for r in result["results"] if r["rule"] == "syntax_check"]
        assert len(syntax_results) > 0
        assert syntax_results[0]["status"] == "fail"


class TestSandbox:
    """Tests for Sandbox."""
    
    @pytest.mark.asyncio
    async def test_execute_python_code(self):
        """Test executing Python code."""
        sandbox = Sandbox()
        
        code = """
print("Hello, World!")
x = 1 + 1
print(f"Result: {x}")
"""
        
        result = await sandbox.execute(code, language="python")
        
        assert result.success is True
        assert "Hello, World!" in result.stdout
        assert result.exit_code == 0
    
    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        """Test executing code with error."""
        sandbox = Sandbox()
        
        code = """
raise ValueError("Test error")
"""
        
        result = await sandbox.execute(code, language="python")
        
        assert result.success is False
        assert result.exit_code != 0
