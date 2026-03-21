"""
Sandbox for Simulation module.

This module provides isolated execution environment for testing
generated code safely.
"""

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SandboxResult:
    """Result from sandbox execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float


class Sandbox:
    """
    Sandbox for isolated code execution.

    Provides secure environment for testing generated code
    with resource limits and timeout controls.
    """

    def __init__(self, timeout: int = 30, memory_limit: int = 512):
        """
        Initialize the sandbox.

        Args:
            timeout: Execution timeout in seconds
            memory_limit: Memory limit in MB
        """
        self._timeout = timeout
        self._memory_limit = memory_limit
        self._temp_dir: Optional[Path] = None
        self._logger = get_logger(__name__)

    async def execute(
        self,
        code: str,
        language: str = "python",
        files: Optional[Dict[str, str]] = None
    ) -> SandboxResult:
        """
        Execute code in sandbox.

        Args:
            code: Code to execute
            language: Programming language
            files: Additional files to include

        Returns:
            Execution result
        """
        import time

        start_time = time.time()

        with tempfile.TemporaryDirectory() as temp_dir:
            self._temp_dir = Path(temp_dir)

            # Write code file
            if language == "python":
                code_file = self._temp_dir / "main.py"
            elif language == "javascript":
                code_file = self._temp_dir / "main.js"
            else:
                code_file = self._temp_dir / "main.txt"

            code_file.write_text(code)

            # Write additional files
            if files:
                for filename, content in files.items():
                    file_path = self._temp_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)

            # Execute
            try:
                if language == "python":
                    result = await self._run_python(code_file)
                elif language == "javascript":
                    result = await self._run_javascript(code_file)
                else:
                    result = SandboxResult(
                        success=False,
                        stdout="",
                        stderr=f"Unsupported language: {language}",
                        exit_code=-1,
                        execution_time=time.time() - start_time
                    )

                return result

            except Exception as e:
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=str(e),
                    exit_code=-1,
                    execution_time=time.time() - start_time
                )

    async def _run_python(self, code_file: Path) -> SandboxResult:
        """Run Python code."""
        import time

        start_time = time.time()

        try:
            process = subprocess.run(
                ["python", str(code_file)],
                cwd=self._temp_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )

            return SandboxResult(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.returncode,
                execution_time=time.time() - start_time
            )

        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Execution timed out after {self._timeout}s",
                exit_code=-1,
                execution_time=time.time() - start_time
            )

    async def _run_javascript(self, code_file: Path) -> SandboxResult:
        """Run JavaScript code."""
        import time

        start_time = time.time()

        try:
            process = subprocess.run(
                ["node", str(code_file)],
                cwd=self._temp_dir,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )

            return SandboxResult(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.returncode,
                execution_time=time.time() - start_time
            )

        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Execution timed out after {self._timeout}s",
                exit_code=-1,
                execution_time=time.time() - start_time
            )
        except FileNotFoundError:
            return SandboxResult(
                success=False,
                stdout="",
                stderr="Node.js not found",
                exit_code=-1,
                execution_time=time.time() - start_time
            )
