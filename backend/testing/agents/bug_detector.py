"""
Bug Detector Agent - AI-powered bug detection and analysis.

This agent uses multiple strategies to detect bugs:
- Static analysis integration (pylint, mypy, bandit)
- LLM-based code review
- Test failure pattern analysis
- Runtime behavior analysis
"""

import ast
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.llm.factory import LLMFactory
from backend.core.logging import get_logger

logger = get_logger(__name__)


class BugSeverity(Enum):
    """Bug severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BugCategory(Enum):
    """Bug categories."""
    SYNTAX = "syntax"
    LOGIC = "logic"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TYPE_SAFETY = "type_safety"
    CONCURRENCY = "concurrency"
    RESOURCE_LEAK = "resource_leak"


@dataclass
class BugLocation:
    """Location of a bug in code."""
    file_path: str
    line_number: int
    column: Optional[int] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "function_name": self.function_name,
            "class_name": self.class_name,
        }


@dataclass
class DetectedBug:
    """Represents a detected bug."""
    id: str
    severity: BugSeverity
    category: BugCategory
    title: str
    description: str
    location: BugLocation
    code_snippet: str
    root_cause: str
    suggested_fix: str
    confidence: float
    detection_method: str
    fix_complexity: str  # simple, moderate, complex
    estimated_effort_minutes: int
    related_bugs: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "location": self.location.to_dict(),
            "code_snippet": self.code_snippet,
            "root_cause": self.root_cause,
            "suggested_fix": self.suggested_fix,
            "confidence": self.confidence,
            "detection_method": self.detection_method,
            "fix_complexity": self.fix_complexity,
            "estimated_effort_minutes": self.estimated_effort_minutes,
            "related_bugs": self.related_bugs,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class BugPattern:
    """Pattern for detecting specific bug types."""
    name: str
    category: BugCategory
    severity: BugSeverity
    pattern: str  # Regex or AST pattern
    description: str
    suggestion: str
    confidence_boost: float = 0.0


class BugDetectorAgent(BaseAgent):
    """
    Agent for detecting bugs using multiple strategies.
    
    This agent combines:
    - Static analysis (AST parsing, regex patterns)
    - LLM-based intelligent code review
    - Test failure analysis
    - Security vulnerability scanning
    - Performance anti-pattern detection
    
    Example:
        >>> agent = BugDetectorAgent()
        >>> task = Task(
        ...     task_type="detect_bugs",
        ...     description="Find bugs in auth module",
        ...     context={"file_path": "backend/services/auth.py"}
        ... )
        >>> result = await agent.execute_task(task)
    """
    
    def __init__(self):
        """Initialize the bug detector agent."""
        super().__init__(
            name="BugDetector",
            role="Security & Quality Analyst",
            capabilities=[
                "static_analysis",
                "security_scanning",
                "pattern_matching",
                "llm_code_review",
                "test_failure_analysis",
            ],
            description="Detects bugs using AI and static analysis",
        )
        self._llm = LLMFactory.create_llm()
        self._patterns = self._load_bug_patterns()
    
    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a bug detection task.
        
        Args:
            task: Task containing detection parameters
            
        Returns:
            TaskResult with detected bugs
        """
        start_time = datetime.utcnow()
        
        try:
            if task.task_type == "detect_bugs":
                result = await self._detect_bugs_task(task)
            elif task.task_type == "security_scan":
                result = await self._security_scan_task(task)
            elif task.task_type == "analyze_test_failure":
                result = await self._analyze_failure_task(task)
            elif task.task_type == "performance_audit":
                result = await self._performance_audit_task(task)
            else:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"Unknown task type: {task.task_type}",
                )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output=result,
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            self._logger.error("Bug detection failed", error=str(e))
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )
    
    async def detect_bugs_in_file(
        self,
        file_path: str,
        use_static_analysis: bool = True,
        use_llm_review: bool = True,
        min_confidence: float = 0.7
    ) -> List[DetectedBug]:
        """
        Detect bugs in a single file.
        
        Args:
            file_path: Path to the file
            use_static_analysis: Enable static analysis
            use_llm_review: Enable LLM review
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of detected bugs
        """
        self._logger.info("Detecting bugs", file_path=file_path)
        
        all_bugs = []
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except Exception as e:
            self._logger.error("Failed to read file", file_path=file_path, error=str(e))
            return []
        
        # Static analysis
        if use_static_analysis:
            static_bugs = await self._run_static_analysis(file_path, code)
            all_bugs.extend(static_bugs)
        
        # Pattern matching
        pattern_bugs = await self._run_pattern_matching(file_path, code)
        all_bugs.extend(pattern_bugs)
        
        # LLM review
        if use_llm_review:
            llm_bugs = await self._run_llm_review(file_path, code)
            all_bugs.extend(llm_bugs)
        
        # Filter by confidence
        filtered_bugs = [b for b in all_bugs if b.confidence >= min_confidence]
        
        # Sort by severity
        severity_order = {
            BugSeverity.CRITICAL: 0,
            BugSeverity.HIGH: 1,
            BugSeverity.MEDIUM: 2,
            BugSeverity.LOW: 3,
            BugSeverity.INFO: 4,
        }
        filtered_bugs.sort(key=lambda b: severity_order[b.severity])
        
        self._logger.info(
            "Bug detection complete",
            file_path=file_path,
            bugs_found=len(filtered_bugs),
            critical=len([b for b in filtered_bugs if b.severity == BugSeverity.CRITICAL]),
        )
        
        return filtered_bugs
    
    async def detect_bugs_in_directory(
        self,
        directory: str,
        file_patterns: List[str] = None,
        **kwargs
    ) -> Dict[str, List[DetectedBug]]:
        """
        Detect bugs in all files in a directory.
        
        Args:
            directory: Directory to scan
            file_patterns: File patterns to include
            **kwargs: Additional arguments for detect_bugs_in_file
            
        Returns:
            Dictionary mapping file paths to bugs
        """
        if file_patterns is None:
            file_patterns = ["*.py"]
        
        results = {}
        path = Path(directory)
        
        for pattern in file_patterns:
            for file_path in path.rglob(pattern):
                if file_path.is_file():
                    bugs = await self.detect_bugs_in_file(
                        str(file_path),
                        **kwargs
                    )
                    if bugs:
                        results[str(file_path)] = bugs
        
        return results
    
    async def analyze_test_failure(
        self,
        test_name: str,
        error_message: str,
        stack_trace: str,
        code_context: str,
        file_path: str
    ) -> Optional[DetectedBug]:
        """
        Analyze a test failure to identify the root cause bug.
        
        Args:
            test_name: Name of the failing test
            error_message: Error message
            stack_trace: Stack trace
            code_context: Code where failure occurred
            file_path: File path
            
        Returns:
            Detected bug or None
        """
        prompt = f"""Analyze this test failure and identify the root cause bug:

Test: {test_name}
Error: {error_message}

Stack Trace:
{stack_trace}

Code Context:
```python
{code_context}
```

Provide analysis as JSON:
{{
    "title": "Brief bug description",
    "category": "logic|syntax|security|performance|type_safety",
    "severity": "critical|high|medium|low",
    "description": "Detailed description",
    "root_cause": "Why this bug occurred",
    "suggested_fix": "How to fix it",
    "line_number": number,
    "confidence": 0.0-1.0
}}"""
        
        try:
            response = await self._llm.generate(prompt)
            import json
            analysis = json.loads(response)
            
            location = BugLocation(
                file_path=file_path,
                line_number=analysis.get("line_number", 1),
            )
            
            return DetectedBug(
                id=f"failure_{datetime.utcnow().timestamp()}",
                severity=BugSeverity(analysis["severity"]),
                category=BugCategory(analysis["category"]),
                title=analysis["title"],
                description=analysis["description"],
                location=location,
                code_snippet=code_context,
                root_cause=analysis["root_cause"],
                suggested_fix=analysis["suggested_fix"],
                confidence=analysis.get("confidence", 0.8),
                detection_method="test_failure_analysis",
                fix_complexity="moderate",
                estimated_effort_minutes=30,
            )
            
        except Exception as e:
            self._logger.error("Failed to analyze test failure", error=str(e))
            return None
    
    async def get_bug_statistics(self, bugs: List[DetectedBug]) -> Dict[str, Any]:
        """
        Get statistics about detected bugs.
        
        Args:
            bugs: List of bugs
            
        Returns:
            Statistics dictionary
        """
        stats = {
            "total": len(bugs),
            "by_severity": {},
            "by_category": {},
            "by_detection_method": {},
            "total_estimated_effort_minutes": 0,
            "high_confidence_bugs": 0,
        }
        
        for bug in bugs:
            # By severity
            sev = bug.severity.value
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
            
            # By category
            cat = bug.category.value
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            
            # By detection method
            method = bug.detection_method
            stats["by_detection_method"][method] = stats["by_detection_method"].get(method, 0) + 1
            
            # Effort
            stats["total_estimated_effort_minutes"] += bug.estimated_effort_minutes
            
            # High confidence
            if bug.confidence >= 0.9:
                stats["high_confidence_bugs"] += 1
        
        return stats
    
    # Private methods
    
    def _load_bug_patterns(self) -> List[BugPattern]:
        """Load bug detection patterns."""
        return [
            # Security patterns
            BugPattern(
                name="hardcoded_password",
                category=BugCategory.SECURITY,
                severity=BugSeverity.CRITICAL,
                pattern=r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                description="Hardcoded password detected",
                suggestion="Use environment variables or secrets manager",
                confidence_boost=0.9,
            ),
            BugPattern(
                name="sql_injection_risk",
                category=BugCategory.SECURITY,
                severity=BugSeverity.HIGH,
                pattern=r'execute\s*\(\s*["\'].*%s.*["\']',
                description="Potential SQL injection vulnerability",
                suggestion="Use parameterized queries",
                confidence_boost=0.8,
            ),
            BugPattern(
                name="eval_usage",
                category=BugCategory.SECURITY,
                severity=BugSeverity.CRITICAL,
                pattern=r'\beval\s*\(',
                description="Dangerous eval() usage",
                suggestion="Use ast.literal_eval for safe evaluation",
                confidence_boost=0.95,
            ),
            
            # Logic patterns
            BugPattern(
                name="bare_except",
                category=BugCategory.LOGIC,
                severity=BugSeverity.MEDIUM,
                pattern=r'except\s*:',
                description="Bare except clause catches all exceptions including KeyboardInterrupt",
                suggestion="Use 'except Exception:' or specific exceptions",
                confidence_boost=0.9,
            ),
            BugPattern(
                name="mutable_default_arg",
                category=BugCategory.LOGIC,
                severity=BugSeverity.HIGH,
                pattern=r'def\s+\w+\s*\([^)]*=\s*(\[|\{)',
                description="Mutable default argument can cause unexpected behavior",
                suggestion="Use None as default and initialize inside function",
                confidence_boost=0.9,
            ),
            
            # Performance patterns
            BugPattern(
                name="list_in_for_loop",
                category=BugCategory.PERFORMANCE,
                severity=BugSeverity.LOW,
                pattern=r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(',
                description="Using range(len()) instead of enumerate()",
                suggestion="Use enumerate() for cleaner code",
                confidence_boost=0.7,
            ),
            
            # Resource leak patterns
            BugPattern(
                name="unclosed_file",
                category=BugCategory.RESOURCE_LEAK,
                severity=BugSeverity.MEDIUM,
                pattern=r'open\s*\([^)]+\)(?!\s+as)',
                description="File opened without context manager",
                suggestion="Use 'with open(...) as f:' pattern",
                confidence_boost=0.8,
            ),
        ]
    
    async def _run_static_analysis(self, file_path: str, code: str) -> List[DetectedBug]:
        """Run static analysis using AST."""
        bugs = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            # Syntax error is a critical bug
            location = BugLocation(
                file_path=file_path,
                line_number=e.lineno or 1,
                column=e.offset,
            )
            
            bug = DetectedBug(
                id=f"syntax_{file_path}_{e.lineno}",
                severity=BugSeverity.CRITICAL,
                category=BugCategory.SYNTAX,
                title="Syntax Error",
                description=str(e),
                location=location,
                code_snippet=code.splitlines()[e.lineno - 1] if e.lineno else "",
                root_cause="Invalid Python syntax",
                suggested_fix="Fix the syntax error",
                confidence=1.0,
                detection_method="static_analysis",
                fix_complexity="simple",
                estimated_effort_minutes=5,
            )
            bugs.append(bug)
            return bugs
        
        # Check for common issues using AST
        for node in ast.walk(tree):
            # Check for unused variables
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # This is a simplified check - full implementation would track usage
                pass
            
            # Check for dangerous built-ins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        location = BugLocation(
                            file_path=file_path,
                            line_number=getattr(node, 'lineno', 1),
                        )
                        
                        bug = DetectedBug(
                            id=f"dangerous_{node.func.id}_{file_path}_{location.line_number}",
                            severity=BugSeverity.CRITICAL,
                            category=BugCategory.SECURITY,
                            title=f"Dangerous {node.func.id}() usage",
                            description=f"Using {node.func.id}() can execute arbitrary code",
                            location=location,
                            code_snippet=ast.unparse(node),
                            root_cause=f"{node.func.id}() executes arbitrary code",
                            suggested_fix=f"Avoid {node.func.id}() or use safer alternatives",
                            confidence=0.95,
                            detection_method="static_analysis",
                            fix_complexity="complex",
                            estimated_effort_minutes=60,
                        )
                        bugs.append(bug)
        
        return bugs
    
    async def _run_pattern_matching(self, file_path: str, code: str) -> List[DetectedBug]:
        """Run regex pattern matching for bug detection."""
        bugs = []
        lines = code.splitlines()
        
        for pattern in self._patterns:
            for match in re.finditer(pattern.pattern, code, re.IGNORECASE):
                # Find line number
                line_number = code[:match.start()].count('\n') + 1
                code_snippet = lines[line_number - 1] if line_number <= len(lines) else ""
                
                location = BugLocation(
                    file_path=file_path,
                    line_number=line_number,
                )
                
                bug = DetectedBug(
                    id=f"{pattern.name}_{file_path}_{line_number}",
                    severity=pattern.severity,
                    category=pattern.category,
                    title=pattern.name.replace("_", " ").title(),
                    description=pattern.description,
                    location=location,
                    code_snippet=code_snippet.strip(),
                    root_cause=f"Pattern '{pattern.name}' detected",
                    suggested_fix=pattern.suggestion,
                    confidence=0.7 + pattern.confidence_boost,
                    detection_method="pattern_matching",
                    fix_complexity="simple",
                    estimated_effort_minutes=15,
                )
                bugs.append(bug)
        
        return bugs
    
    async def _run_llm_review(self, file_path: str, code: str) -> List[DetectedBug]:
        """Run LLM-based code review."""
        prompt = f"""Review this Python code for bugs, security issues, and code smells:

File: {file_path}

```python
{code}
```

Identify issues and return as JSON array:
[
  {{
    "title": "Issue title",
    "category": "logic|security|performance|maintainability|type_safety",
    "severity": "critical|high|medium|low",
    "line_number": 1,
    "description": "Detailed description",
    "root_cause": "Why this is a problem",
    "suggested_fix": "How to fix it",
    "confidence": 0.0-1.0
  }}
]

If no issues found, return empty array []. Be thorough but only report real issues."""
        
        try:
            response = await self._llm.generate(prompt)
            import json
            findings = json.loads(response)
            
            bugs = []
            for finding in findings:
                location = BugLocation(
                    file_path=file_path,
                    line_number=finding.get("line_number", 1),
                )
                
                bug = DetectedBug(
                    id=f"llm_{file_path}_{finding.get('line_number', 0)}_{datetime.utcnow().timestamp()}",
                    severity=BugSeverity(finding["severity"]),
                    category=BugCategory(finding["category"]),
                    title=finding["title"],
                    description=finding["description"],
                    location=location,
                    code_snippet="",  # Could extract based on line number
                    root_cause=finding["root_cause"],
                    suggested_fix=finding["suggested_fix"],
                    confidence=finding.get("confidence", 0.8),
                    detection_method="llm_review",
                    fix_complexity="moderate",
                    estimated_effort_minutes=30,
                )
                bugs.append(bug)
            
            return bugs
            
        except Exception as e:
            self._logger.error("LLM review failed", error=str(e))
            return []
    
    async def _detect_bugs_task(self, task: Task) -> Dict[str, Any]:
        """Handle detect_bugs task type."""
        file_path = task.context.get("file_path")
        directory = task.context.get("directory")
        
        if directory:
            results = await self.detect_bugs_in_directory(
                directory,
                task.context.get("file_patterns", ["*.py"]),
                use_static_analysis=task.context.get("use_static_analysis", True),
                use_llm_review=task.context.get("use_llm_review", True),
                min_confidence=task.context.get("min_confidence", 0.7),
            )
            all_bugs = [bug for bugs in results.values() for bug in bugs]
            
            return {
                "directory": directory,
                "files_scanned": len(results),
                "total_bugs": len(all_bugs),
                "bugs_by_file": {f: len(b) for f, b in results.items()},
                "statistics": await self.get_bug_statistics(all_bugs),
                "bugs": [b.to_dict() for b in all_bugs[:50]],  # Limit output
            }
        
        elif file_path:
            bugs = await self.detect_bugs_in_file(
                file_path,
                use_static_analysis=task.context.get("use_static_analysis", True),
                use_llm_review=task.context.get("use_llm_review", True),
                min_confidence=task.context.get("min_confidence", 0.7),
            )
            
            return {
                "file_path": file_path,
                "bugs_found": len(bugs),
                "statistics": await self.get_bug_statistics(bugs),
                "bugs": [b.to_dict() for b in bugs],
            }
        
        else:
            raise ValueError("Either file_path or directory required")
    
    async def _security_scan_task(self, task: Task) -> Dict[str, Any]:
        """Handle security_scan task type."""
        file_path = task.context.get("file_path")
        bugs = await self.detect_bugs_in_file(
            file_path,
            use_static_analysis=True,
            use_llm_review=True,
        )
        
        # Filter only security bugs
        security_bugs = [b for b in bugs if b.category == BugCategory.SECURITY]
        
        return {
            "file_path": file_path,
            "security_issues_found": len(security_bugs),
            "critical": len([b for b in security_bugs if b.severity == BugSeverity.CRITICAL]),
            "bugs": [b.to_dict() for b in security_bugs],
        }
    
    async def _analyze_failure_task(self, task: Task) -> Dict[str, Any]:
        """Handle analyze_test_failure task type."""
        bug = await self.analyze_test_failure(
            test_name=task.context["test_name"],
            error_message=task.context["error_message"],
            stack_trace=task.context["stack_trace"],
            code_context=task.context["code_context"],
            file_path=task.context["file_path"],
        )
        
        return {
            "bug": bug.to_dict() if bug else None,
        }
    
    async def _performance_audit_task(self, task: Task) -> Dict[str, Any]:
        """Handle performance_audit task type."""
        file_path = task.context.get("file_path")
        bugs = await self.detect_bugs_in_file(file_path)
        
        # Filter performance bugs
        perf_bugs = [b for b in bugs if b.category == BugCategory.PERFORMANCE]
        
        return {
            "file_path": file_path,
            "performance_issues": len(perf_bugs),
            "bugs": [b.to_dict() for b in perf_bugs],
        }
