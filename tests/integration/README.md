# IntraMind Platform Integration Tests

This directory contains **platform-level integration tests** that validate the entire IntraMind microservices stack working together.

## Overview

These tests are different from service-level tests found in individual submodules:

| Test Level | Location | Scope | Services Required |
|------------|----------|-------|-------------------|
| **Unit Tests** | Each submodule | Single service, mocked deps | None (mocks used) |
| **Service Integration** | Each submodule | Single service + real deps | Partial (e.g., just Weaviate) |
| **Platform Integration** | This directory | Dockerized core stack | API Gateway, Vector Service, Weaviate, Prompt Registry |

## Test Categories

### 🏥 Health Tests (`test_full_stack_health.py`)
Quick smoke tests to verify all services are running and can communicate.

**Tests:** 7 tests  
**Duration:** ~5 seconds  
**Markers:** `@pytest.mark.health`, `@pytest.mark.smoke`

### 🔄 End-to-End Workflow Tests (`test_end_to_end_workflows.py`)
Complete user scenarios across all services.

**Tests:** 8-10 tests  
**Duration:** ~2-3 minutes  
**Markers:** `@pytest.mark.e2e`

### 🚨 Error Scenario Tests (`test_error_scenarios.py`)
Validate error handling and propagation across service boundaries.

**Tests:** 6-8 tests  
**Duration:** ~1-2 minutes  
**Markers:** `@pytest.mark.error`

### ⚡ Performance Tests (`test_performance.py`)
Load testing and performance benchmarking.

**Tests:** 4-5 tests  
**Duration:** ~5-10 minutes  
**Markers:** `@pytest.mark.performance`, `@pytest.mark.slow`

### 🧾 Prompt Registry Tests (`test_prompt_registry.py`)
Validate Prompt Registry health/auth plus seed-and-resolve behavior through the platform compose stack.

**Tests:** 2 tests  
**Duration:** ~5-10 seconds  
**Markers:** `@pytest.mark.integration`

## Prerequisites

### Required Services

The recommended local path is to start the CI-optimized compose stack from the repository root:

```powershell
cd ..
docker compose -f docker-compose.ci.yml up -d
```

For full local semantic-search behavior, use `docker compose up -d` instead. That starts the heavier `text2vec-transformers` container.

### Service Endpoints

Tests expect services at these URLs (configurable via environment variables):

| Service | Default Local | CI Environment | Environment Variable |
|---------|---------------|----------------|---------------------|
| **API Gateway** | http://localhost:5000 | http://localhost:5000 | `API_GATEWAY_URL` |
| **Weaviate** | http://localhost:8080 | http://localhost:8080 | `WEAVIATE_URL` |
| **Prompt Registry** | http://localhost:8010 | http://localhost:8010 | `PROMPT_REGISTRY_URL` |
| **Ollama** | http://localhost:11434 | (not required) | `OLLAMA_URL` |

**Note:** CI uses `docker-compose.ci.yml`, disables the vectorizer for faster testing, and starts Prompt Registry with an ephemeral Postgres database. Web UI and AI Agent CLI are not started by the platform integration compose stack.

### Python Dependencies

**Option 1: Automated Setup (Recommended)**

```powershell
# Windows (PowerShell)
cd tests
.\setup.ps1

# Linux/Mac (Bash)
cd tests
chmod +x setup.sh
./setup.sh
```

**Option 2: Manual Setup**

```powershell
# Create virtual environment
cd tests
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

**Note:** Make sure your virtual environment is activated before running tests:

```powershell
# Windows
cd tests
.\venv\Scripts\Activate.ps1

# Linux/Mac
cd tests
source venv/bin/activate
```

### Run All Integration Tests

```powershell
pytest integration/ -v
```

### Run Specific Test Categories

```powershell
# Quick smoke tests only (health checks)
pytest integration/ -v -m smoke

# Health tests
pytest integration/ -v -m health

# End-to-end workflow tests
pytest integration/ -v -m e2e

# Skip slow tests
pytest integration/ -v -m "not slow"

# Performance tests only
pytest integration/ -v -m performance
```

### Run Specific Test Files

```powershell
# Health tests only
pytest integration/test_full_stack_health.py -v

