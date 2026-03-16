# AI Software Factory - Implementation Plan

## Project Overview
Building a complete, virtual AI-powered software engineering organization that transforms a founder's product idea into a deployed SaaS application. The system follows a strict 8-phase architecture with defined technology stack and modular design.

## Technology Stack (Fixed)
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, Tailwind CSS |
| Backend | Python 3.11, FastAPI (async) |
| Workflow Orchestration | LangGraph (state machines, phase transitions, task flows) |
| Agent Role Management | CrewAI (hierarchical teams, role-based collaboration) |
| Memory | PostgreSQL 15, pgvector, LlamaIndex |
| LLM Inference | Ollama (local models: Qwen, DeepSeek Coder, Llama, Mixtral) |
| Infrastructure | Docker, Docker Compose, Redis |
| Monitoring | Prometheus, Grafana |
| Real-time | WebSockets |

## Orchestration Architecture

### LangGraph Responsibilities
- High-level workflow orchestration
- State machine management (IDEA → REQUIREMENTS → ARCHITECTURE → IMPLEMENTATION → TESTING → DEPLOYMENT → COMPLETE)
- Sequential and parallel task execution
- State persistence and transitions
- Retry logic and error handling at workflow level

### CrewAI Responsibilities
- Agent role definitions (CEO, Product Manager, Backend Engineer, etc.)
- Hierarchical agent teams
- Collaborative task execution within phases
- Agent-to-agent delegation
- Role-based task assignment

### Integration Pattern
```
LangGraph Workflow Engine
    ↓ (triggers phase)
CrewAI Crew Assembly
    ↓ (assigns roles)
Collaborative Agent Execution
    ↓ (returns results)
LangGraph State Update
    ↓ (transitions to next phase)
```

## Project Structure
```
c:\Users\DELL\Projects\ThetaAI - Software Factory\
├── frontend/                 # Next.js dashboard
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── backend/                  # FastAPI application
│   ├── api/                  # API routes
│   ├── agents/               # Agent framework (CrewAI integration)
│   ├── workflows/            # Workflow engine (LangGraph)
│   ├── agent_os/             # Agent runtime
│   ├── brain/                # Knowledge system
│   ├── simulation/           # Validation layer
│   ├── services/
│   ├── models/
│   ├── core/                 # Config, logging
│   └── utils/
├── infrastructure/           # Docker, configs
├── scripts/                  # Setup scripts
└── tests/                    # Test suites
```

---

## Phase 1: Core Backend Foundation

### Scope
Establish the FastAPI backend skeleton with configuration management, structured logging, error handling, and health monitoring.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application entry point |
| `backend/core/config.py` | Environment-based configuration (pydantic-settings) |
| `backend/core/logging.py` | Structured JSON logging |
| `backend/core/exceptions.py` | Custom exception classes |
| `backend/middleware/error_handler.py` | Global error handling middleware |
| `backend/api/health.py` | Health check endpoint |
| `backend/requirements.txt` | Python dependencies |
| `backend/tests/test_config.py` | Configuration tests |
| `backend/tests/test_health.py` | Health endpoint tests |
| `backend/.env.example` | Environment template |

### Key Implementation Details

**Config Management (`backend/core/config.py`)**:
- Use pydantic-settings for type-safe environment variables
- Support .env file loading
- Separate configs for dev/test/prod
- No hard-coded values

**Logging (`backend/core/logging.py`)**:
- JSON structured logging
- Correlation IDs for request tracing
- Configurable log levels via environment

**Error Handling (`backend/middleware/error_handler.py`)**:
- Custom exception hierarchy
- Consistent error response format
- Automatic error logging

**Health Check (`backend/api/health.py`)**:
- GET /health endpoint
- Returns status, version, timestamp
- 200 OK when healthy

### Dependencies (requirements.txt)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
structlog==24.1.0
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.26.0
```

### Stabilization Steps
1. Run `pip install -r backend/requirements.txt`
2. Run `pytest backend/tests/ -v`
3. Start server: `uvicorn backend.main:app --reload --port 8000`
4. Test: `curl http://localhost:8000/health`
5. Verify no startup errors in logs

