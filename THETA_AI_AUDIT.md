# ThetaAI - Software Factory
## Comprehensive Code-Level Audit & System Documentation

**Document Generated:** March 20, 2026  
**Version:** 1.0.0  
**Status:** Production-Ready Enterprise Platform

---

## Executive Summary

ThetaAI - Software Factory is an **autonomous AI-powered software engineering platform** that transforms product ideas into deployed SaaS applications through a sophisticated orchestration of AI agents, workflows, and validation systems. The platform simulates a complete software development organization with specialized AI agents collaborating through structured workflows to deliver production-ready applications.

### Core Value Proposition
- **Autonomous Development**: End-to-end software development from idea to deployment
- **AI Orchestration**: Multi-agent collaboration using CrewAI and LangGraph
- **Quality Assurance**: Built-in simulation, testing, and validation layers
- **Enterprise-Ready**: Production-grade architecture with monitoring, security, and scalability

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Core Features & Services](#core-features--services)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [AI Agent System](#ai-agent-system)
7. [Workflow Engine](#workflow-engine)
8. [Knowledge & Memory](#knowledge--memory)
9. [Simulation & Testing](#simulation--testing)
10. [Deployment & Infrastructure](#deployment--infrastructure)
11. [Security & Monitoring](#security--monitoring)
12. [API Reference](#api-reference)
13. [Database Schema](#database-schema)
14. [Development Workflow](#development-workflow)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                     │
│  Dashboard | Project Management | Agent Monitoring         │
│  Workflow Visualization | Simulation Results               │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API + WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                  API Gateway (Nginx)                        │
│  Reverse Proxy | Load Balancing | Rate Limiting            │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Backend (FastAPI - Async)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes Layer                                    │  │
│  │  Projects | Agents | Workflows | Deployments        │  │
│  │  Testing | Auth | WebSocket                          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services Layer                                      │  │
│  │  Project Service | Agent Service | Workflow Service  │  │
│  │  Deployment Service | Database Service               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Core Intelligence Layer                             │  │
│  │  Workflow Engine | Agent OS | Brain | Simulation     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
┌───────▼────┐ ┌────▼─────┐ ┌───▼────┐ ┌───▼────┐
│ PostgreSQL │ │  Redis   │ │ Ollama │ │Prometheus│
│ + pgvector │ │ Cache/Queue│ │  LLM  │ │ Metrics │
└────────────┘ └──────────┘ └────────┘ └──────────┘
```

### Architectural Principles

1. **Layered Architecture**: Clear separation of concerns across presentation, business logic, and data layers
2. **Event-Driven**: Asynchronous communication via Redis and WebSockets
3. **Microservices-Ready**: Modular design enabling future service decomposition
4. **Observability-First**: Built-in logging, metrics, and health monitoring
5. **Security-by-Design**: Multi-layer security with authentication, authorization, and input validation

---

## Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.109.0 | Async web framework |
| **Language** | Python | 3.11+ | Core programming language |
| **Workflow** | LangGraph | 0.0.40 | State machine orchestration |
| **Agents** | CrewAI | 0.28.8 | Agent role management |
| **Database** | PostgreSQL | 15 | Primary data store |
| **Vector DB** | pgvector | 0.2.x | Semantic search/embeddings |
| **Cache** | Redis | 7 | Caching & task queues |
| **LLM** | Ollama | latest | Local LLM inference |
| **ORM** | SQLAlchemy | 2.0.36 | Async database ORM |
| **Migration** | Alembic | 1.13.1 | Database migrations |
| **Validation** | Pydantic | 2.5.3 | Data validation |
| **Logging** | StructLog | 24.1.0 | Structured logging |
| **Auth** | python-jose | 3.3.0 | JWT authentication |
| **Metrics** | Prometheus | 0.19.0 | Monitoring & metrics |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | Next.js | 16.1.6 | React framework |
| **Language** | TypeScript | 5.x | Type-safe JavaScript |
| **UI Library** | React | 19.2.3 | Component framework |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS |
| **Components** | shadcn/ui | latest | UI component library |
| **State** | TanStack Query | 5.90.21 | Server state management |
| **Charts** | Recharts | 3.8.0 | Data visualization |
| **Animations** | Framer Motion | 12.36.0 | UI animations |
| **Icons** | Lucide React | 0.577.0 | Icon library |
| **Theme** | next-themes | 0.4.6 | Dark/light mode |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Docker Compose | Multi-container management |
| **Reverse Proxy** | Nginx | API gateway & load balancing |
| **Monitoring** | Prometheus + Grafana | Metrics & dashboards |
| **CI/CD** | GitHub Actions | Automated testing & deployment |

---

## Core Features & Services

### 1. Project Management System

**Purpose**: Complete lifecycle management for AI-driven software development projects.

**Key Capabilities**:
- Project creation with requirements definition
- Status tracking (Draft → Active → Completed)
- Phase progression monitoring
- Progress percentage calculation
- Metadata and documentation storage

**Service Implementation**:
- [`ProjectService`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\services\project_service.py) - Business logic layer
- RESTful API with full CRUD operations
- Database persistence with async support

**API Endpoints**:
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project details
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project
- `POST /api/v1/projects/{id}/activate` - Activate project

---

### 2. AI Agent Orchestration

**Purpose**: Manage autonomous AI agents with specialized roles and capabilities.

**Agent Roles**:
- **CEO Agent**: Strategic decision-making and project oversight
- **Product Manager**: Requirements gathering and user story creation
- **Architect**: System design and technology selection
- **Backend Engineer**: API and database implementation
- **Frontend Engineer**: UI/UX implementation
- **DevOps Engineer**: Deployment and infrastructure setup
- **QA Engineer**: Testing and quality assurance

**Key Features**:
- Agent registration and discovery via [`AgentRegistry`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\agent_registry.py)
- Capability-based agent selection
- Task assignment and tracking
- Real-time status monitoring
- Hierarchical crew assembly

**Crew Configurations**:
- [`CEO Crew`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\ceo_crew.py) - Strategic planning
- [`Engineering Crew`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\engineering_crew.py) - Implementation
- [`Planning Crew`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\planning_crew.py) - Requirements & architecture
- [`Design Crew`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\design_crew.py) - UX/UI design
- [`Implementation Crew`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\implementation_crew.py) - Code generation
- [`Deployment Crew`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\deployment_crew.py) - Production deployment

---

### 3. Workflow Engine (LangGraph)

**Purpose**: Orchestrate the software development lifecycle through state-managed workflows.

**Workflow States** (8-Phase Process):
1. **IDEA** - Initial concept and validation
2. **REQUIREMENTS** - Detailed requirements gathering
3. **ARCHITECTURE** - System design and tech stack
4. **IMPLEMENTATION** - Code generation
5. **TESTING** - Quality assurance
6. **DEPLOYMENT** - Production release
7. **COMPLETE** - Successful delivery
8. **FAILED** - Error state with rollback

**Key Components**:
- [`WorkflowEngine`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\workflow_engine.py) - Main orchestrator
- [`StateMachine`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\state_machine.py) - State transitions
- [`TaskManager`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\task_manager.py) - Task queue management
- [`CrewIntegration`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\crew_integration.py) - CrewAI bridge

**Features**:
- Sequential and parallel task execution
- Conditional phase transitions
- Retry logic with exponential backoff
- State persistence and recovery
- Real-time progress tracking

---

### 4. AgentOS (Runtime Environment)

**Purpose**: Provide runtime infrastructure for agent execution and management.

**Core Components**:
- [`Scheduler`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agent_os\scheduler.py) - Cron-like task scheduling
- [`TaskQueue`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agent_os\task_queue.py) - Redis-based queue system
- [`WorkerPool`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agent_os\worker_pool.py) - Dynamic worker scaling
- [`ResourceManager`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agent_os\resource_manager.py) - Resource allocation
- [`ErrorHandler`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agent_os\error_handler.py) - Failure recovery
- [`CrewExecutor`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agent_os\crew_executor.py) - Crew execution wrapper

**Capabilities**:
- Priority-based task execution
- Dynamic worker scaling
- Health monitoring
- Graceful shutdown
- Circuit breaker pattern
- Dead letter queue for failures

---

### 5. Project Brain (Knowledge System)

**Purpose**: Centralized knowledge repository with semantic search and RAG capabilities.

**Knowledge Layers**:
- **Product Layer**: Requirements, user stories, feature specs
- **Architecture Layer**: Design decisions, diagrams, API specs
- **Implementation Layer**: Code documentation, comments, READMEs
- **Deployment Layer**: Infrastructure configs, environment variables

**Key Components**:
- [`KnowledgeBase`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\knowledge_base.py) - Knowledge storage
- [`RAGPipeline`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\rag_pipeline.py) - Retrieval-augmented generation
- [`RetrievalEngine`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\retrieval.py) - Semantic search
- [`ContextManager`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\context_manager.py) - Conversation context
- [`MemoryStore`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\memory_store.py) - Short-term memory
- [`VectorStore`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\vector_store.py) - Vector embeddings
- [`Embeddings`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\embeddings.py) - Embedding generation

**Features**:
- Semantic search using pgvector
- Context-aware responses
- Source attribution
- Conversation history tracking
- CrewAI memory tool integration

---

### 6. Simulation Layer

**Purpose**: Validate designs, code, and infrastructure before actual deployment.

**Simulation Types**:

**UX Simulation**:
- User journey validation
- Accessibility compliance
- Responsive design verification
- Navigation flow testing

**Architecture Simulation**:
- Component interaction modeling
- Performance prediction
- Scalability analysis
- Bottleneck detection

**API Simulation**:
- Contract validation
- Load testing simulation
- Error scenario testing
- Response time analysis

**Infrastructure Simulation**:
- Resource requirement estimation
- Cost prediction
- Deployment feasibility
- Scaling capacity

**Key Components**:
- [`Sandbox`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\sandbox.py) - Isolated code execution
- [`SecurityScanner`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\security_scanner.py) - Security validation
- [`PerformanceTester`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\performance_tester.py) - Performance analysis
- [`IntegrationTester`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\integration_tester.py) - Integration testing
- [`ValidationEngine`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\validation_engine.py) - Validation logic
- [`ReportGenerator`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\report_generator.py) - Report generation

---

### 7. Intelligent Testing System

**Purpose**: Advanced testing framework with self-healing capabilities.

**Key Features**:
- **Self-Healing Tests**: Automatic retry with exponential backoff
- **Flaky Test Detection**: Identify and quarantine unstable tests
- **Smart Test Ordering**: Priority-based execution with failure history
- **Parallel Execution**: Concurrent test runs with isolation
- **Selector Healing**: Auto-fix broken E2E selectors

**Components**:
- [`SelfHealingRunner`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\testing\self_healing_runner.py) - Intelligent test execution
- [`IntelligenceEngine`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\testing\intelligence_engine.py) - Test case generation
- [`CoverageAnalyzer`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\testing\coverage_analyzer.py) - Coverage analysis

**Testing Agents**:
- Unit test generation
- Integration test creation
- E2E test automation
- Performance testing
- Security scanning

---

### 8. Code Generation System

**Purpose**: Automated code generation with templates and quality checks.

**Supported Languages**:
- Python (FastAPI, Django, Flask)
- TypeScript/JavaScript (React, Next.js, Express)
- HTML/CSS
- SQL
- Dockerfile
- YAML/JSON configurations
- Markdown

**Templates**:
- FastAPI endpoints and models
- React components
- Database schemas
- Docker configurations
- Test files (pytest)
- CI/CD pipelines

**Key Components**:
- [`CodeGenerator`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\codegen\generator.py) - Main generation engine
- [`FileManager`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\codegen\file_manager.py) - File operations
- [`QualityChecker`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\codegen\quality_checker.py) - Code validation
- [`Simulation`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\codegen\simulation.py) - Code simulation

**Features**:
- Template-based generation
- Syntax validation
- Code formatting
- Quality assurance
- Multi-language support

---

### 9. Deployment Engine

**Purpose**: Automated deployment orchestration across environments.

**Deployment Environments**:
- Development (dev)
- Staging (staging)
- Production (prod)

**Deployment Steps**:
1. Build - Compile and package application
2. Test - Run automated test suite
3. Infrastructure - Provision resources
4. Deploy - Roll out application
5. Verify - Health check validation

**Key Components**:
- [`DeploymentOrchestrator`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\orchestrator.py) - Main orchestrator
- [`DockerGenerator`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\docker_generator.py) - Docker config generation
- [`TerraformGenerator`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\terraform_generator.py) - Infrastructure as Code
- [`CICDGenerator`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\cicd_generator.py) - CI/CD pipeline generation
- [`Environment`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\environment.py) - Environment management

**Features**:
- Rollback capabilities
- Blue-green deployment support
- Canary releases
- Health monitoring
- Automated recovery

**API Endpoints**:
- `POST /api/v1/deployments` - Create deployment
- `GET /api/v1/deployments` - List deployments
- `GET /api/v1/deployments/{id}` - Get deployment status
- `POST /api/v1/deployments/{id}/cancel` - Cancel deployment

---

### 10. Authentication & Authorization

**Purpose**: Secure access control and user management.

**Authentication Methods**:
- JWT token-based authentication
- Session management
- API key support for services

**Authorization**:
- Role-based access control (RBAC)
- Permission-based authorization
- Resource-level permissions

**Key Components**:
- [`AuthService`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\services\auth_service.py) - Authentication logic
- [`Auth API`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\api\routes\auth.py) - Auth endpoints

**Security Features**:
- Password hashing with bcrypt
- Token expiration and refresh
- CORS configuration
- Rate limiting
- Input validation

---

## Backend Architecture

### Directory Structure

```
backend/
├── main.py                          # FastAPI application entry point
├── core/                            # Core utilities
│   ├── config.py                    # Configuration management
│   ├── logging.py                   # Logging setup
│   └── exceptions.py                # Custom exceptions
├── api/                             # API layer
│   ├── routes/                      # Route handlers
│   │   ├── projects.py
│   │   ├── agents.py
│   │   ├── workflows.py
│   │   ├── deployments.py
│   │   ├── testing.py
│   │   ├── auth.py
│   │   └── websocket.py
│   ├── models.py                    # API data models
│   └── dependencies.py              # Dependency injection
├── services/                        # Business logic
│   ├── project_service.py
│   ├── agent_service.py
│   ├── workflow_service.py
│   ├── deployment_service.py
│   └── database_services.py
├── agents/                          # AI agent system
│   ├── base_agent.py
│   ├── agent_registry.py
│   ├── model_router.py
│   ├── crews/                       # Crew configurations
│   └── roles/                       # Agent role definitions
├── workflows/                       # Workflow orchestration
│   ├── workflow_engine.py
│   ├── state_machine.py
│   ├── task_manager.py
│   └── crew_integration.py
├── agent_os/                        # Agent runtime
│   ├── scheduler.py
│   ├── task_queue.py
│   ├── worker_pool.py
│   └── resource_manager.py
├── brain/                           # Knowledge system
│   ├── knowledge_base.py
│   ├── rag_pipeline.py
│   ├── retrieval.py
│   └── vector_store.py
├── simulation/                      # Validation layer
│   ├── sandbox.py
│   ├── security_scanner.py
│   └── performance_tester.py
├── testing/                         # Testing framework
│   ├── self_healing_runner.py
│   ├── intelligence_engine.py
│   └── coverage_analyzer.py
├── codegen/                         # Code generation
│   ├── generator.py
│   ├── file_manager.py
│   └── quality_checker.py
├── deployment/                      # Deployment system
│   ├── orchestrator.py
│   ├── docker_generator.py
│   └── terraform_generator.py
├── db/                              # Database layer
│   ├── session.py
│   └── base.py
├── models/                          # Database models
│   ├── task.py
│   └── workflow.py
├── middleware/                      # Middleware
│   ├── error_handler.py
│   ├── request_logging.py
│   └── correlation_id.py
└── utils/                           # Utilities
    ├── validators.py
    ├── security.py
    └── formatters.py
```

### Middleware Stack

**Execution Order** (outermost to innermost):

1. **ErrorHandlerMiddleware** - Global exception handling
2. **RequestLoggingMiddleware** - Request/response logging
3. **CorrelationIdMiddleware** - Request tracing IDs
4. **CORS Middleware** - Cross-origin resource sharing

### Error Handling

**Exception Hierarchy**:
- `BackendException` - Base exception
  - `ValidationError` - Input validation errors
  - `NotFoundException` - Resource not found
  - `AuthenticationError` - Auth failures
  - `AuthorizationError` - Permission denied
  - `WorkflowError` - Workflow execution errors
  - `AgentError` - Agent execution errors

**Error Response Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": {},
    "correlation_id": "uuid"
  }
}
```

### Logging System

**Features**:
- Structured JSON logging
- Correlation ID tracking
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Environment-based configuration
- Performance metrics logging

**Log Format**:
```json
{
  "timestamp": "2026-03-20T10:00:00Z",
  "level": "INFO",
  "logger": "backend.api.routes.projects",
  "event": "Project created",
  "project_id": "uuid",
  "user_id": "user-uuid",
  "correlation_id": "corr-uuid"
}
```

---

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   └── app/
│       ├── layout.tsx                    # Root layout
│       ├── page.tsx                      # Home page
│       ├── globals.css                   # Global styles
│       ├── (dashboard)/                  # Dashboard section
│       │   ├── layout.tsx
│       │   ├── page.tsx                  # Dashboard home
│       │   ├── projects/
│       │   ├── agents/
│       │   ├── workflows/
│       │   ├── simulations/
│       │   └── deployments/
│       └── test-actions/                 # Test utilities
├── public/                               # Static assets
├── components.json                       # Component config
└── next.config.ts                        # Next.js config
```

### Key Pages

**Dashboard** (`/(dashboard)/page.tsx`):
- Project overview
- System statistics
- Recent activity feed
- Quick actions

**Projects** (`/(dashboard)/projects/`):
- Project list view
- Project creation form
- Project detail page
- Phase progression tracker

**Agents** (`/(dashboard)/agents/`):
- Agent registry display
- Agent status monitoring
- Crew assignments
- Capability browser

**Workflows** (`/(dashboard)/workflows/`):
- Workflow state visualization
- Phase transition history
- Current phase details
- Workflow execution logs

**Simulations** (`/(dashboard)/simulations/`):
- Run new simulations
- View simulation results
- Approval/rejection interface
- Historical reports

### Component Library

**UI Components** (shadcn/ui):
- Buttons, inputs, forms
- Dialogs, modals, popovers
- Tables, lists, grids
- Cards, badges, avatars
- Tabs, accordions, dropdowns
- Toasts, alerts, notifications

**Custom Components**:
- `IdeaForm` - Project idea submission
- `ActivityFeed` - Real-time activity stream
- `WorkflowViewer` - LangGraph visualization
- `CrewStatus` - Agent crew status
- `ArchitectureViewer` - Mermaid diagrams
- `ProjectCard` - Project summary display
- `PhaseProgress` - Phase completion indicator

### State Management

**TanStack Query** (React Query):
- Server state management
- Automatic caching
- Background refetching
- Optimistic updates
- Error handling

**Local State**:
- Component-level state with React hooks
- Form state management
- UI state (modals, toggles, etc.)

### Real-Time Features

**WebSocket Integration**:
- Live activity feed updates
- Agent status changes
- Workflow state transitions
- Deployment progress tracking

---

## AI Agent System

### Agent Architecture

**Base Agent Class** ([`base_agent.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\base_agent.py)):

```python
class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    
    def __init__(
        self,
        agent_id: str,
        role: str,
        capabilities: List[str]
    )
    
    async def execute_task(self, task: Task) -> TaskResult
    async def query_memory(self, query: str) -> MemoryResult
    @property
    def identity(self) -> AgentIdentity
```

### Agent Registry

**Singleton Pattern** ([`agent_registry.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\agent_registry.py)):

**Operations**:
- `register_agent(agent)` - Register agent
- `unregister_agent(agent_id)` - Unregister agent
- `get_agent(agent_id)` - Get agent by ID
- `get_agents_by_role(role)` - Filter by role
- `get_agents_by_capability(capability)` - Filter by capability
- `list_agents()` - List all agents

### Model Router

**LLM Abstraction** ([`model_router.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\model_router.py)):

**Supported Models** (via Ollama):
- Qwen (coding specialist)
- DeepSeek Coder
- Llama series
- Mixtral

**Features**:
- Model selection based on task type
- Automatic retry on failure
- Response streaming
- Token counting and cost tracking

### Crew Configurations

**CEO Crew** ([`ceo_crew.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\ceo_crew.py)):
- **Mission**: Strategic oversight and decision-making
- **Tasks**: Project approval, resource allocation, priority setting
- **Output**: Strategic plans, approvals, directives

**Engineering Crew** ([`engineering_crew.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\engineering_crew.py)):
- **Mission**: Technical implementation
- **Tasks**: Code generation, API design, database modeling
- **Output**: Source code, technical documentation

**Planning Crew** ([`planning_crew.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\planning_crew.py)):
- **Mission**: Requirements and architecture
- **Tasks**: Requirement analysis, tech stack selection
- **Output**: Requirements docs, architecture diagrams

**Design Crew** ([`design_crew.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\design_crew.py)):
- **Mission**: UX/UI design
- **Tasks**: User journey mapping, wireframing
- **Output**: Design mockups, style guides

**Implementation Crew** ([`implementation_crew.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\implementation_crew.py)):
- **Mission**: Code implementation
- **Tasks**: Feature development, bug fixes
- **Output**: Working code, unit tests

**Deployment Crew** ([`deployment_crew.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\crews\deployment_crew.py)):
- **Mission**: Production deployment
- **Tasks**: Infrastructure setup, CI/CD configuration
- **Output**: Deployed application, monitoring setup

---

## Workflow Engine

### State Machine

**States and Transitions** ([`state_machine.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\state_machine.py)):

```
IDEA ──► REQUIREMENTS ──► ARCHITECTURE ──► IMPLEMENTATION
  │            │               │                │
  ▼            ▼               ▼                ▼
FAILED      FAILED          FAILED           FAILED
                                        │
                                        ▼
                                   TESTING ──► DEPLOYMENT ──► COMPLETE
                                     │            │
                                     ▼            ▼
                                   FAILED      FAILED
```

**Phase Status**:
- `PENDING` - Not yet started
- `IN_PROGRESS` - Currently executing
- `COMPLETED` - Successfully finished
- `FAILED` - Error occurred
- `ROLLED_BACK` - Reverted after failure

### Workflow Execution

**Engine Operations** ([`workflow_engine.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\workflow_engine.py)):

1. **Initialize**: Create workflow state
2. **Execute Phase**: Run phase-specific tasks
3. **Evaluate**: Check completion criteria
4. **Transition**: Move to next phase or rollback
5. **Repeat**: Continue until COMPLETE or FAILED

**Phase Handlers**:
- `_execute_idea_phase()` - Initialize project
- `_execute_requirements_phase()` - Gather requirements with CrewAI
- `_execute_architecture_phase()` - Design architecture with CrewAI
- `_execute_implementation_phase()` - Generate code with CrewAI
- `_execute_testing_phase()` - Run tests and validation
- `_execute_deployment_phase()` - Deploy with CrewAI
- `_execute_complete_phase()` - Finalize project
- `_execute_failed_phase()` - Handle failures

### Task Management

**Task Lifecycle** ([`task_manager.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\task_manager.py)):

1. **Creation**: Task generated from workflow
2. **Assignment**: Routed to appropriate agent/crew
3. **Execution**: Agent processes task
4. **Validation**: Output verified
5. **Completion**: Task marked done
6. **Integration**: Results merged into state

**Task Priorities**:
- CRITICAL (0) - Blocker tasks
- HIGH (1) - Important tasks
- MEDIUM (2) - Standard tasks
- LOW (3) - Background tasks

---

## Knowledge & Memory

### Knowledge Base

**Storage Structure** ([`knowledge_base.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\knowledge_base.py)):

**Document Types**:
- Text documents (requirements, specs)
- Code files (source code, configs)
- Diagrams (architecture, flows)
- Metadata (tags, timestamps, sources)

**Operations**:
- `add_document()` - Store knowledge
- `delete_document()` - Remove knowledge
- `update_document()` - Modify knowledge
- `search()` - Semantic search
- `get_by_tag()` - Filter by tags

### RAG Pipeline

**Query Flow** ([`rag_pipeline.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\rag_pipeline.py)):

1. **Input**: User query received
2. **Context**: Retrieve conversation history
3. **Retrieval**: Search knowledge base (top-k)
4. **Augmentation**: Build prompt with context
5. **Generation**: LLM generates response
6. **Output**: Return response with citations

**Prompt Structure**:
```
System: You are a helpful assistant. Use provided context.

Context:
[Document 1]: <retrieved text>
[Document 2]: <retrieved text>

Conversation History:
user: <previous question>
assistant: <previous answer>

User: <current question>

Assistant:
```

### Vector Store

**Implementation** ([`vector_store.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\vector_store.py)):

**Database Schema**:
```sql
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    document_id UUID,
    embedding VECTOR(1536),  -- pgvector
    text TEXT,
    metadata JSONB,
    created_at TIMESTAMP
);
```

**Operations**:
- `insert_embedding()` - Store vector
- `similarity_search()` - Find similar vectors
- `delete_embedding()` - Remove vector
- `batch_insert()` - Bulk insert

### Context Management

**Conversation Context** ([`context_manager.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\context_manager.py)):

**Features**:
- Conversation history tracking
- Context window management
- Message pruning (FIFO)
- Context serialization

**Message Format**:
```python
{
    "role": "user|assistant|system",
    "content": "message text",
    "timestamp": "ISO timestamp",
    "metadata": {}
}
```

---

## Simulation & Testing

### Sandbox Execution

**Isolated Environment** ([`sandbox.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\sandbox.py)):

**Security Features**:
- Temporary directory isolation
- Timeout enforcement (default: 30s)
- Memory limits (default: 512MB)
- No network access
- File system restrictions

**Supported Languages**:
- Python (via subprocess)
- JavaScript/Node.js
- Text output for others

**Execution Result**:
```python
SandboxResult(
    success=True|False,
    stdout="output",
    stderr="errors",
    exit_code=0,
    execution_time=1.23
)
```

### Self-Healing Tests

**Intelligent Recovery** ([`self_healing_runner.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\testing\self_healing_runner.py)):

**Retry Strategy**:
- Exponential backoff: delay = base_delay * 2^(attempt-1)
- Max retries: 3 (configurable)
- Jitter: Random variation to prevent thundering herd

**Healing Strategies**:
1. **Timing Issues**: Add waits, increase timeouts
2. **Selector Issues**: Find alternative selectors
3. **Network Issues**: Retry with backoff

**Flaky Test Detection**:
- Track failure rate over last 10 runs
- Threshold: >20% failure rate = flaky
- Auto-quarantine flaky tests
- Notification on quarantine

**Test Execution Flow**:
```
Test Start
    ↓
Execute Test
    ↓
Success? ──► Record Result ──► Done
    ↓
Failure
    ↓
Apply Healing Strategy
    ↓
Retry (up to max_retries)
    ↓
Still Failed? ──► Mark Flaky/Failed
```

### Coverage Analysis

**Comprehensive Coverage** ([`coverage_analyzer.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\testing\coverage_analyzer.py)):

**Coverage Types**:
- Line coverage
- Branch coverage
- Function coverage
- Statement coverage
- Path coverage

**Analysis Features**:
- Per-file coverage reports
- Coverage trends over time
- Uncovered code identification
- Coverage threshold enforcement
- Integration with CI/CD

---

## Deployment & Infrastructure

### Docker Architecture

**Services** ([`docker-compose.yml`](c:\Users\DELL\Projects\ThetaAI - Software Factory\docker-compose.yml)):

1. **Backend** (port 8000)
   - FastAPI application
   - Async workers
   - Health checks

2. **Frontend** (port 3000)
   - Next.js application
   - SSR support
   - Static asset serving

3. **PostgreSQL** (port 5432)
   - Primary database
   - pgvector extension
   - Persistent volumes

4. **Redis** (port 6379)
   - Cache layer
   - Task queues
   - Session storage

5. **Ollama** (port 11434)
   - LLM inference
   - Model management
   - GPU support (optional)

6. **Nginx** (port 80)
   - Reverse proxy
   - Load balancing
   - SSL termination

7. **Prometheus** (port 9090)
   - Metrics collection
   - Time-series database
   - Alerting

8. **Grafana** (port 3001)
   - Dashboards
   - Visualization
   - Alerting rules

### Deployment Orchestrator

**Deployment Process** ([`orchestrator.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\orchestrator.py)):

**Steps**:
1. **Build** - Compile and package
2. **Test** - Run test suite
3. **Infrastructure** - Provision resources
4. **Deploy** - Roll out application
5. **Verify** - Health checks

**Deployment Strategies**:
- Rolling deployment (default)
- Blue-green deployment
- Canary releases
- A/B testing support

**Rollback Process**:
```
Rollback Triggered
    ↓
Create Rollback Deployment
    ↓
Deploy Previous Stable Version
    ↓
Verify Health
    ↓
Update DNS/Routing
    ↓
Mark Original as ROLLED_BACK
```

### Infrastructure as Code

**Docker Generator** ([`docker_generator.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\docker_generator.py)):

**Generated Artifacts**:
- Dockerfile (multi-stage)
- docker-compose.yml
- .dockerignore
- Health check scripts

**Terraform Generator** ([`terraform_generator.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\terraform_generator.py)):

**Generated Resources**:
- Cloud provider config (AWS/Azure/GCP)
- VPC and networking
- Database instances
- Load balancers
- Storage buckets
- IAM roles and policies

**CI/CD Generator** ([`cicd_generator.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\cicd_generator.py)):

**Generated Pipelines**:
- GitHub Actions workflows
- GitLab CI pipelines
- Jenkins pipelines
- Pre-commit hooks
- Linting and formatting
- Test execution
- Build and push containers
- Deployment steps

---

## Security & Monitoring

### Security Features

**Authentication**:
- JWT tokens with expiration
- Refresh token rotation
- API key authentication for services
- Password hashing (bcrypt)

**Authorization**:
- Role-based access control (RBAC)
- Permission-based authorization
- Resource-level permissions
- Ownership validation

**Input Validation**:
- Pydantic model validation
- SQL injection prevention
- XSS protection
- CSRF protection

**Infrastructure Security**:
- Network segmentation
- Container isolation
- Secret management
- Encrypted communications (TLS)

### Monitoring Stack

**Prometheus Metrics**:

**Application Metrics**:
- Request rate (requests/sec)
- Response time (p50, p95, p99)
- Error rate (errors/sec)
- Active connections
- Queue depth

**Business Metrics**:
- Projects created
- Workflows executed
- Agents active
- Tasks completed
- Deployments successful

**System Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Container health

**Grafana Dashboards**:

1. **System Overview**
   - Service health status
   - Resource utilization
   - Request throughput
   - Error rates

2. **Application Performance**
   - API endpoint latency
   - Database query times
   - Cache hit rates
   - Queue processing times

3. **Workflow Monitoring**
   - Active workflows
   - Phase durations
   - Success/failure rates
   - Agent utilization

4. **Agent Activity**
   - Active agents
   - Task completion rates
   - Average task duration
   - Error rates by agent type

5. **Deployment Tracking**
   - Deployment frequency
   - Deployment duration
   - Success rates
   - Rollback incidents

### Health Checks

**Endpoints**:

1. **`GET /health`** - Basic health
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "timestamp": "2026-03-20T10:00:00Z"
   }
   ```

2. **`GET /ready`** - Readiness probe
   - Database connection
   - Redis connection
   - Ollama connection
   - All dependencies healthy

3. **`GET /live`** - Liveness probe
   - Application is running
   - Not in deadlock state

**Startup Checks** ([`main.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\main.py)):

```python
# Database connection
await init_db()

# Redis connection
redis_client = redis.from_url(REDIS_URL)
await redis_client.ping()

# Ollama connection
urllib.request.urlopen(f"{OLLAMA_URL}/api/tags")
```

---

## API Reference

### Base URL

- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

### Authentication Endpoints

#### POST `/api/v1/auth/register`
Register new user

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "User Name"
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "token": "jwt_token"
}
```

#### POST `/api/v1/auth/login`
User login

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "token": "jwt_token",
  "refresh_token": "refresh_jwt"
}
```

### Project Endpoints

#### POST `/api/v1/projects`
Create new project

**Request**:
```json
{
  "name": "My SaaS App",
  "description": "A revolutionary SaaS product",
  "requirements": "Must have user auth, payments, dashboard",
  "tech_stack": {
    "frontend": "react",
    "backend": "fastapi",
    "database": "postgresql"
  }
}
```

**Response**:
```json
{
  "id": "proj-uuid",
  "name": "My SaaS App",
  "description": "A revolutionary SaaS product",
  "status": "draft",
  "current_phase": "idea",
  "progress_percent": 0.0,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z"
}
```

#### GET `/api/v1/projects`
List projects

**Query Parameters**:
- `status` (optional) - Filter by status
- `skip` (default: 0) - Pagination offset
- `limit` (default: 100) - Page size

**Response**:
```json
[
  {
    "id": "proj-uuid",
    "name": "Project Name",
    "status": "active",
    "current_phase": "implementation",
    "progress_percent": 45.5
  }
]
```

#### GET `/api/v1/projects/{project_id}`
Get project details

**Response**:
```json
{
  "id": "proj-uuid",
  "name": "My SaaS App",
  "description": "A revolutionary SaaS product",
  "requirements": "Detailed requirements...",
  "status": "active",
  "current_phase": "implementation",
  "progress_percent": 45.5,
  "tech_stack": {
    "frontend": "react",
    "backend": "fastapi"
  },
  "phases": {
    "idea": {"status": "completed"},
    "requirements": {"status": "completed"},
    "architecture": {"status": "completed"},
    "implementation": {"status": "in_progress"}
  },
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T12:00:00Z"
}
```

#### PATCH `/api/v1/projects/{project_id}`
Update project

**Request**:
```json
{
  "name": "Updated Project Name",
  "status": "active"
}
```

#### DELETE `/api/v1/projects/{project_id}`
Delete project

**Response**: `204 No Content`

#### POST `/api/v1/projects/{project_id}/activate`
Activate project

**Response**: Updated project object

### Agent Endpoints

#### GET `/api/v1/agents`
List all agents

**Response**:
```json
[
  {
    "agent_id": "agent-uuid",
    "name": "CEO Agent",
    "role": "ceo",
    "capabilities": ["strategic_planning", "decision_making"],
    "status": "idle",
    "current_task": null,
    "last_active": "2026-03-20T10:00:00Z"
  }
]
```

#### GET `/api/v1/agents/{agent_id}`
Get agent details

#### GET `/api/v1/agents/roles/available`
List available agent roles

**Response**:
```json
["ceo", "product_manager", "architect", "backend_engineer", "frontend_engineer", "devops_engineer"]
```

#### POST `/api/v1/agents/{agent_id}/tasks`
Assign task to agent

**Request**:
```json
{
  "task_type": "code_review",
  "task_description": "Review the authentication module",
  "priority": "high"
}
```

**Response**:
```json
{
  "task_id": "task-uuid",
  "agent_id": "agent-uuid",
  "status": "accepted",
  "message": "Task assigned successfully"
}
```

### Workflow Endpoints

#### GET `/api/v1/workflows`
List workflows

#### GET `/api/v1/workflows/{workflow_id}`
Get workflow details

#### POST `/api/v1/workflows/{workflow_id}/execute`
Execute workflow

#### POST `/api/v1/workflows/{workflow_id}/pause`
Pause workflow

#### POST `/api/v1/workflows/{workflow_id}/resume`
Resume workflow

### Deployment Endpoints

#### POST `/api/v1/deployments`
Create deployment

**Request**:
```json
{
  "project_id": "proj-uuid",
  "environment": "staging",
  "version": "1.0.0",
  "config": {
    "replicas": 3,
    "resources": {
      "cpu": "500m",
      "memory": "512Mi"
    }
  }
}
```

**Response**:
```json
{
  "deployment_id": "deploy-uuid",
  "project_id": "proj-uuid",
  "environment": "staging",
  "version": "1.0.0",
  "status": "pending",
  "steps": [
    {"name": "Build", "status": "pending"},
    {"name": "Test", "status": "pending"},
    {"name": "Deploy", "status": "pending"},
    {"name": "Verify", "status": "pending"}
  ],
  "started_at": "2026-03-20T10:00:00Z"
}
```

#### GET `/api/v1/deployments`
List deployments

**Query Parameters**:
- `project_id` (optional)
- `environment` (optional)

#### GET `/api/v1/deployments/{deployment_id}`
Get deployment status

#### POST `/api/v1/deployments/{deployment_id}/cancel`
Cancel deployment

#### GET `/api/v1/deployments/environments/available`
List available environments

**Response**:
```json
["dev", "staging", "prod"]
```

### Testing Endpoints

#### POST `/api/v1/testing/run`
Run test suite

**Request**:
```json
{
  "project_id": "proj-uuid",
  "test_types": ["unit", "integration", "e2e"],
  "parallel": true
}
```

**Response**:
```json
{
  "run_id": "test-run-uuid",
  "status": "running",
  "total_tests": 150,
  "results": {
    "passed": 0,
    "failed": 0,
    "skipped": 0
  }
}
```

#### GET `/api/v1/testing/runs/{run_id}`
Get test run results

#### POST `/api/v1/testing/generate`
Generate tests

**Request**:
```json
{
  "project_id": "proj-uuid",
  "target_path": "backend/api/routes/",
  "test_type": "unit"
}
```

### WebSocket Endpoints

#### WebSocket `/ws/notifications`
Real-time notifications

**Messages**:
```json
{
  "type": "workflow_update",
  "data": {
    "workflow_id": "uuid",
    "phase": "implementation",
    "status": "in_progress"
  }
}
```

#### WebSocket `/ws/logs`
Real-time logs

---

## Database Schema

### Core Tables

#### `projects`
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    requirements TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    current_phase VARCHAR(50) DEFAULT 'idea',
    progress_percent FLOAT DEFAULT 0.0,
    tech_stack JSONB,
    owner_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `workflows`
```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    current_state VARCHAR(50),
    context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### `tasks`
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    agent_id UUID,
    task_type VARCHAR(100),
    description TEXT,
    priority INTEGER DEFAULT 2,
    status VARCHAR(50) DEFAULT 'pending',
    result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

#### `agents`
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    role VARCHAR(100),
    capabilities TEXT[],
    status VARCHAR(50) DEFAULT 'idle',
    current_task_id UUID REFERENCES tasks(id),
    last_active TIMESTAMP,
    metadata JSONB
);
```

#### `deployments`
```sql
CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    environment VARCHAR(50),
    version VARCHAR(50),
    status VARCHAR(50),
    steps JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

#### `knowledge_documents`
```sql
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    document_type VARCHAR(50),
    content TEXT,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_embedding 
ON knowledge_documents USING ivfflat (embedding vector_cosine_ops);
```

---

## Development Workflow

### Setup Instructions

#### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop with WSL2 (Windows) or Docker (Linux/Mac)
- Git

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn backend.main:app --reload --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Start development server
npm run dev
```

#### Full Stack with Docker

```bash
# From project root
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### Testing

#### Backend Tests

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ -v --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_health.py -v

# Run async tests
pytest backend/tests/ -v --asyncio-mode=auto
```

#### Frontend Tests

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- src/components/__tests__/idea-form.test.tsx
```

### Code Quality

#### Backend

```bash
# Format code
black backend/

# Sort imports
isort backend/

# Type checking
mypy backend/

# Linting
flake8 backend/
```

#### Frontend

```bash
# Format code
npx prettier --write src/

# Linting
npm run lint

# Type checking
npx tsc --noEmit
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Environment Variables

#### Backend (.env)

```env
# Application
APP_NAME=AI Software Factory
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aifactory
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379/0

# Ollama
OLLAMA_URL=http://localhost:11434

# CORS
ALLOWED_HOSTS=*

# Metrics
ENABLE_METRICS=True
METRICS_PORT=9090
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Common Commands

```bash
# Backend
uvicorn backend.main:app --reload          # Start dev server
pytest backend/tests/ -v                   # Run tests
alembic revision --autogenerate -m "msg"   # Create migration
alembic upgrade head                       # Apply migrations

# Frontend
npm run dev                                # Start dev server
npm run build                              # Build for production
npm run lint                               # Lint code
npm test                                   # Run tests

# Docker
docker compose up -d                       # Start all services
docker compose down                        # Stop all services
docker compose logs -f                     # View logs
docker compose ps                          # List containers
```

---

## Conclusion

ThetaAI - Software Factory represents a **comprehensive, enterprise-grade platform** for autonomous software development. Its modular architecture, sophisticated AI orchestration, and robust infrastructure make it capable of transforming ideas into production-ready SaaS applications with minimal human intervention.

### Key Strengths

✅ **Modular Design**: Clean separation of concerns across 14+ major modules  
✅ **AI-Powered**: Multi-agent collaboration with CrewAI and LangGraph  
✅ **Production-Ready**: Enterprise features like monitoring, security, and scalability  
✅ **Developer-Friendly**: Comprehensive testing, documentation, and tooling  
✅ **Extensible**: Plugin architecture for custom agents, workflows, and integrations  

### Current Status

**Completed Phases**:
- ✅ Phase 1: Core Backend Foundation
- ✅ Phase 2: Agent Framework
- ✅ Phase 3: Workflow Engine
- ✅ Phase 4: AgentOS
- ✅ Phase 5: Project Brain
- ✅ Phase 6: Simulation Layer
- ✅ Phase 7: Dashboard
- ✅ Phase 8: Infrastructure

**Ready for Production**:
- All core features implemented
- Comprehensive test coverage
- Full monitoring and observability
- Docker deployment ready
- Security best practices implemented

### Future Enhancements

**Potential Improvements**:
- Multi-cloud deployment support
- Enhanced AI models integration
- Advanced analytics and reporting
- Marketplace for pre-built agents
- Collaborative features for teams
- Integration with external tools (GitHub, Jira, etc.)

---

## Appendix

### Glossary

- **Agent**: Autonomous AI entity with specific role and capabilities
- **Crew**: Team of agents collaborating on tasks
- **Workflow**: Structured sequence of phases for project completion
- **Phase**: Distinct stage in software development lifecycle
- **RAG**: Retrieval-Augmented Generation
- **Sandbox**: Isolated execution environment
- **pgvector**: PostgreSQL extension for vector similarity search

### File Index

**Core Backend Files**:
- [`main.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\main.py) - Application entry
- [`config.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\core\config.py) - Configuration
- [`logging.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\core\logging.py) - Logging

**Services**:
- [`project_service.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\services\project_service.py)
- [`agent_service.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\services\agent_service.py)
- [`workflow_service.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\services\workflow_service.py)
- [`deployment_service.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\services\deployment_service.py)

**AI & Workflows**:
- [`base_agent.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\agents\base_agent.py)
- [`workflow_engine.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\workflow_engine.py)
- [`state_machine.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\workflows\state_machine.py)

**Brain & Knowledge**:
- [`rag_pipeline.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\rag_pipeline.py)
- [`knowledge_base.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\brain\knowledge_base.py)

**Testing & Simulation**:
- [`self_healing_runner.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\testing\self_healing_runner.py)
- [`sandbox.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\simulation\sandbox.py)

**Infrastructure**:
- [`docker-compose.yml`](c:\Users\DELL\Projects\ThetaAI - Software Factory\docker-compose.yml)
- [`orchestrator.py`](c:\Users\DELL\Projects\ThetaAI - Software Factory\backend\deployment\orchestrator.py)

### References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**End of Document**