# E2E workflows only
pytest integration/test_end_to_end_workflows.py -v

# Error scenarios only
pytest integration/test_error_scenarios.py -v

# Prompt Registry only
pytest integration/test_prompt_registry.py -v

# Performance tests only
pytest integration/test_performance.py -v
```

### Run Specific Tests

```powershell
# Run a single test by name
pytest integration/test_full_stack_health.py::test_api_gateway_health -v

# Run tests matching a pattern
pytest integration/ -v -k "health"
```

### Parallel Execution

```powershell
# Run tests in parallel (faster execution)
pytest integration/ -v -n 4  # 4 parallel workers

# Parallel with specific markers
pytest integration/ -v -n 4 -m "not slow"
```

### Generate HTML Report

```powershell
pytest integration/ -v --html=report.html --self-contained-html
```

## Test Output

### Successful Run

```
============= test session starts =============
platform win32 -- Python 3.11.0
plugins: pytest-asyncio, pytest-xdist, pytest-timeout

============================================================
Checking service availability...
============================================================
✓ API Gateway          [HEALTHY]
✓ Weaviate             [HEALTHY]
✓ Prompt Registry      [HEALTHY]
============================================================
✓ All services are healthy. Starting tests...

integration/test_full_stack_health.py::test_api_gateway_health PASSED
integration/test_full_stack_health.py::test_weaviate_readiness PASSED
integration/test_full_stack_health.py::test_ollama_availability PASSED
...

============= 7 passed in 5.23s =============
```

### Failed Prerequisites

If services are not running, you'll see:

```
❌ PREREQUISITE CHECK FAILED

The following services are not available:
  - API Gateway is not accessible at http://localhost:5000/health
  - Weaviate is not accessible at http://localhost:8080/v1/.well-known/ready
  - Prompt Registry is not accessible at http://localhost:8010/health

Please start all required services before running integration tests.
See tests/integration/README.md for setup instructions.
```

## Test Fixtures

### Available Fixtures (from `conftest.py`)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `api_client` | Function | Configured `requests.Session` for API calls |
| `unique_collection_name` | Function | Generates unique collection name for test isolation |
| `cleanup_collection` | Function | Registers collections for automatic cleanup |
| `wait_for_indexing` | Function | Wait helper for Weaviate indexing delays |
| `performance_baseline` | Session | Performance threshold values |
| `prompt_registry_url` | Session | Prompt Registry base URL |

### Example Usage

```python
def test_example(api_client, unique_collection_name, cleanup_collection):
    """Example test using common fixtures."""
    cleanup_collection(unique_collection_name)
    
    # Create collection
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"name": unique_collection_name}
    )
    assert response.status_code == 201
    
    # Collection automatically cleaned up after test
```

## Troubleshooting

### "Services not available" Error

**Problem:** Tests exit immediately with service availability errors.

**Solutions:**
1. Verify all services are running (check each terminal)
2. Check service health endpoints manually:
   ```powershell
   curl http://localhost:5000/health
   curl http://localhost:8080/v1/.well-known/ready
   curl http://localhost:8010/health
   curl http://localhost:11434/api/tags
   ```
3. Check ports are not in use by other applications
4. Restart services if needed

### Tests Timeout

**Problem:** Tests hang or timeout.

**Solutions:**
1. Check service logs for errors
2. Increase timeout in `pytest.ini` if needed
3. Verify network connectivity between services
4. Check Docker container health: `docker ps`

### Collection Already Exists Errors

**Problem:** Tests fail because test collections already exist.

**Solutions:**
1. Each test uses `unique_collection_name` fixture for isolation
2. Cleanup fixture should handle deletion automatically
3. Manually delete test collections if needed:
   ```powershell
   # List collections
   curl http://localhost:5000/v1/collections
   
   # Delete test collections
   curl -X DELETE http://localhost:5000/v1/collections/test_integration_xxxxx
   ```

### Performance Tests Too Slow

**Problem:** Performance tests exceed expected thresholds.

**Solutions:**
1. This is informational - baseline may need adjustment
2. Check system resources (CPU, memory, disk)
3. Ensure no other heavy processes are running
4. Consider if baseline thresholds are appropriate for your hardware

## Performance Baselines

Expected performance characteristics (may vary by hardware):

| Metric | Baseline | Notes |
|--------|----------|-------|
| Single search latency | < 500ms | Typical query with 10 results |
| Batch insert (100 docs) | < 5s | Throughput: >20 docs/sec |
| Concurrent searches (10) | < 1s each | No degradation under load |

## CI/CD Integration

### CI Environment Configuration

The test suite supports running in **CI mode without vectorizer** for faster test execution. This is automatically configured in the GitHub Actions CI pipeline.

**Environment Variables:**

| Variable | CI Value | Local Value | Purpose |
|----------|----------|-------------|---------|
| `VECTORIZER_ENABLED` | `false` | `true` | Controls whether vectorizer/semantic search tests run |
| `REQUIRE_OLLAMA` | `false` | `true` | Controls whether Ollama is required |
| `PROMPT_REGISTRY_URL` | `http://localhost:8010` | `http://localhost:8010` | Prompt Registry base URL |
| `PROMPT_REGISTRY_ADMIN_API_KEY` | `admin-dev-key` | `admin-dev-key` | Admin key for seed/promotion tests |
| `PROMPT_REGISTRY_SERVICE_API_KEY` | `service-dev-key` | `service-dev-key` | Service key for resolve tests |