---

## Phase 2: Agent Framework

### Scope
Create reusable base for AI agents with CrewAI integration for role management, identity, task execution, memory access stubs, and registry pattern.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/agents/base_agent.py` | BaseAgent abstract class |
| `backend/agents/agent_registry.py` | Agent registration and discovery |
| `backend/agents/crews/` | CrewAI crew definitions |
| `backend/agents/crews/ceo_crew.py` | CEO-led crew configuration |
| `backend/agents/crews/engineering_crew.py` | Engineering crew configuration |
| `backend/agents/roles/` | CrewAI role definitions |
| `backend/agents/roles/ceo_role.py` | CEO role |
| `backend/agents/roles/product_manager_role.py` | PM role |
| `backend/agents/roles/backend_engineer_role.py` | Backend Engineer role |
| `backend/agents/model_router.py` | Ollama integration stub |
| `backend/agents/__init__.py` | Package exports |
| `backend/tests/agents/test_base_agent.py` | Agent instantiation tests |
| `backend/tests/agents/test_registry.py` | Registry tests |
| `backend/tests/agents/test_crews.py` | CrewAI integration tests |

### Key Implementation Details

**BaseAgent (`backend/agents/base_agent.py`)**:
```python
class BaseAgent(ABC):
    def __init__(self, agent_id: str, role: str, capabilities: List[str])
    async def execute_task(self, task: Task) -> TaskResult
    async def query_memory(self, query: str) -> MemoryResult  # stub
    @property
    def identity(self) -> AgentIdentity
```

**CrewAI Roles (`backend/agents/roles/`)**:
- Define agent roles using CrewAI's Role class
- Specify goals, backstories, and capabilities
- Enable hierarchical collaboration

**CrewAI Crews (`backend/agents/crews/`)**:
- Assemble agents into functional crews
- Define task delegation patterns
- Configure collaboration workflows

**AgentRegistry (`backend/agents/agent_registry.py`)**:
- Singleton pattern for agent discovery
- Register/unregister agents
- Get agent by ID or role
- List all registered agents

**Model Router Stub (`backend/agents/model_router.py`)**:
- Interface for LLM calls
- Support Ollama models
- Retry logic placeholder

### Dependencies to Add
```
crewai==0.11.0
langchain==0.1.0
```

### Stabilization Steps
1. Run `pytest backend/tests/agents/ -v`
2. Instantiate each agent type
3. Run mock tasks
4. Verify agent registration in registry
5. Test CrewAI crew assembly
6. Check structured logs

---

## Phase 3: Workflow Engine

### Scope
Build orchestration system using LangGraph for workflow management, integrating with CrewAI for agent collaboration within phases.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/workflows/workflow_engine.py` | Main workflow orchestrator (LangGraph) |
| `backend/workflows/graph_builder.py` | LangGraph StateGraph builder |
| `backend/workflows/task_manager.py` | Task queue management |
| `backend/workflows/state_machine.py` | Project state transitions |
| `backend/workflows/agent_router.py` | Agent selection and delegation to CrewAI |
| `backend/workflows/pipeline.py` | Full pipeline workflow definition |
| `backend/workflows/crew_integration.py` | LangGraph-CrewAI bridge |
| `backend/models/workflow.py` | Workflow data models |
| `backend/models/task.py` | Task data models |
| `backend/tests/workflows/test_workflow_engine.py` | Workflow tests |
| `backend/tests/workflows/test_state_machine.py` | State transition tests |
| `backend/tests/workflows/test_crew_integration.py` | Integration tests |

### Key Implementation Details

**State Machine States**:
- IDEA → REQUIREMENTS → ARCHITECTURE → IMPLEMENTATION → TESTING → DEPLOYMENT → COMPLETE

**LangGraph Workflow Engine**:
- StateGraph for workflow definition
- Nodes represent phases
- Edges represent transitions
- Support sequential and parallel task execution
- Retry logic with exponential backoff
- State persistence

