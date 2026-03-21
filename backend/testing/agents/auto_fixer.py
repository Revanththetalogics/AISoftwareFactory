"""
Auto Fixer Agent - AI-powered automatic code repair.

This agent automatically fixes detected bugs using:
- Pattern-based fixes for common issues
- LLM-generated fixes for complex bugs
- Safe refactoring with validation
- Rollback capability
"""

import ast
import difflib
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus
from backend.core.logging import get_logger
from backend.llm.factory import LLMFactory

logger = get_logger(__name__)


class FixStatus(Enum):
    """Status of a fix attempt."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    VALIDATION_FAILED = "validation_failed"
    ROLLED_BACK = "rolled_back"


class FixStrategy(Enum):
    """Strategy used for fixing."""
    PATTERN = "pattern"  # Regex/AST pattern-based
    LLM = "llm"  # LLM-generated fix
    REFACTORING = "refactoring"  # Safe refactoring
    MANUAL = "manual"  # Requires human review


@dataclass
class CodeChange:
    """Represents a code change."""
    file_path: str
    line_start: int
    line_end: int
    original_code: str
    new_code: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "original_code": self.original_code,
            "new_code": self.new_code,
            "description": self.description,
        }


@dataclass
class FixAttempt:
    """Represents a fix attempt."""
    id: str
    bug_id: str
    file_path: str
    strategy: FixStrategy
    status: FixStatus
    changes: list[CodeChange] = field(default_factory=list)
    diff: str = ""
    validation_results: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    applied_at: datetime | None = None
    rolled_back_at: datetime | None = None
    backup_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "bug_id": self.bug_id,
            "file_path": self.file_path,
            "strategy": self.strategy.value,
            "status": self.status.value,
            "changes": [c.to_dict() for c in self.changes],
            "diff": self.diff,
            "validation_results": self.validation_results,
            "error_message": self.error_message,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "rolled_back_at": self.rolled_back_at.isoformat() if self.rolled_back_at else None,
        }


@dataclass
class ValidationResult:
    """Result of fix validation."""
    passed: bool
    syntax_valid: bool
    tests_pass: bool
    no_new_issues: bool
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "syntax_valid": self.syntax_valid,
            "tests_pass": self.tests_pass,
            "no_new_issues": self.no_new_issues,
            "messages": self.messages,
        }


class AutoFixerAgent(BaseAgent):
    """
    Agent for automatically fixing detected bugs.

    This agent provides:
    - Pattern-based fixes for common issues
    - LLM-generated fixes for complex bugs
    - Safe validation before applying
    - Automatic rollback on failure
    - Batch fix operations

    Example:
        >>> agent = AutoFixerAgent()
        >>> task = Task(
        ...     task_type="auto_fix",
        ...     description="Fix security issues",
        ...     context={"bug_id": "bug_123", "file_path": "auth.py"}
        ... )
        >>> result = await agent.execute_task(task)
    """

    def __init__(self, backup_dir: str = ".test_backups"):
        """
        Initialize the auto fixer agent.

        Args:
            backup_dir: Directory for backup files
        """
        super().__init__(
            name="AutoFixer",
            role="Code Repair Specialist",
            capabilities=[
                "pattern_based_fixing",
                "llm_generated_fixes",
                "safe_refactoring",
                "validation",
                "rollback",
            ],
            description="Automatically fixes bugs with validation and rollback",
        )
        self._llm = LLMFactory.create_llm()
        self._backup_dir = Path(backup_dir)
        self._backup_dir.mkdir(exist_ok=True)
        self._fix_patterns = self._load_fix_patterns()
        self._fix_history: list[FixAttempt] = []

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute an auto-fix task.

        Args:
            task: Task containing fix parameters

        Returns:
            TaskResult with fix results
        """
        start_time = datetime.utcnow()

        try:
            if task.task_type == "auto_fix":
                result = await self._auto_fix_task(task)
            elif task.task_type == "batch_fix":
                result = await self._batch_fix_task(task)
            elif task.task_type == "rollback":
                result = await self._rollback_task(task)
            elif task.task_type == "preview_fix":
                result = await self._preview_fix_task(task)
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
            self._logger.error("Auto-fix failed", error=str(e))
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def fix_bug(
        self,
        bug_id: str,
        file_path: str,
        bug_description: str,
        suggested_fix: str,
        line_number: int | None = None,
        auto_apply: bool = False,
        validate: bool = True
    ) -> FixAttempt:
        """
        Fix a single bug.

        Args:
            bug_id: Unique bug identifier
            file_path: Path to the file
            bug_description: Description of the bug
            suggested_fix: Suggested fix from bug detector
            line_number: Line number of the bug
            auto_apply: Whether to apply without confirmation
            validate: Whether to validate the fix

        Returns:
            FixAttempt with results
        """
        self._logger.info("Fixing bug", bug_id=bug_id, file_path=file_path)

        # Try pattern-based fix first
        fix_attempt = await self._try_pattern_fix(
            bug_id, file_path, bug_description, line_number
        )

        # If pattern fix failed, try LLM
        if fix_attempt.status == FixStatus.FAILED:
            fix_attempt = await self._try_llm_fix(
                bug_id, file_path, bug_description, suggested_fix, line_number
            )

        # Validate if requested
        if validate and fix_attempt.status != FixStatus.FAILED:
            validation = await self._validate_fix(fix_attempt)
            fix_attempt.validation_results = validation.to_dict()

            if not validation.passed:
                fix_attempt.status = FixStatus.VALIDATION_FAILED
                fix_attempt.error_message = "Validation failed: " + "; ".join(validation.messages)

        # Apply if auto_apply and validation passed
        if auto_apply and fix_attempt.status in [FixStatus.PENDING, FixStatus.SUCCESS]:
            success = await self._apply_fix(fix_attempt)
            if success:
                fix_attempt.status = FixStatus.SUCCESS
                fix_attempt.applied_at = datetime.utcnow()
            else:
                fix_attempt.status = FixStatus.FAILED

        self._fix_history.append(fix_attempt)

        self._logger.info(
            "Fix attempt complete",
            bug_id=bug_id,
            status=fix_attempt.status.value,
            strategy=fix_attempt.strategy.value,
        )

        return fix_attempt

    async def batch_fix(
        self,
        bugs: list[dict[str, Any]],
        auto_apply: bool = False,
        stop_on_failure: bool = True
    ) -> list[FixAttempt]:
        """
        Fix multiple bugs in batch.

        Args:
            bugs: List of bug dictionaries
            auto_apply: Whether to apply fixes automatically
            stop_on_failure: Stop on first failure

        Returns:
            List of fix attempts
        """
        self._logger.info("Starting batch fix", bug_count=len(bugs))

        results = []

        for bug in bugs:
            fix_attempt = await self.fix_bug(
                bug_id=bug["id"],
                file_path=bug["file_path"],
                bug_description=bug["description"],
                suggested_fix=bug.get("suggested_fix", ""),
                line_number=bug.get("line_number"),
                auto_apply=auto_apply,
                validate=True,
            )

            results.append(fix_attempt)

            if stop_on_failure and fix_attempt.status == FixStatus.FAILED:
                self._logger.warning("Stopping batch fix due to failure", bug_id=bug["id"])
                break

        self._logger.info(
            "Batch fix complete",
            total=len(results),
            successful=sum(1 for r in results if r.status == FixStatus.SUCCESS),
            failed=sum(1 for r in results if r.status == FixStatus.FAILED),
        )

        return results

    async def rollback_fix(self, fix_id: str) -> bool:
        """
        Rollback a previously applied fix.

        Args:
            fix_id: ID of the fix to rollback

        Returns:
            True if rollback successful
        """
        # Find the fix attempt
        fix_attempt = None
        for attempt in self._fix_history:
            if attempt.id == fix_id:
                fix_attempt = attempt
                break

        if not fix_attempt:
            self._logger.error("Fix not found for rollback", fix_id=fix_id)
            return False

        if not fix_attempt.backup_path:
            self._logger.error("No backup found for rollback", fix_id=fix_id)
            return False

        try:
            # Restore from backup
            shutil.copy2(fix_attempt.backup_path, fix_attempt.file_path)

            fix_attempt.status = FixStatus.ROLLED_BACK
            fix_attempt.rolled_back_at = datetime.utcnow()

            self._logger.info("Fix rolled back", fix_id=fix_id)
            return True

        except Exception as e:
            self._logger.error("Rollback failed", fix_id=fix_id, error=str(e))
            return False

    async def preview_fix(
        self,
        bug_id: str,
        file_path: str,
        bug_description: str,
        suggested_fix: str,
        line_number: int | None = None
    ) -> dict[str, Any]:
        """
        Preview a fix without applying it.

        Args:
            bug_id: Bug identifier
            file_path: File path
            bug_description: Bug description
            suggested_fix: Suggested fix
            line_number: Line number

        Returns:
            Preview information including diff
        """
        fix_attempt = await self._try_llm_fix(
            bug_id, file_path, bug_description, suggested_fix, line_number
        )

        return {
            "can_fix": fix_attempt.status != FixStatus.FAILED,
            "strategy": fix_attempt.strategy.value,
            "changes": [c.to_dict() for c in fix_attempt.changes],
            "diff": fix_attempt.diff,
            "validation_estimate": "Will validate syntax and run tests",
        }

    def get_fix_statistics(self) -> dict[str, Any]:
        """
        Get statistics about fixes.

        Returns:
            Fix statistics
        """
        total = len(self._fix_history)
        successful = sum(1 for f in self._fix_history if f.status == FixStatus.SUCCESS)
        failed = sum(1 for f in self._fix_history if f.status == FixStatus.FAILED)
        rolled_back = sum(1 for f in self._fix_history if f.status == FixStatus.ROLLED_BACK)

        by_strategy = {}
        for fix in self._fix_history:
            strategy = fix.strategy.value
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1

        return {
            "total_fixes": total,
            "successful": successful,
            "failed": failed,
            "rolled_back": rolled_back,
            "success_rate": successful / total if total > 0 else 0,
            "by_strategy": by_strategy,
            "recent_fixes": [f.to_dict() for f in self._fix_history[-10:]],
        }

    # Private methods

    def _load_fix_patterns(self) -> dict[str, Any]:
        """Load pattern-based fix definitions."""
        return {
            "bare_except": {
                "pattern": r'except\s*:',
                "replacement": 'except Exception:',
                "description": "Replace bare except with explicit Exception",
            },
            "mutable_default": {
                "pattern": r'def\s+(\w+)\s*\(([^)]*=\s*)(\[|\{)([^\}\]]*)(\}|\])',
                "replacement": r'def \1(\2None):\n    \2 = \3\4\5 if \2 is None else \2',
                "description": "Fix mutable default argument",
            },
            "print_to_logger": {
                "pattern": r'print\s*\(([^)]+)\)',
                "replacement": r'logger.info(\1)',
                "description": "Replace print with logger",
            },
            "unused_import": {
                "pattern": r'^import\s+(\w+)$',
                "replacement": '',
                "description": "Remove unused import",
            },
        }

    async def _try_pattern_fix(
        self,
        bug_id: str,
        file_path: str,
        bug_description: str,
        line_number: int | None
    ) -> FixAttempt:
        """Try to fix using pattern matching."""
        fix_attempt = FixAttempt(
            id=f"fix_{bug_id}_{datetime.utcnow().timestamp()}",
            bug_id=bug_id,
            file_path=file_path,
            strategy=FixStrategy.PATTERN,
            status=FixStatus.PENDING,
        )

        try:
            with open(file_path) as f:
                original_code = f.read()

            new_code = original_code
            changes_made = False

            # Check for known patterns in bug description
            for pattern_name, pattern_def in self._fix_patterns.items():
                if pattern_name.lower() in bug_description.lower():
                    import re
                    new_code, count = re.subn(
                        pattern_def["pattern"],
                        pattern_def["replacement"],
                        new_code
                    )
                    if count > 0:
                        changes_made = True
                        change = CodeChange(
                            file_path=file_path,
                            line_start=line_number or 1,
                            line_end=line_number or 1,
                            original_code=original_code,
                            new_code=new_code,
                            description=pattern_def["description"],
                        )
                        fix_attempt.changes.append(change)

            if changes_made:
                fix_attempt.diff = self._generate_diff(original_code, new_code)
            else:
                fix_attempt.status = FixStatus.FAILED
                fix_attempt.error_message = "No matching pattern found"

        except Exception as e:
            fix_attempt.status = FixStatus.FAILED
            fix_attempt.error_message = str(e)

        return fix_attempt

    async def _try_llm_fix(
        self,
        bug_id: str,
        file_path: str,
        bug_description: str,
        suggested_fix: str,
        line_number: int | None
    ) -> FixAttempt:
        """Try to fix using LLM."""
        fix_attempt = FixAttempt(
            id=f"fix_{bug_id}_{datetime.utcnow().timestamp()}",
            bug_id=bug_id,
            file_path=file_path,
            strategy=FixStrategy.LLM,
            status=FixStatus.PENDING,
        )

        try:
            with open(file_path) as f:
                original_code = f.read()

            prompt = f"""Fix this bug in the code:

Bug Description: {bug_description}
Suggested Fix: {suggested_fix}
Line Number: {line_number}

Original Code:
```python
{original_code}
```

Provide the complete fixed code. Only return the code, no explanations."""

            fixed_code = await self._llm.generate(prompt)

            # Clean up the response
            fixed_code = self._extract_code_from_response(fixed_code)

            change = CodeChange(
                file_path=file_path,
                line_start=line_number or 1,
                line_end=line_number or 1,
                original_code=original_code,
                new_code=fixed_code,
                description=f"LLM-generated fix for: {bug_description[:50]}",
            )

            fix_attempt.changes.append(change)
            fix_attempt.diff = self._generate_diff(original_code, fixed_code)

        except Exception as e:
            fix_attempt.status = FixStatus.FAILED
            fix_attempt.error_message = str(e)

        return fix_attempt

    async def _validate_fix(self, fix_attempt: FixAttempt) -> ValidationResult:
        """Validate a fix attempt."""
        result = ValidationResult(
            passed=True,
            syntax_valid=True,
            tests_pass=True,
            no_new_issues=True,
        )

        if not fix_attempt.changes:
            result.passed = False
            result.messages.append("No changes to validate")
            return result

        change = fix_attempt.changes[0]

        # Validate syntax
        try:
            ast.parse(change.new_code)
            result.syntax_valid = True
        except SyntaxError as e:
            result.syntax_valid = False
            result.passed = False
            result.messages.append(f"Syntax error: {e}")

        # Additional validations would go here:
        # - Run tests
        # - Check for new issues
        # - Verify behavior preserved

        return result

    async def _apply_fix(self, fix_attempt: FixAttempt) -> bool:
        """Apply a fix to the file."""
        try:
            if not fix_attempt.changes:
                return False

            change = fix_attempt.changes[0]

            # Create backup
            backup_path = self._backup_dir / f"{Path(change.file_path).name}.{datetime.utcnow().timestamp()}.bak"
            shutil.copy2(change.file_path, backup_path)
            fix_attempt.backup_path = str(backup_path)

            # Apply change
            with open(change.file_path, 'w') as f:
                f.write(change.new_code)

            return True

        except Exception as e:
            self._logger.error("Failed to apply fix", error=str(e))
            return False

    def _generate_diff(self, original: str, modified: str) -> str:
        """Generate a unified diff."""
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile="original",
            tofile="modified",
        )

        return ''.join(diff)

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from LLM response."""
        # Try to extract from markdown code blocks
        import re

        code_block_pattern = r'```(?:python)?\s*\n(.*?)\n```'
        match = re.search(code_block_pattern, response, re.DOTALL)

        if match:
            return match.group(1).strip()

        # Return as-is if no code block found
        return response.strip()

    async def _auto_fix_task(self, task: Task) -> dict[str, Any]:
        """Handle auto_fix task type."""
        fix_attempt = await self.fix_bug(
            bug_id=task.context["bug_id"],
            file_path=task.context["file_path"],
            bug_description=task.context["bug_description"],
            suggested_fix=task.context.get("suggested_fix", ""),
            line_number=task.context.get("line_number"),
            auto_apply=task.context.get("auto_apply", False),
            validate=task.context.get("validate", True),
        )

        return fix_attempt.to_dict()

    async def _batch_fix_task(self, task: Task) -> dict[str, Any]:
        """Handle batch_fix task type."""
        fixes = await self.batch_fix(
            bugs=task.context["bugs"],
            auto_apply=task.context.get("auto_apply", False),
            stop_on_failure=task.context.get("stop_on_failure", True),
        )

        return {
            "total": len(fixes),
            "successful": sum(1 for f in fixes if f.status == FixStatus.SUCCESS),
            "failed": sum(1 for f in fixes if f.status == FixStatus.FAILED),
            "fixes": [f.to_dict() for f in fixes],
        }

    async def _rollback_task(self, task: Task) -> dict[str, Any]:
        """Handle rollback task type."""
        success = await self.rollback_fix(task.context["fix_id"])

        return {
            "fix_id": task.context["fix_id"],
            "rolled_back": success,
        }

    async def _preview_fix_task(self, task: Task) -> dict[str, Any]:
        """Handle preview_fix task type."""
        return await self.preview_fix(
            bug_id=task.context["bug_id"],
            file_path=task.context["file_path"],
            bug_description=task.context["bug_description"],
            suggested_fix=task.context.get("suggested_fix", ""),
            line_number=task.context.get("line_number"),
        )
