"""
Validation engine for Simulation module.

This module provides pass/fail criteria and quality gates for
code validation.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from backend.core.logging import get_logger

logger = get_logger(__name__)


class ValidationStatus(Enum):
    """Validation status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class ValidationRule:
    """Validation rule definition."""
    name: str
    check: Callable
    required: bool = True
    weight: float = 1.0


@dataclass
class ValidationResult:
    """Validation result."""
    rule_name: str
    status: ValidationStatus
    message: str
    score: float = 0.0


class ValidationEngine:
    """
    Validation engine for quality gates.
    
    Provides configurable validation rules and scoring
    for code quality assessment.
    """
    
    def __init__(self):
        """Initialize the validation engine."""
        self._rules: List[ValidationRule] = []
        self._logger = get_logger(__name__)
        
        # Default rules
        self._add_default_rules()
    
    def _add_default_rules(self):
        """Add default validation rules."""
        self.add_rule(ValidationRule(
            name="syntax_check",
            check=self._check_syntax,
            required=True,
            weight=2.0
        ))
        
        self.add_rule(ValidationRule(
            name="no_critical_vulnerabilities",
            check=self._check_vulnerabilities,
            required=True,
            weight=3.0
        ))
    
    def add_rule(self, rule: ValidationRule):
        """
        Add a validation rule.
        
        Args:
            rule: Rule to add
        """
        self._rules.append(rule)
        self._logger.info("Validation rule added", rule_name=rule.name)
    
    async def validate(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run all validation rules.
        
        Args:
            code: Code to validate
            context: Additional validation context
            
        Returns:
            Validation results
        """
        results = []
        total_score = 0.0
        max_score = 0.0
        passed = 0
        failed = 0
        
        for rule in self._rules:
            try:
                result = await rule.check(code, context or {})
                results.append(result)
                
                max_score += rule.weight
                
                if result.status == ValidationStatus.PASS:
                    total_score += rule.weight
                    passed += 1
                elif result.status == ValidationStatus.FAIL and rule.required:
                    failed += 1
                
            except Exception as e:
                self._logger.error(
                    "Validation rule failed",
                    rule=rule.name,
                    error=str(e)
                )
                results.append(ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.FAIL,
                    message=f"Rule execution failed: {e}",
                    score=0.0
                ))
                failed += 1
        
        score_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            "overall_status": "pass" if failed == 0 else "fail",
            "score": score_percentage,
            "passed_rules": passed,
            "failed_rules": failed,
            "total_rules": len(self._rules),
            "results": [
                {
                    "rule": r.rule_name,
                    "status": r.status.value,
                    "message": r.message,
                    "score": r.score
                }
                for r in results
            ]
        }
    
    async def _check_syntax(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Check code syntax."""
        try:
            import ast
            ast.parse(code)
            return ValidationResult(
                rule_name="syntax_check",
                status=ValidationStatus.PASS,
                message="Syntax is valid",
                score=1.0
            )
        except SyntaxError as e:
            return ValidationResult(
                rule_name="syntax_check",
                status=ValidationStatus.FAIL,
                message=f"Syntax error: {e}",
                score=0.0
            )
    
    async def _check_vulnerabilities(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Check for critical vulnerabilities."""
        from backend.simulation.security_scanner import SecurityScanner
        
        scanner = SecurityScanner()
        issues = await scanner.scan_code(code)
        
        critical_count = len([i for i in issues if i.severity == "critical"])
        
        if critical_count == 0:
            return ValidationResult(
                rule_name="no_critical_vulnerabilities",
                status=ValidationStatus.PASS,
                message="No critical vulnerabilities found",
                score=1.0
            )
        else:
            return ValidationResult(
                rule_name="no_critical_vulnerabilities",
                status=ValidationStatus.FAIL,
                message=f"Found {critical_count} critical vulnerabilities",
                score=0.0
            )
