# IntraMind: Project Roadmap

> AI-powered intelligent search platform for enterprise internal documents

## 🎯 Project Goal

Create **IntraMind**, an AI-powered platform that enables semantic search across internal enterprise documents through a microservices architecture. The system will support multimodal content (text, images, presentations, flowcharts) and showcase understanding of:
- Microservices architecture patterns
- Git submodules for independent service management
- gRPC service contracts
- API Gateway design
- AI agentic workflows
- Vector database operations

## 📁 Repository Structure

IntraMind uses Git submodules to manage independent microservices:

```
IntraMind/                           (Main Platform - This Repo)
├── README.md                        # Platform overview
├── PROJECT_ROADMAP.md               # This file
├── docker-compose.yml               # Orchestration for all services
│
├── vector-db-service/               # Submodule → ai-vector-db-practice
│   ├── src/
│   ├── tests/
│   └── docker-compose.yml
│
├── api-gateway/                     # Submodule → intramind-api-gateway
│   ├── src/IntraMind.ApiGateway/
│   ├── src/IntraMind.ApiGateway.Tests/
│   └── docker-compose.yml
│
└── ai-agent/                        # Submodule → intramind-ai-agent
    └── (AI Agent Service)
```

**Repositories:**
- **Main Platform**: [IntraMind](https://github.com/JessKelly91/IntraMind)
- **Vector DB Service**: [ai-vector-db-practice](https://github.com/JessKelly91/ai-vector-db-practice)
- **API Gateway**: [intramind-api-gateway](https://github.com/JessKelly91/intramind-api-gateway)
- **AI Agent**: [intramind-ai-agent](https://github.com/JessKelly91/intramind-ai-agent)

## 🏗️ Architecture Overview

```
┌─────────────┐
│  AI Agent   │  (LangGraph)
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│ API Gateway │  (ASP.NET Core 8.0)
└──────┬──────┘
       │ gRPC
       ▼
┌─────────────┐
│   Vector    │  (Python gRPC Service)
│   Service   │
└──────┬──────┘
       │ Weaviate Client
       ▼
┌─────────────┐
│  Weaviate   │  (Vector Database)
│     DB      │  (Docker)
└─────────────┘
```

### Components

| Component | Technology | Repository | Purpose |
|-----------|-----------|------------|---------|
| **AI Agent** | LangGraph + LangChain tools | `ai-agent/` | Orchestrates AI workflows and decision-making |
| **API Gateway** | ASP.NET Core 8.0 | `api-gateway/` | REST API layer, request routing, auth |
| **Vector Service** | Python + gRPC | `vector-db-service/` | Core microservice for vector operations |
| **Proto Contracts** | Protocol Buffers | `vector-db-service/` | Service definitions and data contracts |
| **Weaviate DB** | Docker Compose | `vector-db-service/` | Vector storage and semantic search |
| **Vectorizer** | text2vec-transformers | `vector-db-service/` | Free local embeddings (no API costs) |

## 📊 Current Status

### ✅ Completed
- [x] **Microservices Architecture Setup**
  - [x] IntraMind main platform repository created
  - [x] Git submodules configured
  - [x] vector-db-service added as submodule
  - [x] Platform documentation (README, roadmap)

- [x] **Phase 1: Foundation - Database Layer** ✅ COMPLETE
  - [x] Weaviate Docker Compose configuration with persistence
  - [x] Free local vectorization (text2vec-transformers)
  - [x] Environment configuration setup
  - [x] Connection testing and validation
  - [x] Data persistence verification
  - [x] Vectorization testing with automatic embeddings

- [x] **Phase 2: Core Service - gRPC Vector Service** ✅ COMPLETE
  - [x] Complete proto contract definitions (`vector_service.proto`)
  - [x] All 11 RPC methods implemented and tested
  - [x] Full CRUD operations (Insert, Get, Update, Delete)
  - [x] Batch operations for efficiency
  - [x] Collection management (Create, List, Get, Delete)
  - [x] Semantic search with streaming support
  - [x] Health checks and comprehensive error handling
  - [x] Telemetry integration (optional Azure monitoring)
  - [x] Production-ready server implementation
  - [x] Comprehensive testing (both Weaviate and gRPC tests passing)
  - [x] Generated Python proto files
  - [x] Configuration management (appSettings.json + .env)

### ✅ Completed
- [x] **Phase 3: Gateway Layer - REST API Gateway** ✅ COMPLETE
  - [x] Create new submodule repository (`intramind-api-gateway`)
  - [x] Implement ASP.NET Core 8.0 REST endpoints
  - [x] Map REST to gRPC calls
  - [x] Add error handling and validation
  - [x] API documentation (Swagger/OpenAPI)
  - [x] Structured logging with Serilog
  - [x] Health checks and monitoring
  - [x] Docker containerization
  - [x] Unit tests with xUnit and FluentAssertions

### 🚧 In Progress
- [ ] **Phase 4: Intelligence Layer - AI Agent**
  - [x] Create new submodule repository (`intramind-ai-agent`)
  - [x] Choose AI framework (LangGraph)
  - [x] Implement core agent tools for API Gateway integration
  - [ ] Add multimodal document processing
  - [x] Create agent interface (CLI)
  - [ ] Create agent interface (Web)

### ❌ Future Phases
- [ ] **Phase 5: Integration & Polish**
  - [ ] Platform-wide Docker Compose orchestration
  - [ ] Integration testing across services
  - [ ] Multimodal document support (images, presentations)

## 🗺️ Development Roadmap (Bottom-Up Approach)

### **Phase 1: Foundation - Database Layer** ✅ COMPLETED
**Goal:** Validate Weaviate is working correctly  
**Location:** `vector-db-service/` submodule

- [x] **Task 1.1:** Start Weaviate with Docker Compose
  - [x] Navigate to `vector-db-service/`
  - [x] Run `docker-compose up -d`
  - [x] Verify both containers are running (weaviate + transformers)
  - [x] Check health endpoints
  
- [x] **Task 1.2:** Test Weaviate Connection
  - [x] Create test script to connect to Weaviate
  - [x] Create a test collection
  - [x] Insert sample documents
  - [x] Perform basic search query
  - [x] Verify data persistence (restart container, check data exists)

- [x] **Task 1.3:** Validate Vectorization
  - [x] Insert documents without explicit vectors
  - [x] Verify transformers model generates embeddings automatically
  - [x] Test semantic search works correctly

**Deliverable:** ✅ Working Weaviate instance with verified CRUD operations

---

### **Phase 2: Core Service - gRPC Vector Service** ✅ COMPLETED
**Goal:** Complete implementation of the gRPC microservice  
**Location:** `vector-db-service/` submodule

- [x] **Task 2.1:** Review Existing Code
  - [x] Review `vector-db-service/src/service/protos/vector_service.proto`
  - [x] Review `vector-db-service/src/service/servicers/vector_db_servicer.py`
  - [x] Review `vector-db-service/src/service/server.py`
  - [x] Identify missing operations
  - [x] Document current capabilities

- [x] **Task 2.2:** Finalize Proto Contracts
  - [x] Define all required RPC methods:
    - [x] InsertVector
    - [x] InsertVectorBatch
    - [x] GetVector
    - [x] UpdateVector
    - [x] DeleteVector
    - [x] SemanticSearch
    - [x] StreamSearch
    - [x] CreateCollection
    - [x] DeleteCollection
    - [x] ListCollections
    - [x] GetCollection
    - [x] HealthCheck
  - [x] Define request/response messages
  - [x] Add proper field validation

- [x] **Task 2.3:** Generate Proto Code
  - [x] Generate Python proto files
  - [x] Update `scripts/generate_proto.bat`
  - [x] Verify generated code compiles

- [x] **Task 2.4:** Implement gRPC Servicer
  - [x] Implement all RPC methods
  - [x] Add error handling
  - [x] Add logging/telemetry
  - [x] Implement gRPC interceptors (auth, logging)
  - [x] Add input validation

- [x] **Task 2.5:** Create gRPC Server
  - [x] Setup gRPC server with servicer
  - [x] Configure ports and settings
  - [x] Add graceful shutdown handling
  - [x] Add health checks

- [x] **Task 2.6:** Test gRPC Service
  - [x] Create gRPC client test script
  - [x] Test all operations end-to-end
  - [x] Test error scenarios
  - [x] Performance testing

**Deliverable:** ✅ Fully functional gRPC Vector Service with all CRUD operations

> **Note:** Work in this phase happens in the `vector-db-service/` submodule. Commit and push changes there first, then update the submodule reference in the main IntraMind repo.

---

### **Phase 3: Gateway Layer - REST API Gateway** ✅ COMPLETED
**Goal:** Create REST API that proxies to gRPC service  
**Location:** `api-gateway/` submodule

- [x] **Task 3.0:** Setup New Submodule
  - [x] Create new GitHub repository: `intramind-api-gateway`
  - [x] Add as submodule: `git submodule add https://github.com/JessKelly91/intramind-api-gateway.git api-gateway`
  - [x] Initialize project structure in the new repo
  - [x] Setup initial documentation

- [x] **Task 3.1:** Design API Gateway
  - [x] Choose framework (ASP.NET Core 8.0)
  - [x] Design REST endpoint structure
  - [x] Define request/response schemas
  - [x] Plan authentication strategy (CORS for development)

- [x] **Task 3.2:** Implement Gateway Core
  - [x] Setup ASP.NET Core 8.0 application
  - [x] Create gRPC client connection pool to vector-db-service
  - [x] Implement health check endpoints
  - [x] Add CORS configuration

- [x] **Task 3.3:** Implement REST Endpoints
  - [x] Map REST endpoints to gRPC calls:
    - [x] GET /v1/collections - List collections
    - [x] GET /v1/collections/{name} - Get collection
    - [x] POST /v1/collections - Create collection
    - [x] DELETE /v1/collections/{name} - Delete collection
    - [x] POST /v1/documents - Insert document
    - [x] POST /v1/documents/batch - Batch insert documents
    - [x] GET /v1/documents/{id} - Get document
    - [x] PUT /v1/documents/{id} - Update document
    - [x] DELETE /v1/documents/{id} - Delete document
    - [x] POST /v1/search - Search documents
    - [x] GET /health - Health check
    - [x] GET /health/liveness - Kubernetes liveness probe
    - [x] GET /health/readiness - Kubernetes readiness probe

- [x] **Task 3.4:** Add Gateway Features
  - [x] Request validation with FluentValidation
  - [x] Error handling and mapping middleware
  - [x] Structured logging with Serilog
  - [x] API documentation (Swagger/OpenAPI)
  - [x] Docker containerization support

- [x] **Task 3.5:** Test API Gateway
  - [x] Unit tests for collections endpoints (xUnit, FluentAssertions, Moq)
  - [x] Unit tests for documents endpoints (xUnit, FluentAssertions, Moq)
  - [x] Unit tests for search endpoints (xUnit, FluentAssertions, Moq) 
  - [x] Unit tests for health endpoints (xUnit, FluentAssertions, Moq)
  - [x] Integration tests with gRPC service
  - [x] Test project structure and configuration

**Deliverable:** ✅ Complete REST API Gateway with full endpoint coverage

> **Note:** This will be a new independent repository added as a submodule to IntraMind.

---

### **Phase 4: Intelligence Layer - AI Agent** 🚧 IN PROGRESS
**Goal:** Create AI agent that can interact with the vector database  
**Location:** `ai-agent/` submodule

- [x] **Task 4.0:** Setup New Submodule
  - [x] Create new GitHub repository: `intramind-ai-agent`
  - [x] Add as submodule: `git submodule add https://github.com/JessKelly91/intramind-ai-agent.git ai-agent`
  - [x] Initialize project structure in the new repo
  - [x] Setup initial documentation

- [ ] **Task 4.1:** Design Agent Architecture
  - [x] Choose framework (LangGraph)
  - [x] Define agent capabilities/tools
  - [x] Design conversation flow
  - [ ] Plan agent memory/context handling
  - [ ] Plan multimodal document processing (text, images, presentations)

- [ ] **Task 4.2:** Implement Agent Tools
  - [x] Create tool for document insertion (via API Gateway)
  - [x] Create tool for semantic search (via API Gateway)
  - [x] Create tool for document retrieval (via API Gateway)
  - [x] Create tool for collection management (via API Gateway)
  - [ ] Create tool for image/presentation processing

- [ ] **Task 4.3:** Implement Agent Core
  - [x] Setup agent framework
  - [x] Configure LLM (local or API)
  - [x] Implement tool calling logic
  - [ ] Add conversation memory
  - [x] Add error recovery
  - [ ] Add multimodal content handling

- [ ] **Task 4.4:** Create Agent Interface
  - [x] CLI interface for testing
  - [ ] Web interface (optional)
  - [x] Logging and observability

- [ ] **Task 4.5:** Test AI Agent
  - [ ] Test basic interactions
  - [ ] Test multi-step workflows
  - [ ] Test multimodal document processing
  - [ ] Test error handling
  - [ ] User acceptance testing

**Deliverable:** Functional AI agent that can interact with vector database and process multimodal documents

> **Note:** This will be a new independent repository added as a submodule to IntraMind.

---

### **Phase 5: Integration & Polish**
**Goal:** Complete end-to-end system with documentation  
**Location:** IntraMind main repo (orchestration)

- [ ] **Task 5.1:** Platform-Wide Docker Compose
  - [ ] Create main `docker-compose.yml` in IntraMind root
  - [ ] Orchestrate all services (Weaviate, Vector Service, API Gateway, AI Agent)
  - [ ] Configure inter-service networking
  - [ ] Setup environment variables and secrets management

- [ ] **Task 5.2:** Integration Testing
  - [ ] End-to-end test scenarios across all services
  - [ ] Load testing full stack
  - [ ] Error scenario testing
  - [ ] Performance optimization
  - [ ] Test submodule update workflows

- [ ] **Task 5.3:** Documentation
  - [x] Architecture documentation (README.md)
  - [x] Project roadmap (PROJECT_ROADMAP.md)
  - [ ] API documentation (consolidated)
  - [ ] Deployment guide
  - [ ] User guide
  - [ ] Submodule management guide
  - [ ] Code comments and docstrings

- [ ] **Task 5.4:** Deployment Preparation
  - [ ] Kubernetes manifests (optional)
  - [ ] CI/CD pipeline setup (.github/workflows)
  - [ ] Monitoring and alerting
  - [ ] Health check aggregation

- [ ] **Task 5.5:** Demo & Showcase
  - [ ] Create demo scenarios with multimodal content
  - [ ] Record demo video
  - [ ] Prepare presentation materials
  - [ ] Update GitHub README with architecture diagrams
  - [ ] Create portfolio writeup

**Deliverable:** Production-ready microservices platform with full documentation and deployment setup

## 🎯 Next Immediate Steps

1. **Finalize LLM configuration**: Set API keys or use Ollama defaults (router); Anthropic/OpenAI for synthesis
2. **Implement conversation memory**: Add short-term memory to the search workflow
3. **Extend tools**: Add batch insert/update/delete tools and image/presentation processing
4. **Expand tests**: Add workflow and CLI tests; increase coverage
5. **Optional Web UI**: Simple web frontend for search and result viewing
6. **Integration checks**: Verify agent ↔ API Gateway ↔ Vector Service end-to-end

## 📝 Key Decisions & Notes

### Architecture Decisions
- **Microservices Structure**: Git submodules for independent service management
  - Each service has its own repository and lifecycle
  - Main IntraMind repo orchestrates the platform
  - Enables independent development, testing, and deployment
- **Vectorization**: Using free `text2vec-transformers` for local development (no API costs)
- **Persistence**: Docker volumes for data persistence across container restarts
- **Authentication**: Anonymous access for local development, to be secured for production
- **Approach**: Bottom-up implementation (database → service → gateway → agent)
- **Multimodal Support**: Planned support for text, images, presentations, and flowcharts

### Technology Choices
- **Vector DB**: Weaviate (open source, production-ready)
- **RPC Protocol**: gRPC (efficient, type-safe, language-agnostic)
- **Contracts**: Protocol Buffers (schema evolution, code generation)
- **Gateway**: ASP.NET Core 8.0 (REST API with Swagger/OpenAPI documentation)
- **AI Framework**: LangGraph + LangChain tools (selected for Phase 4)
- **Repository Management**: Git submodules (independent service repositories)

### Submodule Workflow
1. **Making Changes**: Navigate into the submodule directory, make changes, commit, and push
2. **Updating References**: After pushing submodule changes, update the reference in the main IntraMind repo
3. **Cloning**: Always use `git clone --recurse-submodules` or `git submodule update --init --recursive`
4. **Pulling**: Use `git pull --recurse-submodules` to update everything

### Future Considerations
- Multimodal document processing (images, presentations, flowcharts)
- OpenAI/Azure OpenAI integration for embeddings and LLM
- Authentication & authorization across services
- Multi-tenancy support
- Caching layer
- Message queue for async operations
- Observability (metrics, tracing, logging)
- Kubernetes deployment
- CI/CD pipeline for each service and platform

## 📚 Resources

### Documentation
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)

### Git Submodules
- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Working with Submodules](https://github.blog/2016-02-01-working-with-submodules/)

### IntraMind Repositories
- [Main Platform](https://github.com/JessKelly91/IntraMind)
- [Vector DB Service](https://github.com/JessKelly91/ai-vector-db-practice)

---

**Last Updated:** October 2025  
**Current Phase:** Phase 4 - Intelligence Layer (AI Agent) — In Progress  
**Architecture:** Microservices with Git Submodules

