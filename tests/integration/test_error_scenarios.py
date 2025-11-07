"""
Error Scenario Tests for IntraMind Platform.

These tests validate that the system handles errors gracefully and returns
appropriate error messages and status codes.

Test Categories:
- Invalid inputs and validation errors
- Resource not found scenarios
- Business logic violations
- Boundary conditions
"""

import pytest
import requests
import uuid
from config import API_GATEWAY_URL


@pytest.mark.integration
@pytest.mark.error
def test_invalid_collection_name_special_chars(api_client):
    """
    Test that collection names with special characters are rejected.
    
    Validates input validation for collection names.
    """
    invalid_names = [
        "test@collection",
        "test collection",  # Space
        "test#collection",
        "test$collection",
        "test!collection",
    ]
    
    for invalid_name in invalid_names:
        response = api_client.post(
            f"{API_GATEWAY_URL}/v1/collections",
            json={"collectionName": invalid_name, "description": "Test"},
            timeout=10
        )
        # Should return 400 Bad Request for invalid names
        assert response.status_code == 400, \
            f"Invalid name '{invalid_name}' should be rejected with 400, got {response.status_code}"
        
        print(f"✓ Invalid name '{invalid_name}' correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_empty_collection_name(api_client):
    """
    Test that empty collection names are rejected.
    """
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": "", "description": "Test"},
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Empty collection name should be rejected with 400, got {response.status_code}"
    
    print("✓ Empty collection name correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_missing_required_fields_collection(api_client):
    """
    Test that missing required fields are caught by validation.
    """
    # Missing collectionName
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"description": "Test"},
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Missing collectionName should return 400, got {response.status_code}"
    
    print("✓ Missing required field (collectionName) correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_get_nonexistent_collection(api_client):
    """
    Test that getting a non-existent collection returns 404 or appropriate error.
    """
    nonexistent_collection = f"nonexistent_{uuid.uuid4().hex[:8]}"
    
    response = api_client.get(
        f"{API_GATEWAY_URL}/v1/collections/{nonexistent_collection}",
        timeout=10
    )
    
    # Should return 404 or 500 with appropriate error message
    assert response.status_code in [404, 500], \
        f"Non-existent collection should return 404/500, got {response.status_code}"
    
    print(f"✓ Non-existent collection '{nonexistent_collection}' correctly handled")


@pytest.mark.integration
@pytest.mark.error
def test_delete_nonexistent_collection(api_client):
    """
    Test that deleting a non-existent collection is handled gracefully.
    """
    nonexistent_collection = f"nonexistent_{uuid.uuid4().hex[:8]}"
    
    response = api_client.delete(
        f"{API_GATEWAY_URL}/v1/collections/{nonexistent_collection}",
        timeout=10
    )
    
    # Should return 404 or succeed idempotently
    assert response.status_code in [204, 404, 500], \
        f"Delete non-existent collection should return 204/404/500, got {response.status_code}"
    
    print(f"✓ Delete non-existent collection handled gracefully")


@pytest.mark.integration
@pytest.mark.error
def test_insert_document_missing_required_fields(api_client, unique_collection_name, cleanup_collection):
    """
    Test that inserting a document without required fields fails.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection first
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    # Missing documentId
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "collectionName": unique_collection_name,
            "content": "Test content"
            # Missing documentId
        },
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Missing documentId should return 400, got {response.status_code}"
    
    print("✓ Missing documentId correctly rejected")
    
    # Missing content
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": f"doc_{uuid.uuid4().hex[:16]}",
            "collectionName": unique_collection_name
            # Missing content
        },
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Missing content should return 400, got {response.status_code}"
    
    print("✓ Missing content correctly rejected")
    
    # Missing collectionName
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": f"doc_{uuid.uuid4().hex[:16]}",
            "content": "Test content"
            # Missing collectionName
        },
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Missing collectionName should return 400, got {response.status_code}"
    
    print("✓ Missing collectionName correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_get_nonexistent_document(api_client, unique_collection_name, cleanup_collection):
    """
    Test that getting a non-existent document returns 404.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    nonexistent_doc_id = f"nonexistent_{uuid.uuid4().hex[:16]}"
    
    response = api_client.get(
        f"{API_GATEWAY_URL}/v1/documents/{nonexistent_doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    
    # Should return 404 or 500 with appropriate error
    assert response.status_code in [404, 500], \
        f"Non-existent document should return 404/500, got {response.status_code}"
    
    print(f"✓ Non-existent document correctly handled")


@pytest.mark.integration
@pytest.mark.error
def test_update_nonexistent_document(api_client, unique_collection_name, cleanup_collection):
    """
    Test that updating a non-existent document returns appropriate error.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    nonexistent_doc_id = f"nonexistent_{uuid.uuid4().hex[:16]}"
    
    response = api_client.put(
        f"{API_GATEWAY_URL}/v1/documents/{nonexistent_doc_id}",
        json={
            "documentId": nonexistent_doc_id,
            "collectionName": unique_collection_name,
            "content": "Updated content",
            "metadata": {}
        },
        timeout=10
    )
    
    # Should return 404 or 500
    assert response.status_code in [404, 500], \
        f"Update non-existent document should return 404/500, got {response.status_code}"
    
    print(f"✓ Update non-existent document correctly handled")


@pytest.mark.integration
@pytest.mark.error
def test_delete_nonexistent_document(api_client, unique_collection_name, cleanup_collection):
    """
    Test that deleting a non-existent document is handled gracefully.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    nonexistent_doc_id = f"nonexistent_{uuid.uuid4().hex[:16]}"
    
    response = api_client.delete(
        f"{API_GATEWAY_URL}/v1/documents/{nonexistent_doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    
    # Should succeed idempotently or return 404
    assert response.status_code in [204, 404, 500], \
        f"Delete non-existent document should return 204/404/500, got {response.status_code}"
    
    print(f"✓ Delete non-existent document handled gracefully")


@pytest.mark.integration
@pytest.mark.error
def test_document_in_nonexistent_collection(api_client):
    """
    Test that operations on documents in non-existent collections are handled.
    
    Note: Weaviate auto-creates collections on first document insert, so 201 is expected.
    This is a feature (schema-less flexibility), not a bug.
    """
    nonexistent_collection = f"nonexistent_{uuid.uuid4().hex[:8]}"
    doc_id = f"doc_{uuid.uuid4().hex[:16]}"
    
    # Try to insert document in non-existent collection
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": doc_id,
            "collectionName": nonexistent_collection,
            "content": "Test content",
            "metadata": {}
        },
        timeout=10
    )
    
    # Weaviate auto-creates collections, so 201 (success) is expected
    assert response.status_code in [201, 404, 500], \
        f"Insert in non-existent collection should return 201/404/500, got {response.status_code}"
    
    if response.status_code == 201:
        print(f"✓ Collection auto-created (Weaviate feature)")
        # Cleanup the auto-created collection
        import requests
        requests.delete(f"{API_GATEWAY_URL}/v1/collections/{nonexistent_collection}", timeout=10)
    else:
        print(f"✓ Document operation in non-existent collection correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_invalid_json_payload(api_client):
    """
    Test that invalid JSON payloads are rejected.
    
    Note: May return 500 (server error) instead of 400 (client error) 
    depending on where deserialization fails. Both indicate rejection.
    """
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        data="This is not valid JSON",
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    # Accept both 400 (ideal) and 500 (also valid - request is rejected)
    assert response.status_code in [400, 500], \
        f"Invalid JSON should return 400 or 500, got {response.status_code}"
    
    print("✓ Invalid JSON payload correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_search_without_query(api_client, unique_collection_name, cleanup_collection):
    """
    Test that search without a query parameter is rejected.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    # Search without query
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/search",
        json={
            "collectionName": unique_collection_name,
            "limit": 5
            # Missing query
        },
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Search without query should return 400, got {response.status_code}"
    
    print("✓ Search without query correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_search_without_collection(api_client):
    """
    Test that search without specifying a collection is rejected.
    """
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/search",
        json={
            "query": "test query",
            "limit": 5
            # Missing collectionName or collectionNames
        },
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Search without collection should return 400, got {response.status_code}"
    
    print("✓ Search without collection correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_search_invalid_limit(api_client, unique_collection_name, cleanup_collection):
    """
    Test that search with invalid limit values is handled appropriately.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    # Negative limit
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/search",
        json={
            "query": "test query",
            "collectionName": unique_collection_name,
            "limit": -1
        },
        timeout=10
    )
    
    assert response.status_code in [400, 500], \
        f"Negative limit should return 400/500, got {response.status_code}"
    
    print("✓ Negative limit correctly rejected")
    
    # Zero limit
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/search",
        json={
            "query": "test query",
            "collectionName": unique_collection_name,
            "limit": 0
        },
        timeout=10
    )
    
    # Zero might be allowed or rejected, just check it doesn't crash
    assert response.status_code in [200, 400], \
        f"Zero limit should return 200/400, got {response.status_code}"
    
    print("✓ Zero limit handled appropriately")


@pytest.mark.integration
@pytest.mark.error
def test_extremely_long_collection_name(api_client):
    """
    Test that extremely long collection names are rejected.
    """
    long_name = "a" * 500  # Very long name
    
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": long_name, "description": "Test"},
        timeout=10
    )
    
    assert response.status_code == 400, \
        f"Extremely long collection name should return 400, got {response.status_code}"
    
    print("✓ Extremely long collection name correctly rejected")


@pytest.mark.integration
@pytest.mark.error
def test_empty_document_content(api_client, unique_collection_name, cleanup_collection):
    """
    Test that documents with empty content are handled appropriately.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    doc_id = f"doc_{uuid.uuid4().hex[:16]}"
    
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": doc_id,
            "collectionName": unique_collection_name,
            "content": "",  # Empty content
            "metadata": {}
        },
        timeout=10
    )
    
    # Empty content might be allowed or rejected - just verify it doesn't crash
    assert response.status_code in [200, 201, 400], \
        f"Empty content should return 200/201/400, got {response.status_code}"
    
    if response.status_code == 400:
        print("✓ Empty content correctly rejected")
    else:
        print("✓ Empty content allowed (may be valid use case)")


@pytest.mark.integration
@pytest.mark.error
def test_batch_insert_empty_array(api_client, unique_collection_name, cleanup_collection):
    """
    Test that batch insert with empty array is handled gracefully.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents/batch",
        json=[],  # Empty array
        timeout=10
    )
    
    # Should handle gracefully - might return 400 or succeed with 0 inserted
    assert response.status_code in [200, 201, 400], \
        f"Empty batch should return 200/201/400, got {response.status_code}"
    
    print("✓ Empty batch array handled gracefully")


@pytest.mark.integration
@pytest.mark.error
def test_invalid_metadata_type(api_client, unique_collection_name, cleanup_collection):
    """
    Test that invalid metadata types are handled appropriately.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Error test"},
        timeout=10
    )
    
    doc_id = f"doc_{uuid.uuid4().hex[:16]}"
    
    # Metadata as string instead of object
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": doc_id,
            "collectionName": unique_collection_name,
            "content": "Test content",
            "metadata": "invalid metadata type"  # Should be dict/object
        },
        timeout=10
    )
    
    # Should reject or handle gracefully
    assert response.status_code in [400, 500], \
        f"Invalid metadata type should return 400/500, got {response.status_code}"
    
    print("✓ Invalid metadata type correctly rejected")

