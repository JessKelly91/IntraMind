"""
Shared pytest fixtures for IntraMind integration tests.

This module provides common fixtures used across all integration tests,
including service health checks, API clients, and cleanup utilities.
"""

import pytest
import requests
import uuid
from typing import List, Callable
import time
import os


# Service Configuration (with environment variable overrides for CI)
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:64536")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
REQUIRE_OLLAMA = os.getenv("REQUIRE_OLLAMA", "true").lower() == "true"

# Timeouts
SERVICE_CHECK_TIMEOUT = 5
API_REQUEST_TIMEOUT = 30


@pytest.fixture(scope="session", autouse=True)
def check_services_running():
    """
    Verify all required services are running before tests start.

    This fixture runs once at the start of the test session and validates
    that all microservices are accessible. If any service is down, all tests
    will be skipped with a clear error message.

    Services checked:
    - API Gateway (configurable via API_GATEWAY_URL env var)
    - Weaviate (configurable via WEAVIATE_URL env var)
    - Ollama (configurable via OLLAMA_URL env var, optional if REQUIRE_OLLAMA=false)
    """
    # Build services dict - Ollama is optional based on REQUIRE_OLLAMA
    services = {
        "API Gateway": f"{API_GATEWAY_URL}/health",
        "Weaviate": f"{WEAVIATE_URL}/v1/.well-known/ready",
    }

    if REQUIRE_OLLAMA:
        services["Ollama"] = f"{OLLAMA_URL}/api/tags"

    print("\n" + "="*60)
    print("Checking service availability...")
    if not REQUIRE_OLLAMA:
        print("  (Ollama is optional - skipping check)")
    print("="*60)

    failed_services = []

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=SERVICE_CHECK_TIMEOUT)
            if response.status_code in [200, 204]:
                print(f"✓ {name:<20} [HEALTHY]")
            else:
                print(f"✗ {name:<20} [UNHEALTHY] Status: {response.status_code}")
                failed_services.append(f"{name} returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ {name:<20} [UNREACHABLE] Cannot connect to {url}")
            failed_services.append(f"{name} is not accessible at {url}")
        except requests.exceptions.Timeout:
            print(f"✗ {name:<20} [TIMEOUT] No response within {SERVICE_CHECK_TIMEOUT}s")
            failed_services.append(f"{name} timed out")
        except Exception as e:
            print(f"✗ {name:<20} [ERROR] {str(e)}")
            failed_services.append(f"{name} error: {str(e)}")

    print("="*60)

    if failed_services:
        error_msg = (
            "\n\n❌ PREREQUISITE CHECK FAILED\n\n"
            "The following services are not available:\n"
            + "\n".join(f"  - {service}" for service in failed_services)
            + "\n\nPlease start all required services before running integration tests.\n"
            "See tests/integration/README.md for setup instructions.\n"
        )
        pytest.exit(error_msg, returncode=1)

    print("✓ All required services are healthy. Starting tests...\n")


@pytest.fixture
def api_client() -> requests.Session:
    """
    Provides an HTTP client for API Gateway requests.
    
    Returns:
        requests.Session: Configured session with timeout defaults
    """
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    return session


@pytest.fixture
def unique_collection_name() -> str:
    """
    Generate a unique collection name for test isolation.
    
    Each test that creates a collection should use this fixture to ensure
    tests don't interfere with each other.
    
    Returns:
        str: Unique collection name in format 'test_integration_{uuid}'
    """
    return f"test_integration_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def cleanup_collection(api_client: requests.Session) -> Callable[[str], None]:
    """
    Provides a cleanup function for test collections.
    
    This fixture yields a function that can be called to register collections
    for cleanup. All registered collections are deleted after the test completes.
    
    Usage:
        def test_something(cleanup_collection, unique_collection_name):
            cleanup_collection(unique_collection_name)
            # ... test code ...
            # Collection is automatically deleted after test
    
    Args:
        api_client: HTTP client session
        
    Yields:
        Callable: Function to register collections for cleanup
    """
    collections_to_delete: List[str] = []
    
    def register_cleanup(collection_name: str) -> None:
        """Register a collection for cleanup after test."""
        if collection_name not in collections_to_delete:
            collections_to_delete.append(collection_name)
    
    yield register_cleanup
    
    # Cleanup phase
    for collection in collections_to_delete:
        try:
            response = api_client.delete(
                f"{API_GATEWAY_URL}/v1/collections/{collection}",
                timeout=10
            )
            if response.status_code in [200, 204, 404]:
                print(f"  Cleaned up collection: {collection}")
            else:
                print(f"  Warning: Failed to cleanup {collection}: {response.status_code}")
        except Exception as e:
            print(f"  Warning: Error cleaning up {collection}: {e}")


@pytest.fixture
def wait_for_indexing():
    """
    Provides a function to wait for Weaviate indexing to complete.
    
    After inserting documents, there may be a brief delay before they're
    available for search. This fixture provides a simple wait mechanism.
    
    Yields:
        Callable: Function that waits for specified seconds
    """
    def wait(seconds: float = 1.0) -> None:
        """Wait for Weaviate to index documents."""
        time.sleep(seconds)
    
    return wait


@pytest.fixture(scope="session")
def performance_baseline():
    """
    Provides performance baseline thresholds for tests.
    
    Returns:
        dict: Performance thresholds in milliseconds
    """
    return {
        "search_latency_ms": 500,      # Single search should be < 500ms
        "batch_insert_ms": 5000,       # 100 docs should insert in < 5s
        "concurrent_search_ms": 1000,  # Concurrent searches < 1s each
    }

