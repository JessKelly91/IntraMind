"""
Configuration for IntraMind integration tests.

This module provides service URL configuration that can be overridden
via environment variables for CI/CD environments.
"""

import os


# Service Configuration (with environment variable overrides for CI)
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:64536")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
PROMPT_REGISTRY_URL = os.getenv("PROMPT_REGISTRY_URL", "http://localhost:8010")
PROMPT_REGISTRY_ADMIN_API_KEY = os.getenv("PROMPT_REGISTRY_ADMIN_API_KEY", "admin-dev-key")
PROMPT_REGISTRY_SERVICE_API_KEY = os.getenv("PROMPT_REGISTRY_SERVICE_API_KEY", "service-dev-key")
REQUIRE_OLLAMA = os.getenv("REQUIRE_OLLAMA", "true").lower() == "true"

# Feature flags for test execution
VECTORIZER_ENABLED = os.getenv("VECTORIZER_ENABLED", "true").lower() == "true"

# Timeouts
SERVICE_CHECK_TIMEOUT = 5
API_REQUEST_TIMEOUT = 30
