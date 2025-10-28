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

- Git
- Docker & Docker Compose
- Python 3.11+

### Clone with Submodules

```bash
# Clone the repository with all submodules
git clone --recurse-submodules https://github.com/JessKelly91/IntraMind.git

# Or if you already cloned, initialize submodules
git clone https://github.com/JessKelly91/IntraMind.git
cd IntraMind
git submodule update --init --recursive
```

### Quick Start

```bash
# Navigate to vector-db-service
cd vector-db-service

# Follow setup instructions in the submodule's README
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

## 📚 Documentation

Each microservice contains its own detailed documentation:

- [Vector DB Service](./vector-db-service/README.md)

## 🤝 Contributing

1. Clone the repository with submodules
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

See individual service repositories for licensing information.

---

**Built with** ❤️ **for enterprise knowledge management**

