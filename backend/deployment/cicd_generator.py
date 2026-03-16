"""
CI/CD Generator for AI Software Factory.

This module provides CI/CD pipeline generation for various platforms
including GitHub Actions, GitLab CI, and Azure DevOps.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from backend.core.logging import get_logger

logger = get_logger(__name__)


class CIPlatform(str, Enum):
    """Supported CI/CD platforms."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    AZURE_DEVOPS = "azure_devops"


class TriggerEvent(str, Enum):
    """Pipeline trigger events."""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    SCHEDULE = "schedule"
    MANUAL = "manual"


@dataclass
class PipelineStep:
    """
    CI/CD pipeline step.
    
    Attributes:
        name: Step name
        command: Command to execute
        working_directory: Working directory
        environment: Environment variables
        condition: Execution condition
    """
    name: str
    command: str
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    condition: Optional[str] = None


@dataclass
class PipelineJob:
    """
    CI/CD pipeline job.
    
    Attributes:
        name: Job name
        runs_on: Runner type
        steps: List of steps
        needs: Job dependencies
        environment: Job environment
        if_condition: Job condition
    """
    name: str
    runs_on: str = "ubuntu-latest"
    steps: List[PipelineStep] = field(default_factory=list)
    needs: List[str] = field(default_factory=list)
    environment: Optional[str] = None
    if_condition: Optional[str] = None


