"""
Prompt Manager for AI Software Factory.

This module provides prompt template management, variable substitution,
and prompt optimization for different tasks.
"""

from dataclasses import dataclass, field
from string import Template
from typing import Any, Dict, List, Optional

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PromptTemplate:
    """
    Template for LLM prompts.

    Attributes:
        name: Template name/identifier
        template: Template string with $variable placeholders
        description: Description of the template
        variables: List of required variables
        metadata: Additional template metadata
    """
    name: str
    template: str
    description: str = ""
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """
        Render the template with variables.

        Args:
            **kwargs: Variable values

        Returns:
            Rendered prompt string

        Example:
            >>> template = PromptTemplate(
            ...     name="greeting",
            ...     template="Hello, $name!",
            ...     variables=["name"],
            ... )
            >>> prompt = template.render(name="World")
            >>> print(prompt)  # "Hello, World!"
        """
        try:
            t = Template(self.template)
            return t.substitute(**kwargs)
        except KeyError as exc:
            missing_var = str(exc).strip("'")
            logger.error(
                "Missing variable in template",
                template=self.name,
                variable=missing_var,
            )
            raise ValueError(
                f"Missing required variable '{missing_var}' in template '{self.name}'"
            )

    def validate_variables(self, **kwargs) -> List[str]:
        """
        Validate that all required variables are provided.

        Args:
            **kwargs: Variable values to check

        Returns:
            List of missing variable names
        """
        missing = []
        for var in self.variables:
            if var not in kwargs:
                missing.append(var)
        return missing


