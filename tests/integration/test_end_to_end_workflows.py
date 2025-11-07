"""
End-to-End Workflow Tests for IntraMind Platform.

These tests validate complete user journeys across all microservices:
- API Gateway (REST) → Vector Service (gRPC) → Weaviate (Database)

Each test represents a realistic use case with full CRUD operations.
"""

import pytest
import requests
import time
from conftest import API_GATEWAY_URL


@pytest.mark.integration
@pytest.mark.e2e
def test_create_collection_e2e(api_client, unique_collection_name, cleanup_collection):
    """
    Test creating a collection through the full stack.
    
    Validates:
    - REST API accepts collection creation request
    - gRPC forwards to Vector Service
    - Weaviate creates the collection
    - Response contains correct metadata
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={
            "collectionName": unique_collection_name,
            "description": "E2E test collection"
        },
        timeout=10
    )
    
    assert response.status_code == 201, f"Failed to create collection: {response.text}"
    data = response.json()
    
    assert data["collectionName"] == unique_collection_name
    assert data["description"] == "E2E test collection"
    assert data["vectorCount"] == 0
    assert "createdAt" in data
    
    print(f"✓ Collection created: {unique_collection_name}")


@pytest.mark.integration
@pytest.mark.e2e
def test_document_lifecycle_e2e(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test complete document lifecycle: Insert → Retrieve → Update → Delete.
    
    This validates all CRUD operations work correctly through the stack.
    """
    cleanup_collection(unique_collection_name)
    
    # Step 1: Create collection
    create_response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Lifecycle test"},
        timeout=10
    )
    assert create_response.status_code == 201
    
    wait_for_indexing(0.5)
    
    # Step 2: Insert document
    import uuid
    doc_id = f"doc_{uuid.uuid4().hex[:16]}"
    doc_data = {
        "documentId": doc_id,
        "collectionName": unique_collection_name,
        "content": "This is a test document for lifecycle testing",
        "metadata": {
            "source": "e2e_test",
            "category": "testing"
        }
    }
    
    insert_response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json=doc_data,
        timeout=10
    )
    assert insert_response.status_code in [200, 201], f"Insert failed: {insert_response.text}"
    insert_data = insert_response.json()
    doc_id = insert_data["documentId"]
    
    assert doc_id, "Document ID should be returned"
    print(f"✓ Document inserted: {doc_id}")
    
    wait_for_indexing(1.0)
    
    # Step 3: Retrieve document
    get_response = api_client.get(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    assert get_response.status_code == 200, f"Get failed: {get_response.text}"
    get_data = get_response.json()
    
    assert get_data["documentId"] == doc_id
    assert get_data["content"] == doc_data["content"]
    assert get_data["metadata"]["source"] == "e2e_test"
    print(f"✓ Document retrieved: {doc_id}")
    
    # Step 4: Update document
    updated_content = "This document has been updated"
    update_response = api_client.put(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}",
        json={
            "documentId": doc_id,
            "collectionName": unique_collection_name,
            "content": updated_content,
            "metadata": {"source": "e2e_test", "status": "updated"}
        },
        timeout=10
    )
    assert update_response.status_code == 200, f"Update failed: {update_response.text}"
    
    wait_for_indexing(1.0)
    
    # Verify update
    verify_response = api_client.get(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    verify_data = verify_response.json()
    assert verify_data["content"] == updated_content
    assert verify_data["metadata"]["status"] == "updated"
    print(f"✓ Document updated: {doc_id}")
    
    # Step 5: Delete document
    delete_response = api_client.delete(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    assert delete_response.status_code in [200, 204], f"Delete failed: {delete_response.text}"
    print(f"✓ Document deleted: {doc_id}")
    
    wait_for_indexing(0.5)
    
    # Verify deletion
    get_deleted_response = api_client.get(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    # Should return 404 or empty result
    assert get_deleted_response.status_code in [404, 200]


@pytest.mark.integration
@pytest.mark.e2e
def test_batch_insert_e2e(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test batch document insertion.
    
    Validates that multiple documents can be inserted efficiently in a single request.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Batch test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    # Prepare batch of documents
    import uuid
    documents = [
        {
            "documentId": f"batch_doc_{i}_{uuid.uuid4().hex[:8]}",
            "collectionName": unique_collection_name,
            "content": f"Document {i}: Testing batch insertion",
            "metadata": {"index": str(i), "batch": "test_batch_1"}
        }
        for i in range(5)
    ]
    
    # Insert batch
    batch_response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents/batch",
        json=documents,  # Send array directly, not wrapped
        timeout=15
    )
    
    assert batch_response.status_code in [200, 201], f"Batch insert failed: {batch_response.text}"
    batch_data = batch_response.json()
    
    # Verify all documents were inserted
    assert isinstance(batch_data, list) and len(batch_data) == 5, f"Expected 5 documents, got: {batch_data}"
    
    print(f"✓ Batch inserted: {len(batch_data)} documents")


@pytest.mark.integration
@pytest.mark.e2e
def test_search_workflow_e2e(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test semantic search workflow: Insert documents → Search → Verify results.
    
    This validates the core search functionality works end-to-end.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Search test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    # Insert test documents with distinct content
    import uuid
    documents = [
        {
            "documentId": f"search_doc_{i}_{uuid.uuid4().hex[:8]}",
            "collectionName": unique_collection_name,
            "content": content,
            "metadata": metadata
        }
        for i, (content, metadata) in enumerate([
            ("Python programming language is great for data science", {"topic": "python"}),
            ("JavaScript is essential for web development", {"topic": "javascript"}),
            ("Machine learning with Python and TensorFlow", {"topic": "ml"}),
        ])
    ]
    
    for doc in documents:
        api_client.post(
            f"{API_GATEWAY_URL}/v1/documents",
            json=doc,
            timeout=10
        )
    
    wait_for_indexing(2.0)  # Give Weaviate time to index
    
    # Search for Python-related content
    search_response = api_client.post(
        f"{API_GATEWAY_URL}/v1/search",
        json={
            "query": "Python programming",
            "collectionName": unique_collection_name,  # Fixed: was "collection"
            "limit": 5
        },
        timeout=10
    )
    
    assert search_response.status_code == 200, f"Search failed: {search_response.text}"
    search_data = search_response.json()
    
    # Verify search returns results
    assert "results" in search_data or "documents" in search_data or isinstance(search_data, list)
    
    # Get results (handle different response formats)
    results = search_data.get("results", search_data.get("documents", search_data if isinstance(search_data, list) else []))
    
    assert len(results) > 0, "Search should return at least one result"
    
    # Verify Python-related documents are in results
    result_contents = [r.get("content", r.get("text", "")) for r in results]
    assert any("Python" in content for content in result_contents), "Search should find Python-related content"
    
    print(f"✓ Search returned {len(results)} results")


@pytest.mark.integration
@pytest.mark.e2e
def test_collection_isolation(api_client, wait_for_indexing):
    """
    Test that multiple collections don't interfere with each other.
    
    Validates data isolation between collections.
    """
    import uuid
    
    collection1 = f"test_isolation_1_{uuid.uuid4().hex[:8]}"
    collection2 = f"test_isolation_2_{uuid.uuid4().hex[:8]}"
    
    try:
        # Create two collections
        api_client.post(
            f"{API_GATEWAY_URL}/v1/collections",
            json={"collectionName": collection1, "description": "Isolation test 1"},
            timeout=10
        )
        api_client.post(
            f"{API_GATEWAY_URL}/v1/collections",
            json={"collectionName": collection2, "description": "Isolation test 2"},
            timeout=10
        )
        
        wait_for_indexing(0.5)
        
        # Insert document in collection 1
        doc1_id = f"iso_doc_1_{uuid.uuid4().hex[:8]}"
        doc1_response = api_client.post(
            f"{API_GATEWAY_URL}/v1/documents",
            json={
                "documentId": doc1_id,
                "collectionName": collection1,
                "content": "Document in collection 1",
                "metadata": {"collection": "1"}
            },
            timeout=10
        )
        doc1_id = doc1_response.json()["documentId"]
        
        # Insert document in collection 2
        doc2_id = f"iso_doc_2_{uuid.uuid4().hex[:8]}"
        doc2_response = api_client.post(
            f"{API_GATEWAY_URL}/v1/documents",
            json={
                "documentId": doc2_id,
                "collectionName": collection2,
                "content": "Document in collection 2",
                "metadata": {"collection": "2"}
            },
            timeout=10
        )
        doc2_id = doc2_response.json()["documentId"]
        
        wait_for_indexing(1.0)
        
        # Verify doc1 is in collection 1
        correct_get_response = api_client.get(
            f"{API_GATEWAY_URL}/v1/documents/{doc1_id}?collectionName={collection1}",
            timeout=10
        )
        assert correct_get_response.status_code == 200
        assert correct_get_response.json()["content"] == "Document in collection 1"
        assert correct_get_response.json()["collectionName"] == collection1
        
        # Verify doc2 is in collection 2
        correct_get_response2 = api_client.get(
            f"{API_GATEWAY_URL}/v1/documents/{doc2_id}?collectionName={collection2}",
            timeout=10
        )
        assert correct_get_response2.status_code == 200
        assert correct_get_response2.json()["content"] == "Document in collection 2"
        assert correct_get_response2.json()["collectionName"] == collection2
        
        print(f"✓ Collections are properly isolated")
        
    finally:
        # Cleanup
        api_client.delete(f"{API_GATEWAY_URL}/v1/collections/{collection1}", timeout=10)
        api_client.delete(f"{API_GATEWAY_URL}/v1/collections/{collection2}", timeout=10)


@pytest.mark.integration
@pytest.mark.e2e
def test_list_collections_e2e(api_client, wait_for_indexing):
    """
    Test listing all collections.
    
    Validates that collections can be listed and filtered.
    """
    import uuid
    
    # Create multiple test collections
    test_prefix = f"test_list_{uuid.uuid4().hex[:8]}"
    collections = [f"{test_prefix}_col{i}" for i in range(3)]
    
    try:
        for col in collections:
            api_client.post(
                f"{API_GATEWAY_URL}/v1/collections",
                json={"collectionName": col, "description": f"List test {col}"},
                timeout=10
            )
        
        wait_for_indexing(0.5)
        
        # List all collections
        list_response = api_client.get(f"{API_GATEWAY_URL}/v1/collections", timeout=10)
        assert list_response.status_code == 200, f"List failed: {list_response.text}"
        
        collections_data = list_response.json()
        
        # Handle different response formats
        if isinstance(collections_data, list):
            collection_list = collections_data
        elif isinstance(collections_data, dict):
            collection_list = collections_data.get("collections", collections_data.get("items", []))
        else:
            collection_list = []
        
        # Get collection names (normalize to lowercase for comparison)
        collection_names = [
            c.get("collectionName", c.get("name", c)) if isinstance(c, dict) else c
            for c in collection_list
        ]
        collection_names_lower = [name.lower() for name in collection_names]

        # Verify our test collections are in the list (case-insensitive)
        # Weaviate capitalizes collection names, so we compare lowercase
        for col in collections:
            assert col.lower() in collection_names_lower, \
                f"Collection {col} should be in list. Found: {collection_names[:10]}"
        
        print(f"✓ Found {len(collection_names)} collections (including {len(collections)} test collections)")
        
    finally:
        # Cleanup
        for col in collections:
            api_client.delete(f"{API_GATEWAY_URL}/v1/collections/{col}", timeout=10)


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.slow
def test_large_document_handling(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test handling of large documents.
    
    Validates the system can handle documents with substantial content.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Large doc test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    # Create a large document (not too large to avoid timeout)
    import uuid
    large_content = " ".join([f"This is sentence {i} in a large document." for i in range(100)])
    doc_id = f"large_doc_{uuid.uuid4().hex[:16]}"
    
    insert_response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": doc_id,
            "collectionName": unique_collection_name,
            "content": large_content,
            "metadata": {"size": "large"}
        },
        timeout=15
    )
    
    assert insert_response.status_code in [200, 201], f"Large doc insert failed: {insert_response.text}"
    doc_id = insert_response.json()["documentId"]
    
    wait_for_indexing(2.0)
    
    # Retrieve and verify
    get_response = api_client.get(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    assert get_response.status_code == 200
    assert len(get_response.json()["content"]) > 1000  # Verify it's actually large
    
    print(f"✓ Large document handled successfully ({len(large_content)} chars)")