class CICDGenerator:
    """
    CI/CD pipeline generator.
    
    This class provides:
    - GitHub Actions workflow generation
    - GitLab CI configuration generation
    - Azure DevOps pipeline generation
    
    Example:
        >>> generator = CICDGenerator()
        >>> workflow = generator.generate_github_actions_python(
        ...     project_name="myproject"
        ... )
    """
    
    def __init__(self):
        """Initialize the CI/CD generator."""
        self._logger = get_logger(__name__)
    
    def generate_github_actions_python(
        self,
        project_name: str,
        python_versions: Optional[List[str]] = None,
        branches: Optional[List[str]] = None,
        enable_docker: bool = False,
        enable_deploy: bool = False,
        deploy_platform: str = "aws",
    ) -> str:
        """
        Generate GitHub Actions workflow for Python projects.
        
        Args:
            project_name: Project name
            python_versions: Python versions to test
            branches: Branches to trigger on
            enable_docker: Whether to include Docker build
            enable_deploy: Whether to include deployment
            deploy_platform: Deployment platform
            
        Returns:
            GitHub Actions workflow YAML
        """
        python_versions = python_versions or ["3.10", "3.11", "3.12"]
        branches = branches or ["main", "master"]
        
        workflow = f'''name: CI/CD Pipeline

on:
  push:
    branches: {branches}
  pull_request:
    branches: {branches}

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: {python_versions}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{"{{"}} matrix.python-version {{"}}"}}
      uses: actions/setup-python@v5
      with:
        python-version: ${{"{{"}} matrix.python-version {{"}}"}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: mypy . --ignore-missing-imports
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
'''
        
        if enable_docker:
            workflow += f'''
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{"{{"}} github.actor {{"}}"}}
        password: ${{"{{"}} secrets.GITHUB_TOKEN {{"}}"}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{"{{"}} github.repository {{"}}"}}:latest
          ghcr.io/${{"{{"}} github.repository {{"}}"}}:${{"{{"}} github.sha {{"}}"}}
        cache-from: type=gha
        cache-to: type=gha,mode=max
'''
        
        if enable_deploy:
            workflow += f'''
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to {deploy_platform.upper()}
      run: |
        echo "Deploying to {deploy_platform}..."
        # Add deployment commands here
'''
        
        self._logger.info(
            "GitHub Actions workflow generated",
            project=project_name,
            python_versions=python_versions,
            docker=enable_docker,
            deploy=enable_deploy,
        )
        
        return workflow
    
    def generate_github_actions_node(
        self,
        project_name: str,
        node_versions: Optional[List[str]] = None,
        branches: Optional[List[str]] = None,
        package_manager: str = "npm",
    ) -> str:
        """
        Generate GitHub Actions workflow for Node.js projects.
        
        Args:
            project_name: Project name
            node_versions: Node.js versions to test
            branches: Branches to trigger on
            package_manager: Package manager (npm, yarn, pnpm)
            
        Returns:
            GitHub Actions workflow YAML
        """
        node_versions = node_versions or ["18", "20"]
        branches = branches or ["main", "master"]
        
        install_cmd = {
            "npm": "npm ci",
            "yarn": "yarn install --frozen-lockfile",
            "pnpm": "pnpm install --frozen-lockfile",
        }.get(package_manager, "npm ci")
        
        workflow = f'''name: CI/CD Pipeline

on:
  push:
    branches: {branches}
  pull_request:
    branches: {branches}

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: {node_versions}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js ${{"{{"}} matrix.node-version {{"}}"}}
      uses: actions/setup-node@v4
      with:
        node-version: ${{"{{"}} matrix.node-version {{"}}"}}
        cache: '{package_manager}'
    
    - name: Install dependencies
      run: {install_cmd}
    
    - name: Lint
      run: {package_manager} run lint
    
    - name: Type check
      run: {package_manager} run type-check
    
    - name: Test
      run: {package_manager} run test:ci
    
    - name: Build
      run: {package_manager} run build
'''
        
        return workflow
    
    def generate_gitlab_ci_python(
        self,
        project_name: str,
        python_version: str = "3.11",
    ) -> str:
        """
        Generate GitLab CI configuration for Python projects.
        
        Args:
            project_name: Project name
            python_version: Python version
            
        Returns:
            GitLab CI YAML
        """
        return f'''image: python:{python_version}-slim

stages:
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

before_script:
  - python -m venv venv
  - source venv/bin/activate
  - pip install -r requirements.txt
  - pip install -r requirements-dev.txt

test:
  stage: test
  script:
    - flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - mypy . --ignore-missing-imports
    - pytest tests/ -v --cov=. --cov-report=xml
  coverage: '/TOTAL.+ ([0-9]+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main
    - master

deploy:
  stage: deploy
  script:
    - echo "Deploying to production..."
  environment:
    name: production
  only:
    - main
    - master
  when: manual
'''
    
    def generate_azure_pipelines(
        self,
        project_name: str,
        language: str = "python",
    ) -> str:
        """
        Generate Azure DevOps pipeline.
        
        Args:
            project_name: Project name
            language: Programming language
            
        Returns:
            Azure DevOps pipeline YAML
        """
        if language == "python":
            return self._generate_azure_python(project_name)
        elif language == "node":
            return self._generate_azure_node(project_name)
        else:
            return f"# Unsupported language: {language}"
    
    def _generate_azure_python(self, project_name: str) -> str:
        """Generate Azure pipeline for Python."""
        return f'''trigger:
  branches:
    include:
      - main
      - master

pool:
  vmImage: 'ubuntu-latest'

strategy:
  matrix:
    Python310:
      python.version: '3.10'
    Python311:
      python.version: '3.11'
    Python312:
      python.version: '3.12'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '$(python.version)'
  displayName: 'Use Python $(python.version)'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
  displayName: 'Install dependencies'

- script: |
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
  displayName: 'Lint with flake8'

- script: |
    pytest tests/ -v --cov=. --cov-report=xml
  displayName: 'Test with pytest'

- task: PublishTestResults@2
  condition: succeededOrFailed()
  inputs:
    testResultsFiles: '**/test-*.xml'
    testRunTitle: 'Python $(python.version)'

- task: PublishCodeCoverageResults@2
  inputs:
    codeCoverageTool: Cobertura
    summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'
'''
    
    def _generate_azure_node(self, project_name: str) -> str:
        """Generate Azure pipeline for Node.js."""
        return f'''trigger:
  branches:
    include:
      - main
      - master

pool:
  vmImage: 'ubuntu-latest'

strategy:
  matrix:
    Node18:
      node.version: '18.x'
    Node20:
      node.version: '20.x'

steps:
- task: NodeTool@0
  inputs:
    versionSpec: '$(node.version)'
  displayName: 'Use Node.js $(node.version)'

- script: npm ci
  displayName: 'Install dependencies'

- script: npm run lint
  displayName: 'Run linter'

- script: npm run test:ci
  displayName: 'Run tests'

- script: npm run build
  displayName: 'Build'
'''
