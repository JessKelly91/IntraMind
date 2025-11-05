# IntraMind Docker Compose Setup Guide

> Complete guide for running IntraMind platform with Docker Compose

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Service Details](#service-details)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Development Workflows](#development-workflows)

---

## 🏗️ Architecture Overview

The IntraMind platform uses Docker Compose to orchestrate multiple services:

```
┌─────────────────────────────────────────────────────┐
│  Host Machine                                       │
│  ┌────────────┐          ┌─────────────────────┐  │
│  │  Ollama    │          │   AI Agent CLI      │  │
│  │  :11434    │          │   (Python)          │  │
│  └────────────┘          └─────────────────────┘  │
│        │                           │                │
│        │                           ▼                │
│        │                  ┌─────────────────────┐  │
│        │                  │  Docker Network     │  │
│        │                  │  intramind-network  │  │
│        │                  │                     │  │
│        │                  │  ┌──────────────┐  │  │
│        │                  │  │ API Gateway  │  │  │
│        │                  │  │   :5000      │  │  │
│        │                  │  └──────┬───────┘  │  │
│        │                  │         │          │  │
│        │                  │  ┌──────▼───────┐  │  │
│        │                  │  │Vector Service│  │  │
│        │                  │  │   :50052     │  │  │
│        │                  │  └──────┬───────┘  │  │
│        │                  │         │          │  │
│        │                  │  ┌──────▼───────┐  │  │
│        │                  │  │   Weaviate   │  │  │
│        │                  │  │    :8080     │  │  │
│        │                  │  └──────┬───────┘  │  │
│        │                  │         │          │  │
│        │                  │  ┌──────▼────────┐ │  │
│        │                  │  │ Transformers  │ │  │
│        │                  │  │   (internal)  │ │  │
│        │                  │  └───────────────┘ │  │
│        │                  └─────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Service Dependencies

```
Startup Order:
1. t2v-transformers (embedding model)
2. weaviate (waits for transformers to be healthy)
3. vector-service (waits for weaviate to be healthy)
4. api-gateway (waits for vector-service to be healthy)

External:
- Ollama (runs on host)
- AI Agent CLI (runs on host, connects to api-gateway)
```

---

## ✅ Prerequisites

### Required Software

1. **Docker Desktop** (or Docker Engine + Docker Compose)
   - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - Mac: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [Docker Engine](https://docs.docker.com/engine/install/)

2. **Git** (with submodule support)
   - [Download Git](https://git-scm.com/downloads)

3. **Python 3.11+** (for AI Agent CLI)
   - [Download Python](https://www.python.org/downloads/)

4. **Ollama** (for local LLM)
   - [Download Ollama](https://ollama.ai/)

### System Requirements

- **RAM**: Minimum 8GB, recommended 16GB
- **Disk Space**: ~5GB free space
  - Weaviate + Transformers: ~2GB
  - Docker images: ~2GB
  - Data volumes: ~1GB (grows with usage)
- **Network**: Internet connection for initial Docker image downloads

---

## 🚀 Quick Start

### Step 1: Clone Repository

```bash
# Clone with all submodules
git clone --recurse-submodules https://github.com/JessKelly91/IntraMind.git
cd IntraMind

# Or if already cloned, initialize submodules
git submodule update --init --recursive
```

### Step 2: Install and Start Ollama

```bash
# Download and install from https://ollama.ai/

# Pull the model (one-time, ~2GB download)
ollama pull llama3.2:3b

# Start Ollama server (keep this running)
ollama serve
```

**Verification:**
```bash
# In a new terminal, test Ollama
curl http://localhost:11434/api/tags
```

### Step 3: Start Docker Services

```bash
# From IntraMind root directory
docker-compose up -d

# This will start:
# - t2v-transformers (embedding model)
# - weaviate (vector database)
# - vector-service (gRPC service)
# - api-gateway (REST API)
```

**Verification:**
```bash
# Check all services are running and healthy
docker-compose ps

# Expected output:
# NAME                        STATUS
# intramind-api-gateway       Up (healthy)
# intramind-vector-service    Up (healthy)
# intramind-weaviate          Up (healthy)
# intramind-transformers      Up (healthy)
```

### Step 4: Setup AI Agent

```bash
# Navigate to AI agent
cd ai-agent

# Install Python dependencies (one-time)
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env and add your API keys (optional - for cloud LLMs)
# nano .env  # or use your preferred editor
```

**Minimal `.env` configuration:**
```bash
API_GATEWAY_URL=http://localhost:5000
OLLAMA_BASE_URL=http://localhost:11434
PRIMARY_LLM_PROVIDER=ollama
ROUTER_LLM_PROVIDER=ollama
```

### Step 5: Test the System

```bash
# From ai-agent directory
python -m src.cli.main

# In the interactive CLI:
> search What is IntraMind?
```

---

## 🔍 Service Details

### 1. Weaviate (Vector Database)

**Container**: `intramind-weaviate`  
**Ports**: 8080 (HTTP), 50051 (gRPC internal)  
**Image**: `cr.weaviate.io/semitechnologies/weaviate:1.27.0`

**Health Check:**
```bash
curl http://localhost:8080/v1/.well-known/ready
```

**View Schema:**
```bash
curl http://localhost:8080/v1/schema
```

### 2. Text2Vec Transformers (Embedding Model)

**Container**: `intramind-transformers`  
**Ports**: Internal only  
**Image**: `sentence-transformers-all-MiniLM-L6-v2`

**Features:**
- Free, local embeddings (no API costs)
- Automatic vectorization of documents
- Fast inference (~50ms per document)

### 3. Vector Service (gRPC)

**Container**: `intramind-vector-service`  
**Ports**: 50052 (gRPC)  
**Language**: Python 3.11  
**Protocol**: gRPC (Protocol Buffers)

**RPC Methods:**
- `CreateCollection`, `DeleteCollection`, `ListCollections`, `GetCollection`
- `InsertVector`, `InsertVectorBatch`
- `GetVector`, `UpdateVector`, `DeleteVector`
- `SemanticSearch`, `StreamSearch`
- `HealthCheck`

### 4. API Gateway (REST)

**Container**: `intramind-api-gateway`  
**Ports**: 5000 (HTTP)  
**Language**: C# (.NET 8.0)  
**Framework**: ASP.NET Core

**Swagger UI:**
```
http://localhost:5000/swagger
```

**Health Endpoints:**
```bash
curl http://localhost:5000/health
curl http://localhost:5000/health/liveness
curl http://localhost:5000/health/readiness
```

---

## ⚙️ Configuration

### Environment Variables

The platform can be configured via environment variables. Copy `.env.template` to `.env` and customize:

```bash
# Platform-wide settings
COMPOSE_PROJECT_NAME=intramind
LOG_LEVEL=Information

# Weaviate
WEAVIATE_URL=http://weaviate:8080

# Vector Service
GRPC_PORT=50052

# API Gateway
API_GATEWAY_PORT=5000
VECTOR_SERVICE_ENDPOINT=http://vector-service:50052

# AI Agent (for CLI usage)
API_GATEWAY_URL=http://localhost:5000
OLLAMA_BASE_URL=http://localhost:11434
PRIMARY_LLM_PROVIDER=anthropic  # or openai, ollama
ANTHROPIC_API_KEY=your_key_here
```

### Volume Mounts

**Data Persistence:**
```yaml
volumes:
  weaviate_data:
    # Location: Docker volume (managed by Docker)
    # Contains: Weaviate database and indexes
    # Size: Grows with stored documents
```

**View Volume:**
```bash
docker volume inspect intramind_weaviate_data
```

**Backup Volume:**
```bash
docker run --rm -v intramind_weaviate_data:/data -v $(pwd):/backup ubuntu tar czf /backup/weaviate_backup.tar.gz /data
```

### Network Configuration

**Internal Network**: `intramind-network`
- Type: Bridge network
- Services communicate via service names
- Isolated from host network

**Exposed Ports:**
- `8080` → Weaviate HTTP API
- `50051` → Weaviate gRPC (not typically used directly)
- `50052` → Vector Service gRPC
- `5000` → API Gateway REST

---

## 🔧 Troubleshooting

### Services Won't Start

**1. Check Docker is running:**
```bash
docker info
```

**2. Check port conflicts:**
```bash
# Windows
netstat -ano | findstr :8080
netstat -ano | findstr :5000

# Mac/Linux
lsof -i :8080
lsof -i :5000
```

**3. Check logs:**
```bash
docker-compose logs weaviate
docker-compose logs vector-service
docker-compose logs api-gateway
```

### Service is Unhealthy

**Check specific service health:**
```bash
docker-compose ps
docker inspect intramind-weaviate --format='{{.State.Health.Status}}'
```

**Common issues:**

1. **Weaviate unhealthy**: Transformers not ready
   ```bash
   # Check transformers logs
   docker-compose logs t2v-transformers
   
   # Restart services
   docker-compose restart t2v-transformers weaviate
   ```

2. **Vector Service unhealthy**: Can't connect to Weaviate
   ```bash
   # Check Weaviate is accessible from container
   docker-compose exec vector-service curl http://weaviate:8080/v1/.well-known/ready
   ```

3. **API Gateway unhealthy**: Can't connect to Vector Service
   ```bash
   # Check Vector Service is accessible
   docker-compose exec api-gateway wget --spider http://vector-service:50052
   ```

### AI Agent Can't Connect

**1. Verify API Gateway is accessible:**
```bash
curl http://localhost:5000/health
```

**2. Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**3. Verify .env configuration:**
```bash
cd ai-agent
cat .env | grep API_GATEWAY_URL
# Should show: API_GATEWAY_URL=http://localhost:5000
```

### Clean Slate Restart

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove all images (optional)
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

---

## 💻 Development Workflows

### Working on Individual Services

**Rebuild a specific service:**
```bash
# After making changes to vector-service code
docker-compose build vector-service
docker-compose up -d vector-service

# Or rebuild and restart in one command
docker-compose up -d --build vector-service
```

**View service logs:**
```bash
# Follow logs in real-time
docker-compose logs -f api-gateway

# View last 100 lines
docker-compose logs --tail=100 vector-service

# View all logs
docker-compose logs
```

### Isolated Service Testing

Each submodule has its own `docker-compose.yml` for isolated testing:

**API Gateway isolated testing:**
```bash
cd api-gateway
docker-compose up -d
# This starts full stack (Weaviate, Vector Service, API Gateway)
# Uses different container names to avoid conflicts with main stack
```

**Vector Service isolated testing:**
```bash
cd vector-db-service
docker-compose up -d
# This starts only Weaviate + Transformers
# Vector Service runs via: python -m src.service.server
```

### Updating Submodules

```bash
# Update all submodules to latest
git submodule update --remote

# Update specific submodule
cd vector-db-service
git pull origin main
cd ..

# Commit submodule reference updates
git add vector-db-service
git commit -m "Update vector-db-service submodule"
git push
```

### Hot Reload Development

**API Gateway** (ASP.NET Core):
```bash
cd api-gateway/src/IntraMind.ApiGateway
dotnet watch run
# API runs on host, connects to Docker services
```

**Vector Service** (Python):
```bash
cd vector-db-service
python -m src.service.server
# Server runs on host, connects to Docker Weaviate
```

**AI Agent** (Python):
```bash
cd ai-agent
python -m src.cli.main
# Always runs on host
```

---

## 📊 Monitoring

### Resource Usage

```bash
# View resource consumption
docker stats

# View disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Health Dashboard

Access service health endpoints:

- **API Gateway**: http://localhost:5000/health
- **Weaviate**: http://localhost:8080/v1/.well-known/ready
- **Swagger UI**: http://localhost:5000/swagger

---

## 🛑 Shutdown

### Graceful Shutdown

```bash
# Stop all services (preserves data)
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Emergency Stop

```bash
# Force stop all containers
docker-compose kill

# Remove everything
docker-compose rm -f
```

---

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [IntraMind Architecture](./ARCHITECTURE.md)
- [Project Roadmap](./PROJECT_ROADMAP.md)

---

**Last Updated**: November 5, 2025  
**Docker Compose Version**: 3.8  
**Platform Version**: 1.0.0