**CrewAI Integration (`backend/workflows/crew_integration.py`)**:
```python
class CrewIntegration:
    def assemble_crew_for_phase(self, phase: str) -> Crew
    def execute_crew_tasks(self, crew: Crew, context: dict) -> CrewOutput
    def map_crew_output_to_state(self, output: CrewOutput) -> WorkflowState
```

**Task Manager**:
- Task creation, assignment, tracking
- Priority queues
- Deadline management

**Agent Router**:
- Route tasks to appropriate CrewAI crews
- Map workflow phases to crew types
- Handle crew lifecycle

### Dependencies to Add
```
langgraph==0.0.40
```

### Stabilization Steps
1. Run `pytest backend/tests/workflows/ -v`
2. Simulate state transitions
3. Test LangGraph-CrewAI integration
4. Verify crew assembly per phase
5. Check retry mechanisms
6. Verify state persistence

---

## Phase 4: AgentOS

### Scope
Runtime environment for agents with scheduling, task queues, worker pools, and resource management. Integrates with both LangGraph and CrewAI.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/agent_os/scheduler.py` | Task scheduling logic |
| `backend/agent_os/task_queue.py` | Redis-based task queue |
| `backend/agent_os/worker_pool.py` | Worker process management |
| `backend/agent_os/resource_manager.py` | Resource allocation |
| `backend/agent_os/error_handler.py` | Failure recovery |
| `backend/agent_os/crew_executor.py` | CrewAI execution wrapper |
| `backend/agent_os/__init__.py` | Package exports |
| `backend/tests/agent_os/test_scheduler.py` | Scheduler tests |
| `backend/tests/agent_os/test_worker_pool.py` | Worker tests |
| `backend/tests/agent_os/test_error_handler.py` | Error recovery tests |
| `backend/tests/agent_os/test_crew_executor.py` | Crew execution tests |

### Key Implementation Details

**Scheduler**:
- Cron-like scheduling
- Priority-based execution
- Dependency resolution
- LangGraph state-aware scheduling

**Task Queue (Redis)**:
- Celery or RQ for task distribution
- Queue per agent type
- Dead letter queue for failures
- Separate queues for LangGraph and CrewAI tasks

**Worker Pool**:
- Dynamic worker scaling
- Health monitoring
- Graceful shutdown
- Crew-specific worker pools

**Crew Executor (`backend/agent_os/crew_executor.py`)**:
- Execute CrewAI crews asynchronously
- Manage crew lifecycle
- Handle crew output

**Error Handler**:
- Retry with backoff
- Escalation to human-in-the-loop
- Circuit breaker pattern

### Dependencies to Add
```
celery==5.3.0
rq==1.15.0
redis==5.0.0
```

### Stabilization Steps
1. Start Redis: `docker run -d -p 6379:6379 redis:7-alpine`
2. Run `pytest backend/tests/agent_os/ -v`
3. Spawn test workers
4. Enqueue tasks and verify execution
5. Test crew execution
6. Simulate failures and verify retry

---

## Phase 5: Project Brain

### Scope
Central knowledge system with semantic search, embeddings, and RAG integration for agents. Accessible by both LangGraph workflows and CrewAI agents.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/brain/brain_service.py` | Main brain service |
| `backend/brain/context_retriever.py` | Context retrieval for RAG |
| `backend/brain/knowledge_graph.py` | Knowledge graph management |
| `backend/brain/embeddings.py` | Embedding generation |
| `backend/brain/models.py` | Brain data models |
| `backend/brain/llama_index_config.py` | LlamaIndex configuration |
| `backend/brain/crew_memory_tool.py` | CrewAI memory tool integration |
| `backend/tests/brain/test_brain_service.py` | Brain service tests |
| `backend/tests/brain/test_retriever.py` | RAG tests |

### Key Implementation Details

**Knowledge Layers**:
- Product Layer: Requirements, user stories
- Architecture Layer: Tech decisions, diagrams
- Implementation Layer: Code docs, APIs
- Deployment Layer: Infra config, env vars

**Vector Store (pgvector)**:
- PostgreSQL with pgvector extension
- LlamaIndex for indexing
- Semantic search with embeddings

