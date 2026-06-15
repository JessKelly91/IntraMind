"""Integration smoke tests for the Prompt Registry service."""

from __future__ import annotations

import pytest
import requests

from .config import (
    PROMPT_REGISTRY_ADMIN_API_KEY,
    PROMPT_REGISTRY_SERVICE_API_KEY,
    PROMPT_REGISTRY_URL,
)


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.smoke
def test_prompt_registry_seed_and_resolve(api_client: requests.Session):
    admin_headers = {"X-API-Key": PROMPT_REGISTRY_ADMIN_API_KEY}
    service_headers = {"X-API-Key": PROMPT_REGISTRY_SERVICE_API_KEY}

    seed = api_client.post(
        f"{PROMPT_REGISTRY_URL}/api/v1/admin/seed",
        headers=admin_headers,
        timeout=10,
    )
    assert seed.status_code == 200
    assert seed.json()["seeded"] >= 3

    resolved = api_client.get(
        f"{PROMPT_REGISTRY_URL}/api/v1/prompts/result_synthesis",
        params={"label": "production"},
        headers=service_headers,
        timeout=10,
    )
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["id"] == "result_synthesis"
    assert body["label"] == "production"
    assert body["template"]


@pytest.mark.integration
@pytest.mark.health
def test_prompt_registry_unauthorized_read_is_rejected(api_client: requests.Session):
    response = api_client.get(
        f"{PROMPT_REGISTRY_URL}/api/v1/prompts",
        headers={"X-API-Key": "not-a-real-key"},
        timeout=5,
    )
    assert response.status_code == 401