**When `VECTORIZER_ENABLED=false`:**
- ✅ Collections are created with `vectorizer="none"` 
- ✅ Core functionality tests run, including Prompt Registry smoke tests
- ⏭️ Semantic search tests are automatically skipped (6 tests)
- ⚡ CI runs ~5 minutes faster (skips 8GB transformers model download)

**Tests Skipped in CI Mode:**
- `test_search_workflow_e2e` - Requires vectorizer for semantic search
- `test_search_without_query` - Search validation test
- `test_search_without_collection` - Search validation test  
- `test_search_invalid_limit` - Search validation test
- `test_search_performance` - Search performance benchmarking
- Search operation in `test_end_to_end_workflow_performance` - conditionally skipped

### Running Tests in CI Mode Locally

To test CI configuration locally:

```bash
# Set environment variables
export VECTORIZER_ENABLED=false
export REQUIRE_OLLAMA=false

# Start services in CI mode (no vectorizer)
docker compose -f docker-compose.ci.yml up -d

# Run tests
cd tests
pytest integration/ -v

# Expected: 34 passed, 6 skipped
#
# Exact counts may change as new integration tests are added; semantic-search
# tests remain skipped while VECTORIZER_ENABLED=false.
```

### GitHub Actions Integration

Example GitHub Actions workflow:

```yaml
- name: Start services (CI mode - no vectorizer)
  run: docker compose -f docker-compose.ci.yml up -d
  
- name: Wait for services
  run: |
    timeout 60 bash -c 'until curl -f http://localhost:5000/health; do sleep 2; done'
    timeout 60 bash -c 'until curl -f http://localhost:8080/v1/.well-known/ready; do sleep 2; done'
    timeout 60 bash -c 'until curl -f http://localhost:8010/health; do sleep 2; done'

- name: Run integration tests
  env:
    API_GATEWAY_URL: http://localhost:5000
    WEAVIATE_URL: http://localhost:8080
    PROMPT_REGISTRY_URL: http://localhost:8010
    PROMPT_REGISTRY_ADMIN_API_KEY: admin-dev-key
    PROMPT_REGISTRY_SERVICE_API_KEY: service-dev-key
    REQUIRE_OLLAMA: false
    VECTORIZER_ENABLED: false
  run: |
    cd tests
    pip install -r requirements.txt
    pytest integration/ -v --html=report.html
    
# Expected Results: core tests pass, vectorizer-dependent tests skip
```

See `.github/workflows/ci.yml` for the complete CI configuration.

## Contributing

When adding new integration tests:

1. Use appropriate markers (`@pytest.mark.integration`, `@pytest.mark.e2e`, etc.)
2. Use `unique_collection_name` and `cleanup_collection` fixtures
3. Add docstrings explaining what the test validates
4. Keep tests isolated (no dependencies between tests)
5. Update this README with new test categories

## Support

For issues or questions:
- Check service logs first
- Review troubleshooting section
- See main project README: `../../README.md`
- Check service-specific documentation in submodules