**RAG Integration**:
- Agents query before task execution
- Context-aware responses
- Source attribution

**CrewAI Memory Tool (`backend/brain/crew_memory_tool.py`)**:
- Custom CrewAI tool for brain access
- Enable agents to query Project Brain
- Store agent decisions and outputs

### Dependencies to Add
```
llama-index==0.9.0
pgvector==0.2.0
sqlalchemy==2.0.0
alembic==1.13.0
openai==1.0.0  # For embeddings fallback
```

### Stabilization Steps
1. Start PostgreSQL with pgvector
2. Run migrations: `alembic upgrade head`
3. Run `pytest backend/tests/brain/ -v`
4. Insert sample knowledge
5. Query and verify semantic search
6. Test CrewAI memory tool

---

## Phase 6: Simulation Layer

### Scope
Validation system for UX flows, architecture, APIs, and infrastructure before actual build. Triggered by LangGraph, executed by simulation crews.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/simulation/simulation_engine.py` | Simulation orchestrator |
| `backend/simulation/crews/ux_simulation_crew.py` | UX simulation crew |
| `backend/simulation/crews/architecture_simulation_crew.py` | Architecture validation crew |
| `backend/simulation/crews/api_simulation_crew.py` | API contract simulation crew |
| `backend/simulation/crews/infra_simulation_crew.py` | Infrastructure simulation crew |
| `backend/simulation/models.py` | Simulation data models |
| `backend/simulation/report_generator.py` | Simulation report generation |
| `backend/tests/simulation/test_simulations.py` | Simulation tests |

### Key Implementation Details

**Simulation Engine**:
- Triggered by LangGraph workflow
- Assembles appropriate CrewAI crew
- Collects and aggregates results
- Generates approval/rejection recommendations

**UX Simulation Crew**:
- User journey validation
- Accessibility checks
- Responsive design verification

**Architecture Simulation Crew**:
- Component interaction modeling
- Performance prediction
- Scalability analysis

**API Simulation Crew**:
- Contract validation
- Load testing simulation
- Error scenario testing

**Infra Simulation Crew**:
- Resource requirement estimation
- Cost prediction
- Deployment feasibility

### Stabilization Steps
1. Run `pytest backend/tests/simulation/ -v`
2. Run simulations on mock data
3. Generate and review reports
4. Test approve/reject workflow
5. Verify LangGraph integration

---

## Phase 7: Dashboard

### Scope
Next.js web control panel for idea submission, monitoring, and human approvals. Displays LangGraph workflow state and CrewAI agent activities.

### Deliverables

| File | Purpose |
|------|---------|
| `frontend/package.json` | Dependencies |
| `frontend/app/layout.tsx` | Root layout |
| `frontend/app/page.tsx` | Dashboard home |
| `frontend/app/projects/page.tsx` | Project list |
| `frontend/app/projects/[id]/page.tsx` | Project detail |
| `frontend/app/agents/page.tsx` | Agent management |
| `frontend/app/workflows/page.tsx` | Workflow visualization |
| `frontend/app/simulations/page.tsx` | Simulation results |
| `frontend/components/idea-form.tsx` | Idea submission form |
| `frontend/components/activity-feed.tsx` | Real-time activity |
| `frontend/components/workflow-viewer.tsx` | LangGraph workflow viz |
| `frontend/components/crew-status.tsx` | CrewAI crew status |
| `frontend/components/architecture-viewer.tsx` | Architecture viz |
| `frontend/lib/api.ts` | Backend API client |
| `frontend/lib/websocket.ts` | WebSocket client |
| `frontend/__tests__/components.test.tsx` | Component tests |

### Key Implementation Details

**Pages**:
- Dashboard: Overview, stats, recent activity
- Projects: List, create, view details
- Agents: View status, capabilities, crew assignments
- Workflows: Visualize LangGraph state machine
- Simulations: Run, view results, approve

**Real-time Features**:
- WebSocket connection for activity feed
- Live agent status updates
- Workflow state changes
- Crew execution progress

**Workflow Viewer**:
- Visualize LangGraph state transitions
- Show current phase
- Display phase history

**Crew Status**:
- Active crews
- Agent assignments
- Task progress

**Architecture Viewer**:
- Mermaid.js for diagrams
- Interactive component exploration

### Dependencies (package.json)
```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "@tailwindcss/forms": "^0.5.7",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",
    "mermaid": "^10.6.0",
    "react-flow-renderer": "^10.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.1.0",
    "typescript": "^5.3.0"
  }
}
```

### Stabilization Steps
1. Run `npm install`
2. Run `npm run test`
3. Start dev server: `npm run dev`
4. Test UI interactions
5. Verify WebSocket connection to backend
6. Test workflow visualization

---

## Phase 8: Infrastructure

### Scope
Complete deployment setup with Docker Compose, monitoring, and backup configuration. Includes both LangGraph and CrewAI services.

### Deliverables

| File | Purpose |
|------|---------|
| `infrastructure/docker-compose.yml` | Full stack orchestration |
| `infrastructure/Dockerfile.backend` | Backend container |
| `infrastructure/Dockerfile.frontend` | Frontend container |
| `infrastructure/prometheus.yml` | Prometheus config |
| `infrastructure/grafana/dashboards/` | Grafana dashboards |
| `infrastructure/nginx/nginx.conf` | Reverse proxy config |
| `scripts/setup.sh` | Setup script (WSL) |
| `scripts/setup.ps1` | Setup script (Windows) |
| `scripts/backup.sh` | Backup script |
| `requirements.txt` | Root requirements reference |
| `Makefile` | Common commands |

### Services (docker-compose.yml)
- frontend: Next.js app (port 3000)
- backend: FastAPI app (port 8000)
- postgres: PostgreSQL 15 with pgvector
- redis: Redis 7 (caching, queues)
- ollama: Ollama server (port 11434)
- prometheus: Metrics (port 9090)
- grafana: Dashboards (port 3001)
- nginx: Reverse proxy (port 80)

### Stabilization Steps
1. Run `docker compose build`
2. Run `docker compose up -d`
3. Verify all services: `docker compose ps`
4. Test: `curl http://localhost/health`
5. Deploy sample project end-to-end

