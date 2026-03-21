"""
Testing Agents for AI-driven autonomous testing.

Each agent specializes in a specific aspect of testing:
- TestGeneratorAgent: Generates test cases from code
- BugDetectorAgent: Detects bugs using multiple strategies
- AutoFixerAgent: Applies automatic fixes to code
- FrontendTesterAgent: Handles E2E and visual testing
"""

from backend.testing.agents.auto_fixer import AutoFixerAgent
from backend.testing.agents.bug_detector import BugDetectorAgent
from backend.testing.agents.frontend_tester import FrontendTesterAgent
from backend.testing.agents.test_generator import TestGeneratorAgent

__all__ = [
    "TestGeneratorAgent",
    "BugDetectorAgent",
    "AutoFixerAgent",
    "FrontendTesterAgent",
]
