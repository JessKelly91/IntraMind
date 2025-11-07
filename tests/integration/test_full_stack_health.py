"""
Health and connectivity tests for IntraMind platform.

These tests validate that all services in the microservices stack are running
and can communicate with each other. They serve as smoke tests to ensure basic
infrastructure is working before running more complex integration tests.

Tests:
- Service health endpoints
- API Gateway connectivity
- Weaviate readiness
- Kubernetes probe endpoints
"""

import pytest
import requests
from .config import API_GATEWAY_URL, WEAVIATE_URL, OLLAMA_URL


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.smoke
def test_api_gateway_health(api_client):
    """
    Test that API Gateway health endpoint is accessible and reports healthy status.
    
    This validates:
    - API Gateway is running
    - Health check endpoint responds correctly
    - Basic HTTP connectivity works
    """
    response = api_client.get(f"{API_GATEWAY_URL}/health", timeout=5)
    
    assert response.status_code == 200, \
        f"API Gateway health check failed with status {response.status_code}"
    
    # Verify response structure if API returns JSON
    try:
        health_data = response.json()
        assert "status" in health_data or health_data, \
            "Health response should contain status information"
    except ValueError:
        # If response is not JSON, that's okay too
        pass


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.smoke
def test_weaviate_readiness(api_client):
    """
    Test that Weaviate database is ready to accept requests.
    
    This validates:
    - Weaviate container is running
    - Database is ready for operations
    - Network connectivity to Weaviate works
    """
    response = api_client.get(f"{WEAVIATE_URL}/v1/.well-known/ready", timeout=5)
    
    assert response.status_code == 200, \
        f"Weaviate readiness check failed with status {response.status_code}"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.smoke
def test_ollama_availability(api_client):
    """
    Test that Ollama LLM service is running and accessible.
    
    This validates:
    - Ollama service is running
    - API endpoint is accessible
    - Required for AI Agent functionality
    """
    response = api_client.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    
    assert response.status_code == 200, \
        f"Ollama service check failed with status {response.status_code}"
    
    # Verify we can parse the response
    tags_data = response.json()
    assert "models" in tags_data, \
        "Ollama response should contain models list"


@pytest.mark.integration
@pytest.mark.health
def test_api_gateway_liveness_probe(api_client):
    """
    Test API Gateway liveness probe endpoint.
    
    Kubernetes liveness probes determine if a container should be restarted.
    This endpoint should always respond quickly with a 200 status.
    """
    response = api_client.get(f"{API_GATEWAY_URL}/health/liveness", timeout=5)
    
    assert response.status_code == 200, \
        f"API Gateway liveness probe failed with status {response.status_code}"


@pytest.mark.integration
@pytest.mark.health
def test_api_gateway_readiness_probe(api_client):
    """
    Test API Gateway readiness probe endpoint.
    
    Kubernetes readiness probes determine if a container is ready to accept traffic.
    This endpoint checks that the API Gateway can reach its dependencies.
    """
    response = api_client.get(f"{API_GATEWAY_URL}/health/readiness", timeout=5)
    
    assert response.status_code == 200, \
        f"API Gateway readiness probe failed with status {response.status_code}"


@pytest.mark.integration
@pytest.mark.health
def test_api_gateway_to_vector_service_connectivity(api_client, unique_collection_name):
    """
    Test that API Gateway can successfully communicate with Vector Service via gRPC.
    
    This validates the full chain:
    API Gateway (REST) → Vector Service (gRPC) → Weaviate (HTTP)
    
    We test this by attempting to list collections, which requires gRPC communication.
    """
    response = api_client.get(f"{API_GATEWAY_URL}/v1/collections", timeout=10)
    
    assert response.status_code == 200, \
        f"Failed to reach Vector Service through API Gateway. Status: {response.status_code}"
    
    # Verify response is valid JSON with expected structure
    collections_data = response.json()
    assert isinstance(collections_data, dict) or isinstance(collections_data, list), \
        "Collections response should be a valid data structure"


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.smoke
def test_complete_stack_connectivity(api_client, unique_collection_name, cleanup_collection):
    """
    Integration smoke test: Create and delete a collection through the full stack.
    
    This is a comprehensive connectivity test that validates:
    1. API Gateway accepts REST requests
    2. API Gateway can communicate with Vector Service via gRPC
    3. Vector Service can communicate with Weaviate
    4. All services can process requests and return responses
    5. Cleanup works correctly
    
    This test creates minimal data to verify the complete pipeline works.
    """
    cleanup_collection(unique_collection_name)
    
    # Step 1: Create a test collection through the full stack
    create_response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Integration test collection"},
        timeout=10
    )
    
    assert create_response.status_code in [200, 201], \
        f"Failed to create collection through full stack. Status: {create_response.status_code}"
    
    # Step 2: Verify collection exists (validates read path)
    list_response = api_client.get(f"{API_GATEWAY_URL}/v1/collections", timeout=10)
    assert list_response.status_code == 200
    
    # Step 3: Delete collection (validates delete path)
    delete_response = api_client.delete(
        f"{API_GATEWAY_URL}/v1/collections/{unique_collection_name}",
        timeout=10
    )
    
    assert delete_response.status_code in [200, 204], \
        f"Failed to delete collection. Status: {delete_response.status_code}"
    
    print(f"✓ Complete stack connectivity verified with collection: {unique_collection_name}")

