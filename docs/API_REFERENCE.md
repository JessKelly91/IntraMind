# IntraMind API Reference

> Complete API reference for all IntraMind services

**Version**: 1.0.0
**Last Updated**: November 6, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [API Gateway (REST API)](#api-gateway-rest-api)
3. [Vector Service (gRPC API)](#vector-service-grpc-api)
4. [Weaviate Database API](#weaviate-database-api)
5. [AI Agent Programmatic Interface](#ai-agent-programmatic-interface)
6. [Authentication](#authentication)
7. [Rate Limiting](#rate-limiting)
8. [Error Codes](#error-codes)

---

## Overview

### Service Architecture

```
┌─────────────────┐
│   AI Agent API  │  Python API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Gateway    │  REST API (Port 5000)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Service  │  gRPC API (Port 50052)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Weaviate DB    │  REST API (Port 8080)
└─────────────────┘
```

### Base URLs

| Service | Environment | Base URL |
|---------|------------|----------|
| API Gateway | Development | http://localhost:5000 |
| API Gateway | Production | https://api.intramind.company.com |
| Weaviate | Development | http://localhost:8080 |
| Vector Service | Development | http://localhost:50052 (gRPC) |

---

## API Gateway (REST API)

### Authentication

Currently configured for anonymous access in development. Production deployment should implement:
- API Key authentication
- OAuth 2.0
- JWT tokens

### Common Headers

```http
Content-Type: application/json
Accept: application/json
```

---

### Collections API

#### List Collections

Retrieve all available document collections.

**Request:**
```http
GET /v1/collections HTTP/1.1
Host: localhost:5000
```

**Response:**
```json
{
  "collections": [
    {
      "name": "company_policies",
      "vectorCount": 1250,
      "description": "Company policy documents"
    },
    {
      "name": "technical_docs",
      "vectorCount": 3420,
      "description": "Technical documentation"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Server error

---

#### Get Collection Details

Retrieve details about a specific collection.

**Request:**
```http
GET /v1/collections/{collectionName} HTTP/1.1
Host: localhost:5000
```

**Path Parameters:**
- `collectionName` (string, required): Name of the collection

**Example:**
```http
GET /v1/collections/company_policies
```

**Response:**
```json
{
  "name": "company_policies",
  "vectorCount": 1250,
  "description": "Company policy documents",
  "vectorDimension": 1536,
  "created": "2025-10-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Collection doesn't exist
- `500 Internal Server Error`: Server error

---

#### Create Collection

Create a new document collection.

**Request:**
```http
POST /v1/collections HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "collectionName": "hr_policies",
  "description": "Human Resources policy documents"
}
```

**Request Body Schema:**
```json
{
  "collectionName": "string (required, 1-100 chars)",
  "description": "string (optional, max 500 chars)"
}
```

**Response:**
```json
{
  "success": true,
  "collectionName": "hr_policies",
  "message": "Collection created successfully"
}
```

**Status Codes:**
- `201 Created`: Collection created successfully
- `400 Bad Request`: Invalid request (validation errors)
- `409 Conflict`: Collection already exists
- `500 Internal Server Error`: Server error

---

#### Delete Collection

Delete a collection and all its documents.

**Request:**
```http
DELETE /v1/collections/{collectionName} HTTP/1.1
Host: localhost:5000
```

**Path Parameters:**
- `collectionName` (string, required): Name of the collection to delete

**Response:**
```json
{
  "success": true,
  "message": "Collection deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Collection deleted
- `404 Not Found`: Collection doesn't exist
- `500 Internal Server Error`: Server error

---

### Documents API

#### Insert Document

Insert a single document into a collection.

**Request:**
```http
POST /v1/documents HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "collectionName": "company_policies",
  "id": "policy_001",
  "content": "Remote work policy: Employees may work remotely up to 3 days per week...",
  "metadata": {
    "document_type": "policy",
    "title": "Remote Work Policy 2025",
    "department": "Human Resources",
    "status": "published",
    "created_date": "2025-10-24T10:00:00Z",
    "author": "hr-team@company.com"
  }
}
```

**Request Body Schema:**
```json
{
  "collectionName": "string (required)",
  "id": "string (required, unique within collection)",
  "content": "string (required, max 100KB)",
  "metadata": {
    "document_type": "string (optional)",
    "title": "string (optional)",
    "department": "string (optional)",
    "status": "string (optional)",
    "...": "custom fields"
  }
}
```

**Response:**
```json
{
  "success": true,
  "documentId": "policy_001",
  "message": "Document inserted successfully"
}
```

**Status Codes:**
- `201 Created`: Document inserted
- `400 Bad Request`: Validation errors
- `404 Not Found`: Collection doesn't exist
- `409 Conflict`: Document ID already exists
- `500 Internal Server Error`: Server error

---

#### Batch Insert Documents

Insert multiple documents in a single request (up to 100 documents).

**Request:**
```http
POST /v1/documents/batch HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "collectionName": "company_policies",
  "documents": [
    {
      "id": "policy_001",
      "content": "Document content 1...",
      "metadata": { "title": "Policy 1" }
    },
    {
      "id": "policy_002",
      "content": "Document content 2...",
      "metadata": { "title": "Policy 2" }
    }
  ]
}
```

**Request Body Schema:**
```json
{
  "collectionName": "string (required)",
  "documents": [
    {
      "id": "string (required)",
      "content": "string (required)",
      "metadata": "object (optional)"
    }
  ] // max 100 documents
}
```

**Response:**
```json
{
  "success": true,
  "insertedCount": 2,
  "failedCount": 0,
  "message": "Batch insert completed"
}
```

**Status Codes:**
- `201 Created`: All documents inserted
- `207 Multi-Status`: Partial success (some documents failed)
- `400 Bad Request`: Validation errors
- `404 Not Found`: Collection doesn't exist
- `500 Internal Server Error`: Server error

---

#### Get Document

Retrieve a document by ID.

**Request:**
```http
GET /v1/documents/{documentId}?collectionName={collectionName} HTTP/1.1
Host: localhost:5000
```

**Query Parameters:**
- `collectionName` (string, required): Name of the collection

**Path Parameters:**
- `documentId` (string, required): Document ID

**Example:**
```http
GET /v1/documents/policy_001?collectionName=company_policies
```

**Response:**
```json
{
  "id": "policy_001",
  "content": "Remote work policy: Employees may work remotely...",
  "metadata": {
    "document_type": "policy",
    "title": "Remote Work Policy 2025",
    "department": "Human Resources",
    "status": "published"
  },
  "created": "2025-10-24T10:00:00Z",
  "updated": "2025-10-24T15:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Document retrieved
- `404 Not Found`: Document or collection doesn't exist
- `500 Internal Server Error`: Server error

---

#### Update Document

Update an existing document.

**Request:**
```http
PUT /v1/documents/{documentId} HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "collectionName": "company_policies",
  "content": "Updated content...",
  "metadata": {
    "document_type": "policy",
    "status": "published",
    "updated_date": "2025-11-01T10:00:00Z",
    "version": "1.1.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "documentId": "policy_001",
  "message": "Document updated successfully"
}
```

**Status Codes:**
- `200 OK`: Document updated
- `404 Not Found`: Document or collection doesn't exist
- `400 Bad Request`: Validation errors
- `500 Internal Server Error`: Server error

---

#### Delete Document

Delete a document by ID.

**Request:**
```http
DELETE /v1/documents/{documentId}?collectionName={collectionName} HTTP/1.1
Host: localhost:5000
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Document deleted
- `404 Not Found`: Document or collection doesn't exist
- `500 Internal Server Error`: Server error

---

### Search API

#### Semantic Search

Perform semantic search across one or more collections.

**Request (Single Collection):**
```http
POST /v1/search HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "collectionName": "company_policies",
  "query": "What is the remote work policy?",
  "limit": 5,
  "minScore": 0.7
}
```

**Request (Multiple Collections):**
```http
POST /v1/search HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "collectionNames": ["hr_policies", "it_policies", "security_policies"],
  "query": "What is the password policy?",
  "limit": 10,
  "minScore": 0.6,
  "metadataFilters": {
    "status": "published",
    "document_type": "policy"
  }
}
```

**Request Body Schema:**
```json
{
  "collectionName": "string (optional, required if collectionNames not provided)",
  "collectionNames": ["string"] // optional, max 10 collections, required if collectionName not provided
  "query": "string (required, 1-1000 chars)",
  "limit": 10, // optional, 1-100, default 10
  "minScore": 0.0, // optional, 0.0-1.0, default 0.0
  "metadataFilters": {
    "key": "value"  // optional, exact match filters
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "documentId": "policy_001",
      "content": "Remote work policy: Employees may work remotely up to 3 days per week with manager approval.",
      "score": 0.89,
      "collectionName": "hr_policies",
      "metadata": {
        "document_type": "policy",
        "title": "Remote Work Policy 2025",
        "department": "Human Resources",
        "status": "published"
      }
    },
    {
      "documentId": "policy_015",
      "content": "Flexible work arrangements include remote work options...",
      "score": 0.82,
      "collectionName": "hr_policies",
      "metadata": {
        "document_type": "policy",
        "title": "Flexible Work Arrangements",
        "department": "Human Resources"
      }
    }
  ],
  "totalCount": 2,
  "executionTimeMs": 150,
  "searchedCollections": ["hr_policies"],
  "partialResults": false,
  "warnings": []
}
```

**Response Fields:**
- `results`: Array of matching documents
  - `documentId`: Document identifier
  - `content`: Document text content
  - `score`: Similarity score (0.0-1.0, higher is better)
  - `collectionName`: Source collection
  - `metadata`: Document metadata
- `totalCount`: Total number of results found
- `executionTimeMs`: Query execution time in milliseconds
- `searchedCollections`: Collections successfully searched
- `partialResults`: True if some collections failed
- `warnings`: Array of warnings (e.g., collection not found)

**Status Codes:**
- `200 OK`: Search completed (may have partial results)
- `400 Bad Request`: Validation errors
- `404 Not Found`: Collection not found (single-collection search only)
- `500 Internal Server Error`: Server error

**Score Interpretation:**
- `1.0`: Perfect match
- `0.8-1.0`: Highly relevant
- `0.6-0.8`: Moderately relevant
- `0.4-0.6`: Somewhat relevant
- `< 0.4`: Low relevance

---

### Health API

#### Health Check

Check overall service health.

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:5000
```

**Response:**
```json
{
  "status": "Healthy",
  "checks": {
    "vectorService": "Healthy",
    "database": "Healthy"
  },
  "timestamp": "2025-11-06T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Service healthy
- `503 Service Unavailable`: Service unhealthy

---

#### Liveness Probe

Kubernetes liveness probe endpoint.

**Request:**
```http
GET /health/liveness HTTP/1.1
Host: localhost:5000
```

**Response:**
```
HTTP/1.1 200 OK
```

**Status Codes:**
- `200 OK`: Service alive
- `503 Service Unavailable`: Service should be restarted

---

#### Readiness Probe

Kubernetes readiness probe endpoint (checks dependencies).

**Request:**
```http
GET /health/readiness HTTP/1.1
Host: localhost:5000
```

**Response:**
```
HTTP/1.1 200 OK
```

**Status Codes:**
- `200 OK`: Service ready to accept traffic
- `503 Service Unavailable`: Service not ready (dependencies unavailable)

---

## Vector Service (gRPC API)

### Overview

The Vector Service provides low-level gRPC operations for vector database management. Most users should use the REST API Gateway instead.

**Proto Definition**: `vector-db-service/src/service/protos/vector_service.proto`

### Service Definition

```protobuf
service VectorDBService {
  // Collection Management
  rpc CreateCollection(CreateCollectionRequest) returns (CreateCollectionResponse);
  rpc DeleteCollection(DeleteCollectionRequest) returns (DeleteCollectionResponse);
  rpc ListCollections(ListCollectionsRequest) returns (ListCollectionsResponse);
  rpc GetCollection(GetCollectionRequest) returns (GetCollectionResponse);

  // Document Operations
  rpc InsertVector(InsertVectorRequest) returns (InsertVectorResponse);
  rpc InsertVectorBatch(InsertVectorBatchRequest) returns (InsertVectorBatchResponse);
  rpc GetVector(GetVectorRequest) returns (GetVectorResponse);
  rpc UpdateVector(UpdateVectorRequest) returns (UpdateVectorResponse);
  rpc DeleteVector(DeleteVectorRequest) returns (DeleteVectorResponse);

  // Search Operations
  rpc SemanticSearch(SemanticSearchRequest) returns (SemanticSearchResponse);
  rpc StreamSearch(SemanticSearchRequest) returns (stream SearchResult);

  // Health Check
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}
```

### Example Usage (Python)

```python
import grpc
from protos import vector_service_pb2
from protos import vector_service_pb2_grpc

# Create channel
channel = grpc.insecure_channel('localhost:50052')
stub = vector_service_pb2_grpc.VectorDBServiceStub(channel)

# Create collection
response = stub.CreateCollection(
    vector_service_pb2.CreateCollectionRequest(
        collection_name="test_collection",
        description="Test collection"
    )
)
print(f"Created: {response.success}")

# Insert document
response = stub.InsertVector(
    vector_service_pb2.InsertVectorRequest(
        collection_name="test_collection",
        document_id="doc_001",
        content="Document content",
        metadata={"title": "Test Doc"}
    )
)

# Search
response = stub.SemanticSearch(
    vector_service_pb2.SemanticSearchRequest(
        collection_name="test_collection",
        query="test query",
        limit=5
    )
)

for result in response.results:
    print(f"Score: {result.score}, Content: {result.content}")
```

### Example Usage (.NET)

```csharp
using Grpc.Net.Client;
using VectorDB.Contracts;

// Create channel
var channel = GrpcChannel.ForAddress("http://localhost:50052");
var client = new VectorDBService.VectorDBServiceClient(channel);

// Create collection
var createResponse = await client.CreateCollectionAsync(
    new CreateCollectionRequest
    {
        CollectionName = "test_collection",
        Description = "Test collection"
    }
);

// Insert document
var insertResponse = await client.InsertVectorAsync(
    new InsertVectorRequest
    {
        CollectionName = "test_collection",
        DocumentId = "doc_001",
        Content = "Document content",
        Metadata = { { "title", "Test Doc" } }
    }
);

// Search
var searchResponse = await client.SemanticSearchAsync(
    new SemanticSearchRequest
    {
        CollectionName = "test_collection",
        Query = "test query",
        Limit = 5
    }
);

foreach (var result in searchResponse.Results)
{
    Console.WriteLine($"Score: {result.Score}, Content: {result.Content}");
}
```

---

## Weaviate Database API

### Overview

Weaviate provides a native REST API. The Vector Service and API Gateway abstract this, but direct access is available if needed.

**Base URL**: http://localhost:8080

**Documentation**: https://weaviate.io/developers/weaviate/api/rest

### Common Operations

#### Health Check

```http
GET /v1/.well-known/ready HTTP/1.1
Host: localhost:8080
```

#### List Schemas

```http
GET /v1/schema HTTP/1.1
Host: localhost:8080
```

#### Query Data (GraphQL)

```http
POST /v1/graphql HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "query": "{
    Get {
      CompanyPolicies(limit: 5) {
        content
        _additional {
          id
          certainty
        }
      }
    }
  }"
}
```

---

## AI Agent Programmatic Interface

### Overview

The AI Agent can be used programmatically in Python applications.

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from agent import IntraMindAgent

async def main():
    agent = IntraMindAgent()

    # Perform search
    result = await agent.search(
        query="What is the remote work policy?",
        collection_name="company_policies",
        num_results=5
    )

    if result["success"]:
        print(f"Response: {result['response']}")
        print(f"Citations: {result['citations']}")
        print(f"Query Complexity: {result['complexity']}")
    else:
        print(f"Error: {result['error']}")

asyncio.run(main())
```

### API Methods

#### search()

Perform intelligent semantic search with query classification and result synthesis.

**Signature:**
```python
async def search(
    query: str,
    collection_name: str = "intramind_documents",
    num_results: int = 10,
    min_score: float = 0.0
) -> dict
```

**Parameters:**
- `query` (str): Natural language search query
- `collection_name` (str): Target collection name
- `num_results` (int): Maximum number of results
- `min_score` (float): Minimum similarity score (0.0-1.0)

**Returns:**
```python
{
    "success": True,
    "response": "AI-generated answer with context",
    "citations": ["doc_id_1", "doc_id_2"],
    "complexity": "simple",  # or "complex"
    "search_results": [
        {
            "document_id": "doc_001",
            "content": "...",
            "score": 0.89,
            "metadata": {...}
        }
    ]
}
```

#### stream_search()

Stream search results as they're generated.

**Signature:**
```python
async def stream_search(
    query: str,
    collection_name: str = "intramind_documents",
    num_results: int = 10
) -> AsyncIterator[dict]
```

**Yields:**
```python
{
    "step": "classify_query",
    "current_step": "classify_query",
    "query_complexity": "simple",
    "response": None,
    "complete": False
}
```

**Example:**
```python
async for update in agent.stream_search("What is the policy?"):
    print(f"Step: {update['step']}")
    if update.get('response'):
        print(f"Response: {update['response']}")
```

#### ingest_document()

Ingest a document from file (supports PDF, DOCX, PPTX, TXT, MD, images).

**Signature:**
```python
async def ingest_document(
    file_path: str,
    collection_name: str = "intramind_documents",
    metadata: dict = None
) -> dict
```

**Parameters:**
- `file_path` (str): Path to document file
- `collection_name` (str): Target collection
- `metadata` (dict): Optional document metadata

**Returns:**
```python
{
    "success": True,
    "document_id": "doc_abc123",
    "chunks_stored": 5,
    "message": "Document ingested successfully"
}
```

---

## Authentication

### Current State (Development)

All services currently use **anonymous access** for local development.

### Production Recommendations

#### API Gateway Authentication

**Option 1: API Key Authentication**

```http
GET /v1/collections HTTP/1.1
Host: api.intramind.company.com
X-API-Key: your-api-key-here
```

**Option 2: Bearer Token (OAuth 2.0/JWT)**

```http
GET /v1/collections HTTP/1.1
Host: api.intramind.company.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Weaviate Authentication

Configure in `docker-compose.yml`:

```yaml
weaviate:
  environment:
    AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
    AUTHENTICATION_APIKEY_ENABLED: 'true'
    AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'your-secure-key'
```

---

## Rate Limiting

### Recommended Rate Limits (Production)

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| Search API | 100 requests | per minute |
| Insert Document | 50 requests | per minute |
| Batch Insert | 10 requests | per minute |
| Collections API | 20 requests | per minute |

### Implementation

Use API Gateway middleware (e.g., AspNetCoreRateLimit):

```csharp
services.AddRateLimiter(options => {
    options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: context.User.Identity?.Name ?? context.Request.Headers.Host.ToString(),
            factory: partition => new FixedWindowRateLimiterOptions
            {
                AutoReplenishment = true,
                PermitLimit = 100,
                Window = TimeSpan.FromMinutes(1)
            }));
});
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| `200 OK` | Success | Successful GET, PUT, DELETE |
| `201 Created` | Resource created | Successful POST (create) |
| `207 Multi-Status` | Partial success | Batch operations with some failures |
| `400 Bad Request` | Invalid request | Validation errors, malformed JSON |
| `401 Unauthorized` | Authentication required | Missing or invalid credentials |
| `403 Forbidden` | Access denied | Insufficient permissions |
| `404 Not Found` | Resource not found | Collection or document doesn't exist |
| `409 Conflict` | Resource conflict | Duplicate ID, collection already exists |
| `429 Too Many Requests` | Rate limit exceeded | Too many requests in time window |
| `500 Internal Server Error` | Server error | Unexpected server failure |
| `503 Service Unavailable` | Service unavailable | Dependency failure, service down |

### Error Response Format

```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "Query": ["The Query field is required."],
    "Limit": ["The field Limit must be between 1 and 100."]
  },
  "traceId": "00-abc123def456-789-00"
}
```

### gRPC Status Codes

| Code | Description |
|------|-------------|
| `0 (OK)` | Success |
| `3 (INVALID_ARGUMENT)` | Invalid request parameters |
| `5 (NOT_FOUND)` | Collection or document not found |
| `6 (ALREADY_EXISTS)` | Resource already exists |
| `13 (INTERNAL)` | Internal server error |
| `14 (UNAVAILABLE)` | Service unavailable |

---

## Additional Resources

- **Swagger UI**: http://localhost:5000/swagger (interactive API documentation)
- **API Usage Guide**: [api-gateway/docs/api-usage-guide.md](../api-gateway/docs/api-usage-guide.md)
- **Metadata Schema**: [api-gateway/docs/metadata-schema.md](../api-gateway/docs/metadata-schema.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **User Guide**: [USER_GUIDE.md](./USER_GUIDE.md)

---

**Last Updated**: November 6, 2025
**Maintained By**: IntraMind Development Team
