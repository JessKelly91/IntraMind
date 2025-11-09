"""
Performance & Load Tests for IntraMind Platform.

These tests validate that the system performs well under various conditions:
- Response time benchmarks
- Concurrent request handling
- Batch operation performance
- Search performance

Note: These tests use pytest-benchmark for performance measurements.
"""

import pytest
import requests
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import API_GATEWAY_URL, VECTORIZER_ENABLED


@pytest.mark.integration
@pytest.mark.performance
def test_collection_creation_performance(api_client, benchmark, cleanup_collection):
    """
    Benchmark collection creation performance.
    
    Validates that collections can be created quickly.
    """
    def create_collection():
        collection_name = f"perf_test_{uuid.uuid4().hex[:8]}"
        cleanup_collection(collection_name)
        
        response = api_client.post(
            f"{API_GATEWAY_URL}/v1/collections",
            json={"collectionName": collection_name, "description": "Performance test"},
            timeout=10
        )
        assert response.status_code == 201
        return collection_name
    
    result = benchmark(create_collection)
    print(f"✓ Collection creation performance: {benchmark.stats.get('mean', 0):.4f}s average")


@pytest.mark.integration
@pytest.mark.performance
def test_document_insert_performance(api_client, benchmark, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Benchmark single document insert performance.
    
    Validates that documents can be inserted quickly.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection first
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Performance test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    def insert_document():
        doc_id = f"perf_doc_{uuid.uuid4().hex[:16]}"
        response = api_client.post(
            f"{API_GATEWAY_URL}/v1/documents",
            json={
                "documentId": doc_id,
                "collectionName": unique_collection_name,
                "content": "Performance test document with some content",
                "metadata": {"test": "performance", "index": "1"}
            },
            timeout=10
        )
        assert response.status_code in [200, 201]
        return doc_id
    
    result = benchmark(insert_document)
    print(f"✓ Document insert performance: {benchmark.stats.get('mean', 0):.4f}s average")


@pytest.mark.integration
@pytest.mark.performance
def test_document_retrieval_performance(api_client, benchmark, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Benchmark document retrieval performance.
    
    Validates that documents can be retrieved quickly.
    """
    cleanup_collection(unique_collection_name)
    
    # Setup: Create collection and insert a document
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Performance test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    doc_id_input = f"perf_doc_{uuid.uuid4().hex[:16]}"
    insert_response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": doc_id_input,
            "collectionName": unique_collection_name,
            "content": "Performance test document",
            "metadata": {}
        },
        timeout=10
    )
    # Use the actual document ID returned from the insert
    doc_id = insert_response.json()["documentId"]
    
    wait_for_indexing(1.0)
    
    def retrieve_document():
        response = api_client.get(
            f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
            timeout=10
        )
        assert response.status_code == 200
        return response.json()
    
    result = benchmark(retrieve_document)
    print(f"✓ Document retrieval performance: {benchmark.stats.get('mean', 0):.4f}s average")


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.slow
def test_batch_insert_performance(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test batch insert performance with various batch sizes.
    
    Validates that batch operations scale well.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Batch performance test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    batch_sizes = [10, 25, 50]
    
    for batch_size in batch_sizes:
        documents = [
            {
                "documentId": f"batch_doc_{i}_{uuid.uuid4().hex[:8]}",
                "collectionName": unique_collection_name,
                "content": f"Batch document {i} with some test content",
                "metadata": {"batch": "test", "index": str(i)}
            }
            for i in range(batch_size)
        ]
        
        start_time = time.time()
        response = api_client.post(
            f"{API_GATEWAY_URL}/v1/documents/batch",
            json=documents,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        assert response.status_code in [200, 201], f"Batch insert failed: {response.text}"
        
        docs_per_second = batch_size / elapsed if elapsed > 0 else 0
        print(f"✓ Batch size {batch_size}: {elapsed:.3f}s ({docs_per_second:.1f} docs/sec)")
    
    print(f"✓ Batch insert performance test completed")


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.skipif(not VECTORIZER_ENABLED, reason="Semantic search requires vectorizer")
def test_search_performance(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test search performance with indexed documents.

    Validates that search remains fast as document count grows.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Search performance test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    # Insert multiple documents for search testing
    num_docs = 50
    documents = [
        {
            "documentId": f"search_doc_{i}_{uuid.uuid4().hex[:8]}",
            "collectionName": unique_collection_name,
            "content": f"Document {i}: This is a test document about {'Python' if i % 3 == 0 else 'JavaScript' if i % 3 == 1 else 'TypeScript'} programming",
            "metadata": {"index": str(i), "category": f"cat_{i % 5}"}
        }
        for i in range(num_docs)
    ]
    
    # Insert in batches
    batch_size = 25
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        api_client.post(
            f"{API_GATEWAY_URL}/v1/documents/batch",
            json=batch,
            timeout=30
        )
    
    wait_for_indexing(3.0)  # Give time for indexing
    
    # Test search performance
    search_queries = [
        "Python programming",
        "JavaScript programming",
        "TypeScript programming"
    ]
    
    search_times = []
    for query in search_queries:
        start_time = time.time()
        response = api_client.post(
            f"{API_GATEWAY_URL}/v1/search",
            json={
                "query": query,
                "collectionName": unique_collection_name,
                "limit": 10
            },
            timeout=10
        )
        elapsed = time.time() - start_time
        search_times.append(elapsed)
        
        assert response.status_code == 200, f"Search failed: {response.text}"
        
        print(f"✓ Search '{query}': {elapsed:.3f}s")
    
    avg_search_time = sum(search_times) / len(search_times)
    print(f"✓ Average search time: {avg_search_time:.3f}s across {num_docs} documents")
    
    # Assert reasonable performance (adjust threshold as needed)
    assert avg_search_time < 2.0, f"Search too slow: {avg_search_time:.3f}s average"


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.slow
def test_concurrent_requests(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test concurrent request handling.
    
    Validates that the system can handle multiple simultaneous requests.
    """
    cleanup_collection(unique_collection_name)
    
    # Create collection
    api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Concurrency test"},
        timeout=10
    )
    
    wait_for_indexing(0.5)
    
    def insert_document(index):
        """Insert a single document (thread worker)."""
        doc_id = f"concurrent_doc_{index}_{uuid.uuid4().hex[:8]}"
        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/v1/documents",
                json={
                    "documentId": doc_id,
                    "collectionName": unique_collection_name,
                    "content": f"Concurrent test document {index}",
                    "metadata": {"index": str(index)}
                },
                timeout=10
            )
            return {
                "index": index,
                "status_code": response.status_code,
                "success": response.status_code in [200, 201]
            }
        except Exception as e:
            return {
                "index": index,
                "status_code": None,
                "success": False,
                "error": str(e)
            }
    
    # Test with 10 concurrent requests
    num_concurrent = 10
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(insert_document, i) for i in range(num_concurrent)]
        results = [future.result() for future in as_completed(futures)]
    
    elapsed = time.time() - start_time
    
    # Analyze results
    successful = sum(1 for r in results if r["success"])
    failed = num_concurrent - successful
    
    print(f"✓ Concurrent requests: {successful}/{num_concurrent} succeeded in {elapsed:.3f}s")
    print(f"  - Success rate: {(successful/num_concurrent)*100:.1f}%")
    print(f"  - Throughput: {num_concurrent/elapsed:.1f} requests/sec")
    
    # Assert acceptable success rate (at least 90%)
    assert successful >= num_concurrent * 0.9, \
        f"Too many failures: {failed}/{num_concurrent} failed"


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.slow
def test_list_collections_performance(api_client, wait_for_indexing):
    """
    Test performance of listing collections when many exist.
    
    Note: This test works with existing collections in the system.
    """
    # Just measure the current performance
    start_time = time.time()
    response = api_client.get(f"{API_GATEWAY_URL}/v1/collections", timeout=10)
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    
    collections_data = response.json()
    if isinstance(collections_data, list):
        count = len(collections_data)
    elif isinstance(collections_data, dict):
        count = len(collections_data.get("collections", collections_data.get("items", [])))
    else:
        count = 0
    
    print(f"✓ List {count} collections: {elapsed:.3f}s")
    
    # Assert reasonable performance
    assert elapsed < 5.0, f"Listing collections too slow: {elapsed:.3f}s"