---

## Cross-Platform Support

### WSL Environment
- All shell scripts (.sh) for Linux/WSL
- Docker Compose with Linux containers
- Makefile for common tasks

### Windows Environment
- PowerShell scripts (.ps1) equivalents
- Docker Desktop with WSL2 backend
- Batch file wrappers if needed

---

## Implementation Rules

1. **100% Phase Completion**: Each phase must be fully implemented, wired properly, tested, bug-free, and production enterprise-grade before proceeding to the next phase. No exceptions.
2. **No Phase Skipping**: Complete each phase fully before proceeding
3. **No Future Dependencies**: Stub future dependencies with TODO comments
4. **Strict Tech Stack**: No deviations from specified technologies
5. **Test Coverage**: Every module must have comprehensive unit/integration tests with >90% coverage
6. **Documentation**: Every file must have docstrings and inline comments
7. **Clean Code**: PEP 8 for Python, ESLint for JavaScript/TypeScript
8. **Type Safety**: Type hints in Python, TypeScript for frontend
9. **Orchestration Integration**: Every phase must properly integrate LangGraph and CrewAI
10. **Production Grade**: All code must be enterprise-ready with proper error handling, logging, security, and performance considerations

---

## Success Criteria

After Phase 8 completion:
- [ ] `docker compose up` starts all services
- [ ] Founder can submit idea via dashboard
- [ ] LangGraph orchestrates workflow through all phases
- [ ] CrewAI crews execute collaborative tasks within phases
- [ ] Human-in-the-loop approvals work
- [ ] Final SaaS application is deployed
- [ ] All tests pass
- [ ] Monitoring dashboards are functional

---

## Next Steps

Upon plan approval:
1. I will begin Phase 1 implementation
2. Create the backend folder structure
3. Implement configuration, logging, and health check
4. Write tests and verify stabilization
5. Await confirmation to proceed to Phase 2