class PromptManager:
    """
    Manager for prompt templates.

    This class provides:
    - Template registration and retrieval
    - Variable substitution
    - Template categorization by task type
    - Prompt optimization

    Example:
        >>> manager = PromptManager()
        >>> manager.register_template(
        ...     name="code_review",
        ...     template="Review this code: $code",
        ...     variables=["code"],
        ... )
        >>> prompt = manager.render("code_review", code="def foo(): pass")
    """

    def __init__(self):
        """Initialize the prompt manager."""
        self._templates: Dict[str, PromptTemplate] = {}
        self._logger = get_logger(__name__)

        # Initialize default templates
        self._init_default_templates()

    def _init_default_templates(self) -> None:
        """Initialize default prompt templates."""
        default_templates = [
            # Code generation templates
            PromptTemplate(
                name="code_generation",
                template="""You are an expert software engineer. Generate code based on the following requirements:

Requirements:
$requirements

Context:
$context

Please provide:
1. Clean, well-documented code
2. Explanation of the implementation
3. Any assumptions made

Code:""",
                description="Generate code from requirements",
                variables=["requirements", "context"],
            ),

            # Code review templates
            PromptTemplate(
                name="code_review",
                template="""You are a senior code reviewer. Review the following code:

Code:
```$language
$code
```

Please provide:
1. Overall assessment
2. Issues found (critical, warning, suggestion)
3. Best practices followed
4. Recommendations for improvement

Review:""",
                description="Review code for quality and issues",
                variables=["code", "language"],
            ),

            # Architecture design templates
            PromptTemplate(
                name="architecture_design",
                template="""You are a system architect. Design a system architecture for:

Requirements:
$requirements

Constraints:
$constraints

Please provide:
1. High-level architecture overview
2. Component breakdown
3. Data flow description
4. Technology recommendations
5. Scalability considerations

Architecture Design:""",
                description="Design system architecture",
                variables=["requirements", "constraints"],
            ),

            # Requirements analysis templates
            PromptTemplate(
                name="requirements_analysis",
                template="""You are a product manager. Analyze the following product idea:

Idea:
$idea

Please provide:
1. Problem statement
2. Target users
3. Key features
4. Success metrics
5. Potential challenges

Requirements Analysis:""",
                description="Analyze product requirements",
                variables=["idea"],
            ),

            # Testing templates
            PromptTemplate(
                name="test_generation",
                template="""You are a QA engineer. Generate tests for the following code:

Code:
```$language
$code
```

Please provide:
1. Unit tests
2. Edge cases to test
3. Integration test scenarios
4. Test data recommendations

Tests:""",
                description="Generate test cases",
                variables=["code", "language"],
            ),

            # Documentation templates
            PromptTemplate(
                name="documentation",
                template="""You are a technical writer. Create documentation for:

Topic:
$topic

Details:
$details

Please provide:
1. Overview
2. Usage instructions
3. Examples
4. API reference (if applicable)

Documentation:""",
                description="Generate documentation",
                variables=["topic", "details"],
            ),

            # Debugging templates
            PromptTemplate(
                name="debugging",
                template="""You are a debugging expert. Help debug the following issue:

Error:
$error

Code Context:
```$language
$code
```

Please provide:
1. Root cause analysis
2. Solution
3. Prevention recommendations

Debug Analysis:""",
                description="Debug errors and issues",
                variables=["error", "code", "language"],
            ),

            # Refactoring templates
            PromptTemplate(
                name="refactoring",
                template="""You are a code quality expert. Refactor the following code:

Code:
```$language
$code
```

Goals:
$goals

Please provide:
1. Refactored code
2. Explanation of changes
3. Benefits of refactoring

Refactored Code:""",
                description="Refactor code for improvement",
                variables=["code", "language", "goals"],
            ),

            # AI Testing templates
            PromptTemplate(
                name="test_case_generation",
                template="""You are an expert QA engineer. Generate comprehensive test cases for this code:

Code:
```$language
$code
```

Component: $component_name
Type: $component_type

Generate tests including:
1. Happy path tests with valid inputs
2. Edge cases (empty, null, boundary values)
3. Error handling tests (exceptions, invalid inputs)
4. Integration points (mock external dependencies)
5. Performance considerations (if applicable)

Use pytest with:
- Descriptive test names
- Type hints
- Proper fixtures
- Async support where needed

Return only the test code:""",
                description="Generate comprehensive test cases",
                variables=["code", "language", "component_name", "component_type"],
            ),

            PromptTemplate(
                name="bug_detection",
                template="""You are a security and code quality expert. Analyze this code for bugs:

Code:
```$language
$code
```

File: $file_path

Identify:
1. Security vulnerabilities (SQL injection, XSS, etc.)
2. Logic errors and bugs
3. Performance issues
4. Code smells and anti-patterns
5. Type safety issues

For each issue provide:
- Severity (critical/high/medium/low)
- Category (security/logic/performance/maintainability)
- Line number
- Description
- Root cause
- Suggested fix

Return findings as JSON array.""",
                description="Detect bugs and security issues",
                variables=["code", "language", "file_path"],
            ),

            PromptTemplate(
                name="auto_fix",
                template="""You are an expert code repair system. Fix this bug:

Bug Description: $bug_description
Root Cause: $root_cause
Suggested Fix: $suggested_fix

Original Code:
```$language
$code
```

Line: $line_number

Provide the complete fixed code that:
1. Addresses the bug
2. Maintains existing functionality
3. Follows best practices
4. Includes proper error handling

Return only the fixed code section:""",
                description="Generate code fixes",
                variables=["bug_description", "root_cause", "suggested_fix", "code", "language", "line_number"],
            ),

            PromptTemplate(
                name="e2e_test_generation",
                template="""You are an expert in Playwright E2E testing. Generate tests for this user flow:

Page: $page_path
Description: $page_description

User Flow:
$user_flow

Generate Playwright tests that:
1. Navigate to the page
2. Perform each user action
3. Use resilient selectors (data-testid preferred)
4. Include proper waits
5. Assert expected outcomes
6. Handle async operations
7. Include cleanup

Return the complete test file code:""",
                description="Generate E2E tests from user flows",
                variables=["page_path", "page_description", "user_flow"],
            ),

            PromptTemplate(
                name="coverage_recommendation",
                template="""You are a test coverage expert. Analyze uncovered code and recommend tests:

File: $file_path
Current Coverage: $coverage_percentage%

Uncovered Code:
$uncovered_code

Recommend specific test cases to cover:
1. What scenarios are missing
2. Input values to use
3. Expected outcomes
4. Setup requirements (mocks, fixtures)

Provide actionable recommendations:""",
                description="Recommend tests for coverage gaps",
                variables=["file_path", "coverage_percentage", "uncovered_code"],
            ),

            PromptTemplate(
                name="regression_test_from_failure",
                template="""You are a QA engineer specializing in regression tests. Create a test from this failure:

Error: $error_message

Stack Trace:
$stack_trace

Code Context:
```$language
$code
```

Create a pytest test that:
1. Reproduces this exact error
2. Verifies the fix works
3. Tests edge cases
4. Uses proper mocking
5. Has clear assertions

Return the complete test code:""",
                description="Generate regression tests from failures",
                variables=["error_message", "stack_trace", "code", "language"],
            ),
        ]

        for template in default_templates:
            self._templates[template.name] = template

        self._logger.info(
            "Default templates initialized",
            count=len(default_templates),
        )

    def register_template(
        self,
        name: str,
        template: str,
        description: str = "",
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PromptTemplate:
        """
        Register a new prompt template.

        Args:
            name: Template name
            template: Template string with $variable placeholders
            description: Template description
            variables: List of required variables
            metadata: Additional metadata

        Returns:
            Created template

        Example:
            >>> manager.register_template(
            ...     name="custom",
            ...     template="Hello, $name!",
            ...     variables=["name"],
            ... )
        """
        prompt_template = PromptTemplate(
            name=name,
            template=template,
            description=description,
            variables=variables or [],
            metadata=metadata or {},
        )

        self._templates[name] = prompt_template
        self._logger.info("Template registered", template=name)

        return prompt_template

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            Template or None if not found
        """
        return self._templates.get(name)

    def render(self, template_name: str, **kwargs) -> str:
        """
        Render a template with variables.

        Args:
            template_name: Name of the template
            **kwargs: Variable values

        Returns:
            Rendered prompt

        Raises:
            ValueError: If template not found or missing variables

        Example:
            >>> prompt = manager.render("code_review", code="def foo(): pass", language="python")
        """
        template = self._templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Check for missing variables
        missing = template.validate_variables(**kwargs)
        if missing:
            raise ValueError(
                f"Missing required variables for template '{template_name}': {missing}"
            )

        return template.render(**kwargs)

    def list_templates(self) -> List[str]:
        """
        List all registered template names.

        Returns:
            List of template names
        """
        return list(self._templates.keys())

    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """
        Get templates by category.

        Args:
            category: Category name (e.g., "code", "documentation")

        Returns:
            List of templates in the category
        """
        # Simple keyword-based categorization
        category_keywords = {
            "code": ["code", "programming", "function", "class"],
            "documentation": ["doc", "documentation", "readme"],
            "testing": ["test", "testing", "qa"],
            "debugging": ["debug", "error", "fix"],
            "architecture": ["architecture", "design", "system"],
        }

        keywords = category_keywords.get(category, [category])

        matching = []
        for template in self._templates.values():
            template_text = (template.name + " " + template.description).lower()
            if any(kw in template_text for kw in keywords):
                matching.append(template)

        return matching

    def optimize_prompt(self, prompt: str, max_length: int = 4000) -> str:
        """
        Optimize a prompt for better results.

        This is a placeholder for future optimization logic.
        Currently just truncates if too long.

        Args:
            prompt: Original prompt
            max_length: Maximum length

        Returns:
            Optimized prompt
        """
        if len(prompt) <= max_length:
            return prompt

        # Simple truncation with warning
        self._logger.warning(
            "Prompt truncated",
            original_length=len(prompt),
            max_length=max_length,
        )

        return prompt[:max_length] + "\n... [truncated]"
