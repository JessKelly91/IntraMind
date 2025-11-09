# IntraMind

> AI-powered intelligent search platform for enterprise internal documents

IntraMind is a microservices-based platform that enables semantic search across your organization's internal knowledge base, supporting multiple file types including documents, presentations, images, and flowcharts.

## 🏗️ Architecture

IntraMind follows a microservices architecture with independent, deployable services:

```
IntraMind/
├── vector-db-service/        # Vector database service (gRPC)
├── api-gateway/              # REST API gateway (ASP.NET Core)
└── ai-agent/                 # AI agent orchestration (LangGraph)
```

### Current Services

- **vector-db-service** ([Repository](https://github.com/JessKelly91/ai-vector-db-practice))
  - gRPC-based vector database service
  - Weaviate integration for semantic search
  - Document vectorization and storage
  - Python + gRPC + Weaviate
- **api-gateway** ([Repository](https://github.com/JessKelly91/intramind-api-gateway))
  - ASP.NET Core 8.0 REST API layer
  - Proxies to gRPC Vector DB Service
  - Swagger, validation, error handling, health checks
- **ai-agent** ([Repository](https://github.com/JessKelly91/intramind-ai-agent))
  - LangGraph-based AI workflows
  - Tools for search/insert/retrieve/collections via API Gateway
  - CLI with streaming and logging

## 🚀 Getting Started

### Prerequisites

- **Git**
- **Docker & Docker Compose**
- **Python 3.11+**
- **Ollama** (for AI Agent LLM)

### Installation Steps

#### 1. Clone with Submodules

```bash
# Clone the repository with all submodules
git clone --recurse-submodules https://github.com/JessKelly91/IntraMind.git
cd IntraMind

# Or if you already cloned, initialize submodules
git submodule update --init --recursive
```

#### 2. Install Ollama (One-time setup)

The AI Agent uses Ollama for local LLM routing. Install it once on your machine:

```bash
# Download and install from https://ollama.ai/
# Then pull the required model:
ollama pull llama3.2:3b

# Start Ollama (keep running in background)
ollama serve
```

#### 3. Start IntraMind Platform

```bash
# Start all backend services (Weaviate, Vector Service, API Gateway)
docker-compose up -d

# Verify all services are healthy
docker-compose ps

# View logs (optional)
docker-compose logs -f api-gateway
```

**Services will be available at:**
- **Weaviate**: http://localhost:8080
- **Vector Service (gRPC)**: http://localhost:50052
- **API Gateway (REST)**: http://localhost:5000
- **API Gateway Swagger**: http://localhost:5000/swagger

#### 4. Run AI Agent CLI

```bash
# Navigate to AI agent directory
cd ai-agent

# Install dependencies (first time only)
pip install -r requirements.txt

# Configure environment (copy and edit .env file)
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY or OPENAI_API_KEY (optional)

# Run interactive CLI
python -m src.cli.main

# Or run a single search query
python -m src.cli.main search "your search query"
```

### Quick Health Check

```bash
# Test Weaviate
curl http://localhost:8080/v1/.well-known/ready

# Test API Gateway
curl http://localhost:5000/health

# Test full stack with AI Agent
cd ai-agent
python -m src.cli.main search "test"
```

### Stopping Services

```bash
# Stop all Docker services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## 🔄 Working with Submodules

### Update Submodules to Latest

```bash
git submodule update --remote
```

### Pull Latest Changes (Including Submodules)

```bash
git pull --recurse-submodules
```

### Making Changes to a Submodule

```bash
# Navigate into the submodule
cd vector-db-service

# Make changes, commit, and push as normal
git checkout main
git pull
# ... make changes ...
git add .
git commit -m "Your changes"
git push

# Return to main repo and update submodule reference
cd ..
git add vector-db-service
git commit -m "Update vector-db-service to latest"
git push
```

## 🛠️ Tech Stack

- **Vector Service**: Python, gRPC, Protocol Buffers, Weaviate
- **API Gateway**: ASP.NET Core 8.0, Grpc.Net.Client, Serilog, FluentValidation, Swagger
- **AI Agent**: Python, LangGraph, LangChain tools, httpx, Click, Rich
- **Vector Database**: Weaviate
- **Containerization**: Docker, Docker Compose
- **LLM Providers**: Ollama (router), Anthropic/OpenAI (synthesis)

## 🎯 Roadmap

- [x] Vector database service with gRPC API
- [x] REST API Gateway
- [ ] AI Agent orchestration layer (in progress)
- [ ] Multimodal support (images, presentations)
- [ ] Document preprocessing pipeline
- [ ] Authentication & authorization
- [ ] Monitoring & observability

## 🧪 Testing

### Integration Tests

Platform-wide integration tests are located in `tests/integration/`:

```bash
# Run all integration tests
cd tests
pip install -r requirements.txt
pytest integration/ -v

# Expected: 34 passed, 6 skipped (in CI mode without vectorizer)
```

**CI Mode:** The CI pipeline uses `docker-compose.ci.yml` which runs without the vectorizer (no 8GB model download) for faster testing. Semantic search tests are automatically skipped in CI.

See [Integration Tests README](./tests/integration/README.md) for detailed testing documentation.

## 📚 Documentation

### Getting Started
- **[User Guide](./docs/USER_GUIDE.md)** - Complete guide with end-to-end usage scenarios
- **[Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)** - Local and production deployment instructions
- **[Docker Setup Guide](./docs/DOCKER_SETUP.md)** - Docker Compose setup and troubleshooting

### Developer Resources
- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation for all services
- **[Submodule Guide](./docs/SUBMODULE_GUIDE.md)** - Working with Git submodules
- **[Architecture Overview](./docs/ARCHITECTURE.md)** - System design and component details
- **[Integration Tests](./tests/integration/README.md)** - Platform-wide integration testing

### CI/CD
- **[GitHub Workflows](./.github/README.md)** - CI/CD pipeline documentation
- **[CI Configuration](./docker-compose.ci.yml)** - Optimized CI environment setup

### Project Management
- **[Project Roadmap](./docs/PROJECT_ROADMAP.md)** - Development progress and plans
- **[Production Improvements](./docs/PRODUCTION_IMPROVEMENTS.md)** - NuGet package implementation
- **[NuGet Implementation](./docs/NUGET_IMPLEMENTATION.md)** - Contract packaging details

### Service-Specific Documentation
- [Vector DB Service](./vector-db-service/README.md) - Python gRPC service
- [API Gateway](./api-gateway/README.md) - ASP.NET Core REST API
- [AI Agent](./ai-agent/README.md) - LangGraph AI workflows

## 🤝 Contributing

1. Clone the repository with submodules
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

See individual service repositories for licensing information.

---

**Built with** ❤️ **for enterprise knowledge management**