@pytest.mark.integration
@pytest.mark.performance
def test_end_to_end_workflow_performance(api_client, unique_collection_name, cleanup_collection, wait_for_indexing):
    """
    Test complete workflow performance: Create → Insert → Search → Get → Delete.
    
    Validates overall system performance for a typical use case.
    """
    cleanup_collection(unique_collection_name)
    
    workflow_times = {}
    
    # 1. Create collection
    start = time.time()
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/collections",
        json={"collectionName": unique_collection_name, "description": "Workflow test"},
        timeout=10
    )
    assert response.status_code == 201
    workflow_times['create_collection'] = time.time() - start
    
    wait_for_indexing(0.5)
    
    # 2. Insert document
    doc_id_input = f"workflow_doc_{uuid.uuid4().hex[:16]}"
    start = time.time()
    response = api_client.post(
        f"{API_GATEWAY_URL}/v1/documents",
        json={
            "documentId": doc_id_input,
            "collectionName": unique_collection_name,
            "content": "Workflow test document about Python programming",
            "metadata": {"test": "workflow"}
        },
        timeout=10
    )
    assert response.status_code in [200, 201]
    # Use the actual document ID returned from the insert
    doc_id = response.json()["documentId"]
    workflow_times['insert_document'] = time.time() - start
    
    wait_for_indexing(2.0)
    
    # 3. Search (skip in CI when vectorizer is disabled)
    if VECTORIZER_ENABLED:
        start = time.time()
        response = api_client.post(
            f"{API_GATEWAY_URL}/v1/search",
            json={
                "query": "Python programming",
                "collectionName": unique_collection_name,
                "limit": 5
            },
            timeout=10
        )
        assert response.status_code == 200
        workflow_times['search'] = time.time() - start
    else:
        print("  (Skipping search - no vectorizer in CI)")
    
    # 4. Get document
    start = time.time()
    response = api_client.get(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    assert response.status_code == 200
    workflow_times['get_document'] = time.time() - start
    
    # 5. Delete document
    start = time.time()
    response = api_client.delete(
        f"{API_GATEWAY_URL}/v1/documents/{doc_id}?collectionName={unique_collection_name}",
        timeout=10
    )
    assert response.status_code in [200, 204]
    workflow_times['delete_document'] = time.time() - start
    
    # Report results
    total_time = sum(workflow_times.values())
    print(f"\n✓ End-to-End Workflow Performance:")
    for operation, duration in workflow_times.items():
        print(f"  - {operation}: {duration:.3f}s")
    print(f"  - Total: {total_time:.3f}s")
    
    # Assert reasonable total time
    assert total_time < 10.0, f"Workflow too slow: {total_time:.3f}s total"

