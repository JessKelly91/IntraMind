# IntraMind User Guide

> Complete guide to using the IntraMind AI-powered document search platform

**Version**: 1.0.0
**Last Updated**: November 6, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [End-to-End Workflows](#end-to-end-workflows)
5. [Using the AI Agent](#using-the-ai-agent)
6. [Using the API Gateway](#using-the-api-gateway)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is IntraMind?

IntraMind is an AI-powered intelligent search platform designed for enterprise internal documents. It enables **semantic search** - finding documents based on meaning rather than just keywords.

### Key Features

- **Semantic Search**: Natural language queries find relevant documents
- **AI Agent**: Intelligent assistant that understands complex questions
- **Multi-format Support**: PDFs, Word documents, presentations, text files, images
- **Metadata Filtering**: Filter by department, document type, status, and more
- **RESTful API**: Easy integration with existing systems
- **Conversation Memory**: Context-aware multi-turn interactions

### Who Should Use This Guide?

- **End Users**: Learn to search for documents using the AI Agent
- **Developers**: Integrate IntraMind into applications via REST API
- **Administrators**: Manage collections and documents
- **Data Scientists**: Build RAG (Retrieval-Augmented Generation) applications

---

## Getting Started

### Prerequisites

Before using IntraMind, ensure:

1. **Services are Running**: All backend services must be started
2. **Collections Created**: At least one document collection exists
3. **Documents Ingested**: Collection contains searchable documents

### Quick Start Checklist

```bash
# 1. Verify services are running
curl http://localhost:8080/v1/.well-known/ready  # Weaviate
curl http://localhost:5000/health                 # API Gateway

# 2. Check collections exist
curl http://localhost:5000/v1/collections

# 3. Run a test search
cd ai-agent
python -m src.cli.main search "test query"
```

If all checks pass, you're ready to use IntraMind!

---

## Core Concepts

### Collections

**Definition**: A collection is a named group of related documents (like a database table).

**Examples**:
- `company_policies` - HR, IT, and security policies
- `technical_docs` - API documentation, architecture guides
- `meeting_notes` - Team meeting summaries
- `knowledge_base` - FAQs, how-to guides

**When to Create a New Collection**:
- Documents share a common theme or category
- You want to search a specific subset of documents
- Different access controls are needed
- Document lifecycle differs (e.g., policies vs. drafts)

### Documents

**Definition**: A document is a single piece of content with text and optional metadata.

**Document Structure**:
```json
{
  "id": "policy_001",
  "content": "Full text content of the document...",
  "metadata": {
    "title": "Remote Work Policy",
    "document_type": "policy",
    "department": "Human Resources",
    "status": "published",
    "created_date": "2025-10-15T10:00:00Z",
    "author": "hr-team@company.com"
  }
}
```

### Metadata

**Definition**: Structured data about a document (who, what, when, where, why).

**Common Metadata Fields**:
- `title`: Document title
- `document_type`: Category (policy, technical_doc, faq, etc.)
- `department`: Owning team (HR, Engineering, Legal)
- `status`: Lifecycle status (draft, published, archived)
- `author`: Document creator
- `created_date` / `updated_date`: Timestamps
- `tags`: Comma-separated keywords

**Why Metadata Matters**:
- **Filtering**: Search only published HR policies
- **Context**: Show users the document source
- **Organization**: Group and categorize results
- **Access Control**: Implement permission-based filtering

### Semantic Search

**Definition**: Search based on meaning, not just keyword matching.

**Traditional Keyword Search**:
- Query: "remote work"
- Matches: Documents containing exact words "remote" and "work"
- Misses: Documents about "telecommuting" or "work from home"

**Semantic Search** (IntraMind):
- Query: "remote work policy"
- Matches: Documents about remote work, telecommuting, WFH, flexible arrangements
- Understanding: Knows these concepts are related

**How It Works**:
1. Document text converted to vector (embedding)
2. Query converted to vector (embedding)
3. Find documents with similar vectors (semantic similarity)
4. Return ranked results by similarity score

### Similarity Scores

**Range**: 0.0 (completely different) to 1.0 (identical)

**Interpretation**:
- **0.8 - 1.0**: Highly relevant, directly answers query
- **0.6 - 0.8**: Moderately relevant, related content
- **0.4 - 0.6**: Somewhat relevant, tangentially related
- **< 0.4**: Low relevance, weak connection

---

## End-to-End Workflows

### Workflow 1: First-Time Setup

**Goal**: Set up IntraMind and ingest your first documents.

#### Step 1: Start Services

```bash
cd IntraMind

# Start backend services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps
```

#### Step 2: Install and Configure AI Agent

```bash
cd ai-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your API keys
```

#### Step 3: Create Your First Collection

```bash
# Using curl
curl -X POST http://localhost:5000/v1/collections \
  -H "Content-Type: application/json" \
  -d '{
    "collectionName": "company_docs",
    "description": "Company documentation"
  }'

# Or using Python
python
>>> import requests
>>> requests.post("http://localhost:5000/v1/collections", json={
...     "collectionName": "company_docs",
...     "description": "Company documentation"
... })
```

#### Step 4: Ingest Documents

**Option A: Using AI Agent (Recommended for Files)**

```bash
# Single file
python -m src.cli.main ingest \
  --file-path "/path/to/document.pdf" \
  --collection "company_docs"

# Multiple files
for file in /path/to/docs/*.pdf; do
  python -m src.cli.main ingest --file-path "$file" --collection "company_docs"
done
```

**Option B: Using API (Programmatic)**

```python
import requests

response = requests.post(
    "http://localhost:5000/v1/documents",
    json={
        "collectionName": "company_docs",
        "id": "doc_001",
        "content": "Your document text here...",
        "metadata": {
            "title": "Company Policy",
            "document_type": "policy",
            "department": "HR"
        }
    }
)
print(response.json())
```

#### Step 5: Run Your First Search

```bash
# Interactive mode
python -m src.cli.main

# Single query
python -m src.cli.main search "What is the vacation policy?"
```

**Success!** You've set up IntraMind and performed your first semantic search.

---

### Workflow 2: Daily Document Search

**Goal**: Find information quickly using natural language.

#### Using AI Agent CLI (Recommended for End Users)

**Interactive Mode**:

```bash
cd ai-agent
python -m src.cli.main

# You'll see a prompt:
Search: What is the remote work policy?

# AI Agent will:
# 1. Classify your query (simple vs complex)
# 2. Search relevant documents
# 3. Synthesize an answer with citations
# 4. Present results with sources
```

**Example Session**:

```
Search: What are the vacation time requirements?

🔍 Searching company_docs...

✓ Found 3 highly relevant documents

📝 Response:
According to company policy, full-time employees accrue vacation time as follows:
- 0-2 years: 15 days per year
- 3-5 years: 20 days per year
- 5+ years: 25 days per year

Vacation requests must be submitted at least 2 weeks in advance for approval.

📚 Sources:
- HR Policy Manual (2025)
- Employee Benefits Guide
- Time Off Request Procedures

Search: How do I submit a vacation request?

🔍 Searching company_docs...

✓ Using conversation context from previous query

📝 Response:
To submit a vacation request:
1. Log into the HR portal at portal.company.com
2. Navigate to Time Off → New Request
3. Select "Vacation" as request type
4. Choose dates and submit
5. Your manager will be notified for approval

Remember to submit at least 2 weeks in advance as mentioned in the previous policy.

📚 Sources:
- HR Portal User Guide
- Time Off Request Procedures
```

**Single Query Mode**:

```bash
# Quick one-off search
python -m src.cli.main search "What is the remote work policy?" --limit 5

# With collection filter
python -m src.cli.main search "API authentication" \
  --collection "technical_docs" \
  --limit 10

# With minimum score threshold
python -m src.cli.main search "security requirements" \
  --min-score 0.7
```

---

### Workflow 3: Building a RAG Application

**Goal**: Integrate IntraMind into your Python application for context-aware AI responses.

#### Step 1: Install IntraMind Agent

```bash
pip install requests python-dotenv
# Or use the ai-agent package directly
```

#### Step 2: Create RAG Function

```python
# rag_app.py
import asyncio
import requests
from typing import List, Dict

def search_context(query: str, collection: str = "company_docs", limit: int = 5) -> List[Dict]:
    """Retrieve context documents for a user query."""
    response = requests.post(
        "http://localhost:5000/v1/search",
        json={
            "collectionName": collection,
            "query": query,
            "limit": limit,
            "minScore": 0.7  # Only high-quality results
        }
    )

    if response.status_code == 200:
        data = response.json()
        return data["results"]
    else:
        return []

def format_context(results: List[Dict]) -> str:
    """Format search results into context for LLM."""
    if not results:
        return "No relevant context found."

    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(
            f"[Source {i}: {result['metadata'].get('title', 'Unknown')}]\n"
            f"{result['content']}\n"
            f"(Relevance: {result['score']:.2f})\n"
        )

    return "\n---\n\n".join(context_parts)

def generate_rag_response(user_question: str, collection: str = "company_docs") -> str:
    """Generate AI response using retrieved context."""
    # Step 1: Retrieve context
    results = search_context(user_question, collection)

    if not results:
        return "I couldn't find any relevant information to answer your question."

    # Step 2: Format context
    context = format_context(results)

    # Step 3: Create prompt for LLM
    prompt = f"""Based on the following company documents, answer the user's question.

Context:
{context}

Question: {user_question}

Provide a clear, accurate answer based only on the context provided. If the context doesn't contain enough information, say so. Include which source(s) you used.

Answer:"""

    # Step 4: Call your LLM (OpenAI, Anthropic, etc.)
    # This is a placeholder - use your preferred LLM API
    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on company documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# Usage
if __name__ == "__main__":
    question = "What is the company vacation policy?"
    answer = generate_rag_response(question)
    print(answer)
```

#### Step 3: Run Your RAG Application

```bash
python rag_app.py
```

**Expected Output**:
```
Based on the HR Policy Manual (2025), full-time employees accrue vacation time based on tenure:
- 0-2 years: 15 days per year
- 3-5 years: 20 days per year
- 5+ years: 25 days per year

Vacation requests must be submitted at least 2 weeks in advance through the HR portal for manager approval.

Sources: HR Policy Manual (2025), Employee Benefits Guide
```

---

### Workflow 4: Document Management

**Goal**: Add, update, and manage documents in collections.

#### Add a Single Document

```python
import requests

# Insert document
response = requests.post(
    "http://localhost:5000/v1/documents",
    json={
        "collectionName": "company_policies",
        "id": "policy_remote_work_2025",
        "content": """
        Remote Work Policy 2025

        Effective January 1, 2025

        Eligible employees may work remotely up to 3 days per week with prior manager approval.

        Requirements:
        - Reliable internet connection
        - Dedicated workspace
        - Available during core hours (10am-3pm)
        - Regular in-office presence for team collaboration

        To request remote work arrangements, submit a request via the HR portal.
        """,
        "metadata": {
            "title": "Remote Work Policy 2025",
            "document_type": "policy",
            "department": "Human Resources",
            "status": "published",
            "effective_date": "2025-01-01",
            "author": "hr-team@company.com",
            "version": "1.0",
            "tags": "remote-work,flexible-arrangements,wfh"
        }
    }
)

print(f"Status: {response.status_code}")
print(response.json())
```

#### Batch Insert Documents

```python
import requests

documents = []
for i in range(1, 11):
    documents.append({
        "id": f"faq_{i}",
        "content": f"FAQ content for question {i}...",
        "metadata": {
            "title": f"FAQ {i}",
            "document_type": "faq",
            "category": "general"
        }
    })

response = requests.post(
    "http://localhost:5000/v1/documents/batch",
    json={
        "collectionName": "faqs",
        "documents": documents
    }
)

print(f"Inserted: {response.json()['insertedCount']}/{len(documents)}")
```

#### Update a Document

```python
# Update document content and metadata
response = requests.put(
    "http://localhost:5000/v1/documents/policy_remote_work_2025",
    json={
        "collectionName": "company_policies",
        "content": "Updated policy content...",
        "metadata": {
            "title": "Remote Work Policy 2025",
            "status": "published",
            "version": "1.1",
            "updated_date": "2025-11-01T10:00:00Z"
        }
    }
)
```

#### Delete a Document

```python
# Delete by ID
response = requests.delete(
    "http://localhost:5000/v1/documents/policy_remote_work_2025",
    params={"collectionName": "company_policies"}
)
```

---

### Workflow 5: Advanced Search with Filters

**Goal**: Use metadata filters to narrow search results.

#### Filter by Document Type

```python
# Search only policy documents
response = requests.post(
    "http://localhost:5000/v1/search",
    json={
        "collectionName": "company_docs",
        "query": "remote work arrangements",
        "limit": 10,
        "metadataFilters": {
            "document_type": "policy",
            "status": "published"
        }
    }
)
```

#### Filter by Department

```python
# Search only HR department documents
response = requests.post(
    "http://localhost:5000/v1/search",
    json={
        "collectionName": "company_docs",
        "query": "employee benefits",
        "limit": 5,
        "metadataFilters": {
            "department": "Human Resources",
            "status": "published"
        }
    }
)
```

#### Multi-Collection Search

```python
# Search across multiple collections
response = requests.post(
    "http://localhost:5000/v1/search",
    json={
        "collectionNames": [
            "hr_policies",
            "it_policies",
            "security_policies"
        ],
        "query": "password requirements",
        "limit": 10,
        "minScore": 0.6,
        "metadataFilters": {
            "status": "published"
        }
    }
)

data = response.json()
print(f"Searched {len(data['searchedCollections'])} collections")
print(f"Found {data['totalCount']} results")

if data.get("partialResults"):
    print(f"Warning: {data['warnings']}")
```

---

## Using the AI Agent

### Installation and Setup

See [Workflow 1: First-Time Setup](#workflow-1-first-time-setup) for installation steps.

### Interactive CLI Mode

**Start Interactive Session**:

```bash
cd ai-agent
python -m src.cli.main
```

**Features**:
- **Natural Language Queries**: Ask questions in plain English
- **Conversation Memory**: Agent remembers context from previous queries
- **Streaming Results**: See results as they're generated
- **Source Citations**: Know where information comes from
- **Multi-turn Conversations**: Ask follow-up questions

**Example Conversation**:

```
Search: What are the company core values?

✓ Found 2 highly relevant documents

📝 Response:
The company's five core values are:
1. Innovation - Encourage creative thinking
2. Integrity - Act ethically and transparently
3. Collaboration - Work together as a team
4. Excellence - Strive for quality in everything
5. Customer Focus - Put customers first

Sources: Company Handbook (2025), New Employee Orientation Guide

Search: How does the company demonstrate innovation?

✓ Using conversation context

📝 Response:
Building on the core values mentioned, the company demonstrates innovation through:
- 20% time policy for experimental projects
- Quarterly hackathons
- Innovation awards program
- Collaboration with universities
- Investment in R&D (15% of revenue)

Sources: Innovation Policy, R&D Investment Report
```

### Single Query Mode

**Run One-Off Searches**:

```bash
# Basic search
python -m src.cli.main search "vacation policy"

# With options
python -m src.cli.main search "API authentication" \
  --collection "technical_docs" \
  --limit 10 \
  --min-score 0.7
```

### Programmatic Usage

**Use AI Agent in Your Python Code**:

```python
import asyncio
from agent import IntraMindAgent

async def main():
    agent = IntraMindAgent()

    # Perform search
    result = await agent.search(
        query="What is the remote work policy?",
        collection_name="company_policies",
        num_results=5,
        min_score=0.7
    )

    if result["success"]:
        print(f"Answer: {result['response']}")
        print(f"\nSources: {', '.join(result['citations'])}")
        print(f"\nQuery Complexity: {result['complexity']}")
    else:
        print(f"Error: {result['error']}")

asyncio.run(main())
```

### Streaming Results

**Watch Search Progress in Real-Time**:

```python
import asyncio
from agent import IntraMindAgent
from rich.console import Console

async def stream_example():
    agent = IntraMindAgent()
    console = Console()

    async for update in agent.stream_search("What is the vacation policy?"):
        step = update.get('step', 'processing')
        console.print(f"[bold blue]Step:[/bold blue] {step}")

        if update.get('response'):
            console.print(f"\n[bold green]Response:[/bold green]")
            console.print(update['response'])

        if update.get('complete'):
            break

asyncio.run(stream_example())
```

---

## Using the API Gateway

### Swagger UI

**Interactive API Documentation**:

1. Open http://localhost:5000/swagger in your browser
2. Browse available endpoints
3. Try API calls directly from the browser
4. View request/response schemas

### Authentication

Currently configured for anonymous access in development.

For production:
```python
import requests

headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}

response = requests.get(
    "http://localhost:5000/v1/collections",
    headers=headers
)
```

### Error Handling

**Robust Error Handling**:

```python
import requests
from requests.exceptions import RequestException

def safe_search(query: str, collection: str) -> dict:
    """Search with comprehensive error handling."""
    try:
        response = requests.post(
            "http://localhost:5000/v1/search",
            json={
                "collectionName": collection,
                "query": query,
                "limit": 5
            },
            timeout=10.0
        )

        # Check status code
        if response.status_code == 200:
            return {"success": True, "data": response.json()}

        elif response.status_code == 400:
            errors = response.json().get("errors", {})
            return {"success": False, "error": "validation", "details": errors}

        elif response.status_code == 404:
            return {"success": False, "error": "collection_not_found"}

        elif response.status_code >= 500:
            return {"success": False, "error": "server_error"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "timeout"}

    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "connection_error"}

    except Exception as e:
        return {"success": False, "error": "unknown", "message": str(e)}

# Usage
result = safe_search("vacation policy", "company_docs")
if result["success"]:
    print(result["data"]["results"])
else:
    print(f"Error: {result['error']}")
```

---

## Advanced Features

### Conversation Memory

**Enable Context-Aware Conversations**:

```bash
# In ai-agent/.env
ENABLE_CONVERSATION_MEMORY=true
MAX_CONVERSATION_HISTORY=5
```

**Benefits**:
- Agent remembers previous questions
- Follow-up questions work naturally
- Reduced need to repeat context

**Example**:
```
Q1: What is the vacation policy?
A1: [Detailed policy explanation]

Q2: How do I request time off?  # Agent knows "time off" refers to vacation
A2: [Request process, referencing previous context]
```

### Document Ingestion Pipeline

**Ingest Files Automatically**:

```python
import asyncio
from agent import IntraMindAgent

async def ingest_directory(directory: str, collection: str):
    """Ingest all documents in a directory."""
    agent = IntraMindAgent()

    import os
    for filename in os.listdir(directory):
        if filename.endswith(('.pdf', '.docx', '.txt', '.md')):
            filepath = os.path.join(directory, filename)
            result = await agent.ingest_document(
                file_path=filepath,
                collection_name=collection
            )
            print(f"{filename}: {result['message']}")

asyncio.run(ingest_directory("/path/to/docs", "company_docs"))
```

### Metadata-Driven Access Control

**Filter by User Permissions** (future enhancement):

```python
def search_with_access_control(query: str, user_department: str) -> dict:
    """Search documents user has permission to see."""
    response = requests.post(
        "http://localhost:5000/v1/search",
        json={
            "collectionName": "company_docs",
            "query": query,
            "metadataFilters": {
                "department": user_department,  # Only user's department
                "status": "published"
            }
        }
    )
    return response.json()
```

---

## Best Practices

### For End Users

1. **Write Natural Questions**: Use complete sentences
   - ✅ "What is the company vacation policy?"
   - ❌ "vacation policy"

2. **Be Specific**: Include relevant details
   - ✅ "How do I request remote work for full-time employees?"
   - ❌ "remote work"

3. **Use Follow-Up Questions**: Take advantage of conversation memory
   - Q1: "What is the vacation policy?"
   - Q2: "How do I request it?" (agent remembers "it" = vacation)

4. **Check Sources**: Always review cited documents for full context

### For Developers

1. **Set Minimum Score Thresholds**: Filter low-quality results
   ```python
   {"minScore": 0.7}  # Only high-confidence matches
   ```

2. **Use Metadata Filters**: Narrow search space
   ```python
   {"metadataFilters": {"document_type": "policy", "status": "published"}}
   ```

3. **Handle Errors Gracefully**: Expect and handle API failures
   ```python
   try:
       response = search(...)
   except requests.exceptions.Timeout:
       return cached_results
   ```

4. **Cache Results**: Avoid redundant searches
   ```python
   @lru_cache(maxsize=100)
   def search(query, collection):
       ...
   ```

5. **Batch Operations**: Use batch insert for multiple documents
   ```python
   POST /v1/documents/batch  # Up to 100 docs
   ```

### For Administrators

1. **Organize Collections Logically**: Group related documents
   - `hr_policies`, `it_policies` (not one giant `policies` collection)

2. **Use Consistent Metadata**: Standardize field names and values
   - Always use `document_type`, not sometimes `doc_type` or `type`

3. **Keep Status Updated**: Mark documents as `draft`, `published`, `archived`

4. **Regular Maintenance**: Remove outdated documents

5. **Monitor Performance**: Track search latency and result quality

---

## Troubleshooting

### No Results Found

**Problem**: Search returns no results.

**Solutions**:
1. Check collection has documents: `GET /v1/collections/{collectionName}`
2. Lower `minScore` threshold (try 0.5)
3. Simplify query (use fewer, more general terms)
4. Remove metadata filters temporarily
5. Try different phrasing

### Low-Quality Results

**Problem**: Results don't match the query well.

**Solutions**:
1. Increase `minScore` to 0.7 or higher
2. Make query more specific and detailed
3. Use metadata filters to narrow scope
4. Check document metadata is correct

### Agent Errors

**Problem**: AI Agent fails with errors.

**Solutions**:
1. Check API Gateway is running: `curl http://localhost:5000/health`
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Check `.env` configuration
4. Review logs: `python -m src.cli.main --verbose`

### Connection Errors

**Problem**: Can't connect to services.

**Solutions**:
1. Verify services are running: `docker-compose ps`
2. Check ports aren't blocked by firewall
3. Restart services: `docker-compose restart`
4. Check Docker network: `docker network inspect intramind-network`

---

## Next Steps

1. **Explore Advanced Features**:
   - Conversation memory
   - Multi-collection search
   - Metadata filtering

2. **Build RAG Applications**:
   - Integrate with your LLM
   - Create chatbots
   - Build knowledge assistants

3. **Scale Your Deployment**:
   - Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
   - Implement authentication
   - Set up monitoring

4. **Learn the API**:
   - Review [API_REFERENCE.md](./API_REFERENCE.md)
   - Try the Swagger UI
   - Build custom integrations

---

## Additional Resources

- **API Reference**: [API_REFERENCE.md](./API_REFERENCE.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Submodule Guide**: [SUBMODULE_GUIDE.md](./SUBMODULE_GUIDE.md)
- **Project Roadmap**: [PROJECT_ROADMAP.md](./PROJECT_ROADMAP.md)

---

**Last Updated**: November 6, 2025
**Maintained By**: IntraMind Development Team
