# IntraMind Deployment Guide

> Complete deployment instructions for the IntraMind AI-powered document search platform

**Version**: 1.0.0
**Last Updated**: June 15, 2026
**Target Audience**: DevOps Engineers, System Administrators, Developers

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Deployment](#local-development-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Service-by-Service Setup](#service-by-service-setup)
7. [Health Checks & Monitoring](#health-checks--monitoring)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## Overview

### Architecture

IntraMind consists of a Dockerized core platform plus host-run AI/UI components:

```
┌──────────────────┐
│   AI Agent CLI   │  (Python - Host)
└────────┬─────────┘
         │ REST/HTTP
         ▼
┌──────────────────┐
│   API Gateway    │  (ASP.NET Core 8.0 - Port 5000)
└────────┬─────────┘
         │ gRPC
         ▼
┌──────────────────┐
│  Vector Service  │  (Python gRPC - Port 50052)
└────────┬─────────┘
         │ Weaviate Client
         ▼
┌──────────────────┐
│  Weaviate DB     │  (Vector Database - Port 8080)
│  + Transformers  │  (Free embeddings)
└──────────────────┘

AI Agent also talks to:
┌──────────────────┐
│ Prompt Registry  │  (FastAPI - Port 8010, Postgres host port 5433)
└──────────────────┘
┌──────────────────┐
│ Phoenix Tracing  │  (Port 6006)
└──────────────────┘
```

The root `docker-compose.yml` currently starts Weaviate, text2vec-transformers, Vector Service, API Gateway, Phoenix, Prompt Registry, and Prompt Registry Postgres. The AI Agent CLI and Web UI backend/widget are still run from the host for local development.

### Deployment Models

| Model | Use Case | Complexity |
|-------|----------|------------|
| **Local Development** | Development, testing, debugging | Low |
| **Host-Based Testing** | Integration testing, CI/CD | Medium |
| **Docker Production** | Production deployment | High |

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| **Docker** | 20.10+ | Container runtime |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Git** | 2.30+ | Version control |
| **Python** | 3.10+ | AI Agent runtime |
| **Ollama** | Latest | Local LLM for AI Agent |
| **.NET SDK** | 8.0+ | For local API Gateway development |

### System Requirements

#### Minimum (Development)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 20 GB free
- **Network**: Internet for Docker image pulls

#### Recommended (Production)
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 50+ GB SSD
- **Network**: Low latency, high bandwidth

---

## Local Development Deployment

### Quick Start (5 Minutes)

**Step 1: Clone Repository with Submodules**

```bash
# Clone with all submodules
git clone --recurse-submodules https://github.com/JessKelly91/IntraMind.git
cd IntraMind

# If already cloned, initialize submodules
git submodule update --init --recursive
```

**Step 2: Install Ollama (One-time)**

```bash
# Install from https://ollama.ai/
# Then pull the required model:
ollama pull llama3.2:3b

# Start Ollama (keep running in background)
ollama serve
```

**Step 3: Start Backend Services**

```bash
# Start Weaviate, Transformers, Vector Service, API Gateway,
# Phoenix, Prompt Registry, and Prompt Registry Postgres
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Verify health
curl http://localhost:8080/v1/.well-known/ready  # Weaviate
curl http://localhost:5000/health                # API Gateway
curl http://localhost:8010/health                # Prompt Registry
curl http://localhost:6006/                      # Phoenix UI
```

**Step 4: Configure and Run AI Agent**

```bash
# Navigate to AI Agent
cd ai-agent

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY or OPENAI_API_KEY (optional)

# Run interactive CLI
python -m src.cli.main

# Or run a quick search test
python -m src.cli.main search "test query"
```

**You're now running IntraMind locally!**

### Service URLs

Once deployed, services are available at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Weaviate** | http://localhost:8080 | Vector database REST API |
| **Vector Service** | http://localhost:50052 | gRPC vector service |
| **API Gateway** | http://localhost:5000 | REST API |
| **API Gateway Swagger** | http://localhost:5000/swagger | API documentation |
| **Prompt Registry** | http://localhost:8010 | Versioned prompt registry and static admin UI |
| **Phoenix** | http://localhost:6006 | Local tracing UI |

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All secrets configured (API keys, database credentials)
- [ ] Environment variables set for production
- [ ] Docker images built and tested
- [ ] Persistent volumes configured
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Health checks validated
- [ ] Load testing completed

### Production Docker Deployment

**Step 1: Prepare Environment File**

```bash
# Create production environment file
cp .env.example .env.production

# Edit with production values
nano .env.production
```

Required production environment variables:

```bash
# Weaviate
WEAVIATE_URL=http://weaviate:8080
WEAVIATE_KEY=your-production-key

# API Gateway
ASPNETCORE_ENVIRONMENT=Production
ASPNETCORE_URLS=http://+:8080

# Vector Service
GRPC_PORT=50052
ENVIRONMENT=Production

# AI Agent (optional)
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
API_GATEWAY_URL=http://api-gateway:5000

# Prompt Registry
PROMPT_REGISTRY_ADMIN_API_KEY=replace-with-secure-admin-key
PROMPT_REGISTRY_SERVICE_API_KEY=replace-with-secure-service-key
PROMPT_REGISTRY_AUTH_DEV_MODE=false
PROMPT_REGISTRY_AUTO_CREATE_SCHEMA=false
PROMPT_REGISTRY_DATABASE_URL=postgresql+asyncpg://user:password@host:5432/intramind_prompt_registry
```

For production-style Prompt Registry deployment, run `alembic upgrade head` before starting the service or provide an equivalent migration step. The local compose file defaults `PROMPT_REGISTRY_AUTO_CREATE_SCHEMA=true` for convenience.

**Step 2: Build and Start Services**

```bash
# Build all services
docker-compose build

# Start in production mode
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Step 3: Verify Deployment**

```bash
# Run health checks
./scripts/health-check.sh  # Create this script (see below)

# Or manually check each service:
curl http://localhost:8080/v1/.well-known/ready
curl http://localhost:5000/health/liveness
curl http://localhost:5000/health/readiness
curl http://localhost:8010/health
curl http://localhost:6006/
```

### Health Check Script

Create `scripts/health-check.sh`:

```bash
#!/bin/bash

echo "Checking IntraMind services..."

# Check Weaviate
if curl -f -s http://localhost:8080/v1/.well-known/ready > /dev/null; then
    echo "✓ Weaviate: Healthy"
else
    echo "✗ Weaviate: Unhealthy"
    exit 1
fi

# Check API Gateway
if curl -f -s http://localhost:5000/health > /dev/null; then
    echo "✓ API Gateway: Healthy"
else
    echo "✗ API Gateway: Unhealthy"
    exit 1
fi

# Check Prompt Registry
if curl -f -s http://localhost:8010/health > /dev/null; then
    echo "✓ Prompt Registry: Healthy"
else
    echo "✗ Prompt Registry: Unhealthy"
    exit 1
fi

echo "All services healthy!"
```

Make executable: `chmod +x scripts/health-check.sh`

---

## Environment Configuration

### Development Environment Variables

**API Gateway** (`api-gateway/src/IntraMind.ApiGateway/appsettings.Development.json`):

```json
{
  "VectorService": {
    "Endpoint": "http://localhost:50052"
  },
  "Serilog": {
    "MinimumLevel": {
      "Default": "Debug"
    }
  }
}
```

**Vector Service** (`vector-db-service/.env`):

```bash
ENVIRONMENT=Local
WEAVIATE_URL=http://localhost:8080
WEAVIATE_KEY=
GRPC_PORT=50052
APPLICATION_ID=intramind-vector-service
```

**AI Agent** (`ai-agent/.env`):

```bash
# API Gateway
API_GATEWAY_URL=http://localhost:5000

# Primary LLM for synthesis
PRIMARY_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxx
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# Router LLM (local - free)
ROUTER_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Agent settings
DEFAULT_COLLECTION=intramind_documents
SEARCH_LIMIT=10
ENABLE_STREAMING=true
AGENT_VERBOSE=true

# Conversation memory
ENABLE_CONVERSATION_MEMORY=true
MAX_CONVERSATION_HISTORY=5
CHECKPOINT_STORAGE_PATH=./data/checkpoints.db

# Runtime prompt registry (optional; unset URL keeps baked-in fallback behavior)
PROMPT_REGISTRY_URL=http://localhost:8010
PROMPT_REGISTRY_LABEL=production
PROMPT_REGISTRY_API_KEY=service-dev-key
PROMPT_REGISTRY_CACHE_TTL=60
```

### Production Environment Variables

**Docker Compose Environment**:

```yaml
# In docker-compose.yml or separate .env file
environment:
  # Weaviate
  - WEAVIATE_URL=http://weaviate:8080
  - WEAVIATE_KEY=${WEAVIATE_PRODUCTION_KEY}

  # API Gateway
  - ASPNETCORE_ENVIRONMENT=Production
  - VectorService__Endpoint=http://vector-service:50052

  # Vector Service
  - ENVIRONMENT=Production
  - GRPC_PORT=50052

  # Observability
  - ENABLE_TRACING=true
  - PHOENIX_ENDPOINT=http://phoenix:6006

  # Prompt Registry
  - PROMPT_REGISTRY_AUTH_DEV_MODE=false
  - PROMPT_REGISTRY_ADMIN_API_KEY=${PROMPT_REGISTRY_ADMIN_API_KEY}
  - PROMPT_REGISTRY_SERVICE_API_KEY=${PROMPT_REGISTRY_SERVICE_API_KEY}
```

---

## Service-by-Service Setup

### 1. Weaviate Database

**Purpose**: Vector storage and semantic search

**Deployment**:

```bash
# Included in docker-compose.yml
# Starts automatically with docker-compose up
```

**Configuration**:

```yaml
weaviate:
  image: cr.weaviate.io/semitechnologies/weaviate:1.27.0
  ports:
    - "8080:8080"
  environment:
    AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'  # Disable for production
    DEFAULT_VECTORIZER_MODULE: 'text2vec-transformers'
    PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
  volumes:
    - weaviate_data:/var/lib/weaviate  # Persistent storage
```

**Health Check**:

```bash
curl http://localhost:8080/v1/.well-known/ready
# Expected: HTTP 200
```

**Data Persistence**:
- Data stored in Docker volume `weaviate_data`
- Survives container restarts
- To wipe data: `docker-compose down -v`

---

### 2. Vector Database Service

**Purpose**: gRPC service for vector operations

**Repository**: `vector-db-service/` (submodule)

**Deployment**:

```bash
# Build and start via docker-compose
docker-compose up -d vector-service

# Or build manually
cd vector-db-service
docker build -t intramind-vector-service .
```

**Configuration**:

```bash
# Environment variables
WEAVIATE_URL=http://weaviate:8080
GRPC_PORT=50052
ENVIRONMENT=Production
```

**Health Check**:

```bash
# gRPC health check (requires grpcurl)
grpcurl -plaintext localhost:50052 list

# From API Gateway (indirect check)
curl http://localhost:5000/v1/collections
```

**Logs**:

```bash
docker-compose logs -f vector-service
```

---

### 3. API Gateway

**Purpose**: REST API layer with Swagger documentation

**Repository**: `api-gateway/` (submodule)

**Local Development** (without Docker):

```bash
cd api-gateway/src/IntraMind.ApiGateway

# Set environment to use local contracts
export UseLocalContracts=true  # Linux/macOS
$env:UseLocalContracts="true"  # PowerShell

# Run
dotnet restore
dotnet build
dotnet run

# Access at http://localhost:5000
```

**Docker Deployment**:

```bash
# Build
cd api-gateway
docker build -f src/IntraMind.ApiGateway/Dockerfile -t intramind-api-gateway .

# Or via docker-compose
docker-compose up -d api-gateway
```

**Health Checks**:

```bash
# General health
curl http://localhost:5000/health

# Kubernetes liveness probe
curl http://localhost:5000/health/liveness

# Kubernetes readiness probe (checks gRPC connection)
curl http://localhost:5000/health/readiness
```

**Swagger UI**:

Open http://localhost:5000/swagger for interactive API documentation

---

### 4. AI Agent

**Purpose**: Intelligent document search and ingestion

**Repository**: `ai-agent/` (submodule)

**Installation**:

```bash
cd ai-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys
```

**Running**:

```bash
# Interactive CLI
python -m src.cli.main

# Single query
python -m src.cli.main search "your query"

# Check health
python -m src.cli.main health

# View configuration
python -m src.cli.main info
```

**Docker Deployment** (optional):

```bash
cd ai-agent
docker build -t intramind-ai-agent .
docker run -it --network intramind-network intramind-ai-agent
```

---

### 5. Prompt Registry

**Purpose**: Versioned runtime prompt source for the AI Agent, with labels (`production`, `candidate`, `staging`), audit history, eval attachments, and code-registry fallback.

**Repository**: `prompt-registry/` (submodule)

**Deployment**:

```bash
# Included in root docker-compose.yml
docker-compose up -d prompt-registry-db prompt-registry

# Seed initial prompt versions from ai-agent/src/prompts/registry.py
curl -X POST http://localhost:8010/api/v1/admin/seed \
  -H "X-API-Key: admin-dev-key"
```

**Production notes**:
- Replace dev keys and database credentials.
- Run Alembic migrations explicitly when `PROMPT_REGISTRY_AUTO_CREATE_SCHEMA=false`.
- Ensure the service can access the AI Agent code registry for seeding, either through the compose mount used locally or a production-specific source path.

---

## Health Checks & Monitoring

### Service Health Endpoints

| Service | Health Endpoint | Expected Response |
|---------|----------------|-------------------|
| Weaviate | `GET http://localhost:8080/v1/.well-known/ready` | HTTP 200 |
| API Gateway | `GET http://localhost:5000/health` | HTTP 200, JSON status |
| API Gateway Liveness | `GET http://localhost:5000/health/liveness` | HTTP 200 |
| API Gateway Readiness | `GET http://localhost:5000/health/readiness` | HTTP 200 |
| Prompt Registry | `GET http://localhost:8010/health` | HTTP 200, DB status |
| Phoenix | `GET http://localhost:6006/` | HTTP 200 |

### Automated Health Monitoring

**Docker Compose** includes built-in health checks:

```yaml
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8080/v1/.well-known/ready"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**Check Service Health**:

```bash
# Via docker-compose
docker-compose ps

# Healthy services show (healthy) status
```

### Integration Tests

Run platform-wide integration tests:

```bash
cd tests

# Setup test environment
./setup.ps1  # Windows
./setup.sh   # Linux/macOS

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Run all integration tests
pytest tests/integration/ -v

# Run specific test categories
pytest -m health      # Health check tests only
pytest -m smoke       # Smoke tests only
pytest -m e2e         # End-to-end tests only
```

**Expected Result**: Core platform tests pass, with vectorizer-dependent tests skipped in CI mode. Prompt Registry has platform smoke coverage, but submodule unit tests are not currently enforced by the superproject CI.

---

## Troubleshooting

### Common Issues

#### 1. Docker Service Won't Start

**Symptom**: `docker-compose up` fails

**Diagnosis**:

```bash
# Check Docker daemon
docker ps

# Check Docker Compose logs
docker-compose logs

# Check specific service
docker-compose logs vector-service
```

**Solutions**:
- Ensure Docker Desktop is running
- Check port conflicts (8080, 5000, 50052, 5433, 6006, 8010)
- Verify submodules are initialized: `git submodule update --init --recursive`

#### 2. API Gateway Can't Connect to Vector Service

**Symptom**: API Gateway health check fails with gRPC errors

**Diagnosis**:

```bash
# Check vector service is running
docker-compose ps vector-service

# Check vector service logs
docker-compose logs vector-service

# Test gRPC port
telnet localhost 50052
```

**Solutions**:
- Ensure vector-service is healthy
- Check `VectorService__Endpoint` configuration in API Gateway
- Verify network connectivity: `docker network inspect intramind-network`

#### 3. Weaviate Not Ready

**Symptom**: Weaviate health check returns 503

**Diagnosis**:

```bash
# Check Weaviate and transformers containers
docker-compose ps weaviate t2v-transformers

# Check Weaviate logs
docker-compose logs weaviate
```

**Solutions**:
- Wait longer (transformers model loads slowly ~30-60 seconds)
- Check if transformers container is healthy
- Restart: `docker-compose restart weaviate t2v-transformers`

#### 4. AI Agent Can't Connect to API Gateway

**Symptom**: Connection errors when running AI Agent

**Diagnosis**:

```bash
# Check API Gateway is accessible
curl http://localhost:5000/health

# Check AI Agent configuration
cat ai-agent/.env | grep API_GATEWAY_URL
```

**Solutions**:
- Verify API Gateway is running and healthy
- Check `API_GATEWAY_URL` in `.env` (should be `http://localhost:5000`)
- Verify no firewall blocking port 5000

#### 5. Ollama Not Found

**Symptom**: AI Agent fails with Ollama connection errors

**Diagnosis**:

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check if model is installed
ollama list
```

**Solutions**:
- Install Ollama from https://ollama.ai/
- Pull required model: `ollama pull llama3.2:3b`
- Start Ollama: `ollama serve`

#### 6. Prompt Registry Can't Seed

**Symptom**: `POST /api/v1/admin/seed` fails.

**Diagnosis**:

```bash
docker-compose logs prompt-registry
curl http://localhost:8010/health
```

**Solutions**:
- Verify the `./ai-agent:/workspace/ai-agent:ro` mount exists in compose.
- Verify `PROMPT_REGISTRY_AI_AGENT_SRC_PATH=/workspace/ai-agent/src`.
- Use the admin API key in `X-API-Key`.

### Log Analysis

**View All Logs**:

```bash
docker-compose logs -f --tail=100
```

**Service-Specific Logs**:

```bash
docker-compose logs -f weaviate
docker-compose logs -f vector-service
docker-compose logs -f api-gateway
docker-compose logs -f prompt-registry
docker-compose logs -f phoenix
```

**Search Logs for Errors**:

```bash
docker-compose logs | grep -i error
docker-compose logs | grep -i exception
```

---

## Maintenance

### Updating Services

**Update Submodules**:

```bash
# Update all submodules to latest
git submodule update --remote

# Or update specific submodule
cd api-gateway
git pull origin main
cd ..

# Commit submodule reference update
git add api-gateway
git commit -m "Update api-gateway submodule"
git push
```

**Rebuild After Updates**:

```bash
# Rebuild changed services
docker-compose build --no-cache api-gateway

# Restart services
docker-compose up -d
```

### Data Backup

**Weaviate Data**:

```bash
# Backup Weaviate volume
docker run --rm -v intramind_weaviate_data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/weaviate-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore from backup
docker run --rm -v intramind_weaviate_data:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/weaviate-backup-20251106.tar.gz -C /data
```

**AI Agent Checkpoints**:

```bash
# Backup conversation memory
cp -r ai-agent/data/checkpoints.db ./backups/checkpoints-$(date +%Y%m%d).db
```

### Scaling

**Horizontal Scaling**:

```bash
# Scale API Gateway (load balance with nginx/traefik)
docker-compose up -d --scale api-gateway=3

# Note: Requires load balancer configuration
```

**Vertical Scaling**:

```yaml
# In docker-compose.yml
api-gateway:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

### Upgrading

**Upgrade Weaviate Version**:

```yaml
# In docker-compose.yml
weaviate:
  image: cr.weaviate.io/semitechnologies/weaviate:1.28.0  # New version
```

**Upgrade .NET SDK** (API Gateway):

```bash
cd api-gateway
# Update global.json or .csproj
dotnet build
```

### Monitoring Production

**Recommended Tools**:
- **Metrics**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger or Application Insights
- **Uptime**: UptimeRobot or StatusCake

**Basic Monitoring Script** (cron job):

```bash
#!/bin/bash
# monitor.sh - Run every 5 minutes

if ! curl -f -s http://localhost:5000/health > /dev/null; then
    echo "API Gateway down!" | mail -s "IntraMind Alert" admin@company.com
    docker-compose restart api-gateway
fi
```

---

## Next Steps

1. **Configure production secrets** (API keys, database credentials)
2. **Enforce submodule unit tests in CI** for `ai-agent`, `api-gateway`, `vector-db-service`, and `prompt-registry`
3. **Containerize or CI-cover the web-ui**; it is currently host-run with manual testing
4. **Promote warning-only Ragas thresholds to a hard gate** once a stable baseline is established
5. **Configure production monitoring** (Prometheus/Grafana/ELK or equivalent plus Phoenix retention policy)
6. **Document runbooks** (migrations, prompt rollback, incident response)

---

## Additional Resources

- **Architecture Documentation**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **API Reference**: [API_REFERENCE.md](./API_REFERENCE.md)
- **User Guide**: [USER_GUIDE.md](./USER_GUIDE.md)
- **Submodule Management**: [SUBMODULE_GUIDE.md](./SUBMODULE_GUIDE.md)
- **Docker Setup Guide**: [DOCKER_SETUP.md](./DOCKER_SETUP.md)
- **NuGet Implementation**: [NUGET_IMPLEMENTATION.md](./NUGET_IMPLEMENTATION.md)

---

**Last Updated**: June 15, 2026
**Maintained By**: IntraMind Development Team
