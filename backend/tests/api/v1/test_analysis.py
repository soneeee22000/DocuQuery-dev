"""Analysis endpoint tests."""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient

from tests.conftest import FIXTURES_DIR, auth_headers, register_and_get_token


async def _upload_txt(
    client: AsyncClient,
    token: str,
    doc_type: str = "resume",
    filename: str = "sample.txt",
) -> dict[str, Any]:
    """Upload sample.txt and return the JSON response."""
    data = (FIXTURES_DIR / "sample.txt").read_bytes()
    return (
        await client.post(
            "/api/v1/documents/upload",
            headers=auth_headers(token),
            files={"file": (filename, data, "text/plain")},
            data={"doc_type": doc_type},
        )
    ).json()


def _mock_openai_success() -> MagicMock:
    """Return a mock AsyncOpenAI that returns valid analysis."""
    llm_response: dict[str, Any] = {
        "score": 75,
        "categories": {
            "skills": {
                "score": 80,
                "matched": ["Python"],
                "missing": ["Go"],
                "feedback": "Good skills.",
            },
            "experience": {
                "score": 70,
                "matched": ["3 years"],
                "missing": [],
                "feedback": "Solid.",
            },
            "education": {
                "score": 65,
                "matched": ["BS CS"],
                "missing": [],
                "feedback": "OK.",
            },
            "keywords": {
                "score": 85,
                "matched": ["API"],
                "missing": ["K8s"],
                "feedback": "Good.",
            },
        },
        "keyword_gaps": ["Go", "K8s"],
        "tips": [
            {
                "priority": i,
                "category": "skills",
                "suggestion": f"Tip {i}",
                "section": "Skills",
            }
            for i in range(1, 6)
        ],
    }
    choice = MagicMock()
    choice.message.content = json.dumps(llm_response)
    response = MagicMock()
    response.choices = [choice]

    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = response
    return mock_client


@patch("app.services.analyzer.AsyncOpenAI")
async def test_trigger_analysis_success(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """POST /analysis/match returns 201 with score and tips."""
    mock_openai_cls.return_value = _mock_openai_success()
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]

    resume = await _upload_txt(client, token, doc_type="resume")
    jd = await _upload_txt(client, token, doc_type="job_description", filename="jd.txt")

    response = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={
            "resume_id": resume["data"]["id"],
            "jd_id": jd["data"]["id"],
        },
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["score"] == 75
    assert len(body["tips"]) == 5
    assert body["resume_name"] == "sample.txt"
    assert body["jd_name"] == "jd.txt"


@patch("app.services.analyzer.AsyncOpenAI")
async def test_trigger_wrong_doc_type(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """Using a JD as resume returns 400."""
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]

    jd1 = await _upload_txt(client, token, doc_type="job_description", filename="jd1.txt")
    jd2 = await _upload_txt(client, token, doc_type="job_description", filename="jd2.txt")

    response = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={
            "resume_id": jd1["data"]["id"],
            "jd_id": jd2["data"]["id"],
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "WRONG_DOC_TYPE"


async def test_trigger_doc_not_found(client: AsyncClient) -> None:
    """Nonexistent document returns 404."""
    tokens = await register_and_get_token(client)
    response = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(tokens["access_token"]),
        json={
            "resume_id": "00000000-0000-0000-0000-000000000000",
            "jd_id": "00000000-0000-0000-0000-000000000001",
        },
    )
    assert response.status_code == 404


async def test_trigger_unauthenticated(client: AsyncClient) -> None:
    """No auth returns 401/403."""
    response = await client.post(
        "/api/v1/analysis/match",
        json={
            "resume_id": "00000000-0000-0000-0000-000000000000",
            "jd_id": "00000000-0000-0000-0000-000000000001",
        },
    )
    assert response.status_code in (401, 403)


@patch("app.services.analyzer.AsyncOpenAI")
async def test_trigger_wrong_owner(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """Using another user's document returns 404."""
    tokens1 = await register_and_get_token(client)
    resume = await _upload_txt(client, tokens1["access_token"], doc_type="resume")

    resp2 = await client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "password": "otherpassword1"},
    )
    token2 = resp2.json()["data"]["access_token"]
    jd = await _upload_txt(client, token2, doc_type="job_description", filename="jd.txt")

    response = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token2),
        json={
            "resume_id": resume["data"]["id"],
            "jd_id": jd["data"]["id"],
        },
    )
    assert response.status_code == 404


@patch("app.services.analyzer.AsyncOpenAI")
async def test_get_analysis_success(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """GET /analysis/{id} returns the analysis."""
    mock_openai_cls.return_value = _mock_openai_success()
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]

    resume = await _upload_txt(client, token, doc_type="resume")
    jd = await _upload_txt(client, token, doc_type="job_description", filename="jd.txt")

    create_resp = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={"resume_id": resume["data"]["id"], "jd_id": jd["data"]["id"]},
    )
    analysis_id = create_resp.json()["data"]["id"]

    response = await client.get(
        f"/api/v1/analysis/{analysis_id}",
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    assert response.json()["data"]["score"] == 75


async def test_get_analysis_not_found(client: AsyncClient) -> None:
    """GET nonexistent analysis returns 404."""
    tokens = await register_and_get_token(client)
    response = await client.get(
        "/api/v1/analysis/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(tokens["access_token"]),
    )
    assert response.status_code == 404


async def test_list_analyses_empty(client: AsyncClient) -> None:
    """GET /analysis/ with no analyses returns empty list."""
    tokens = await register_and_get_token(client)
    response = await client.get(
        "/api/v1/analysis/",
        headers=auth_headers(tokens["access_token"]),
    )
    assert response.status_code == 200
    assert response.json()["data"] == []


@patch("app.services.analyzer.AsyncOpenAI")
async def test_list_analyses_populated(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """GET /analysis/ returns user's analyses."""
    mock_openai_cls.return_value = _mock_openai_success()
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]

    resume = await _upload_txt(client, token, doc_type="resume")
    jd = await _upload_txt(client, token, doc_type="job_description", filename="jd.txt")

    await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={"resume_id": resume["data"]["id"], "jd_id": jd["data"]["id"]},
    )

    response = await client.get(
        "/api/v1/analysis/",
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["score"] == 75


@patch("app.services.analyzer.AsyncOpenAI")
async def test_compare_analyses_success(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """Compare two analyses returns deltas."""
    mock_openai_cls.return_value = _mock_openai_success()
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]

    resume = await _upload_txt(client, token, doc_type="resume")
    jd = await _upload_txt(client, token, doc_type="job_description", filename="jd.txt")

    resp1 = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={"resume_id": resume["data"]["id"], "jd_id": jd["data"]["id"]},
    )
    resp2 = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={"resume_id": resume["data"]["id"], "jd_id": jd["data"]["id"]},
    )

    id1 = resp1.json()["data"]["id"]
    id2 = resp2.json()["data"]["id"]

    response = await client.get(
        f"/api/v1/analysis/{id2}/compare/{id1}",
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["score_delta"] == 0
    assert len(body["category_deltas"]) == 4


async def test_compare_not_found(client: AsyncClient) -> None:
    """Compare with nonexistent analysis returns 404."""
    tokens = await register_and_get_token(client)
    response = await client.get(
        "/api/v1/analysis/00000000-0000-0000-0000-000000000000/compare/00000000-0000-0000-0000-000000000001",
        headers=auth_headers(tokens["access_token"]),
    )
    assert response.status_code == 404


@patch("app.services.analyzer.AsyncOpenAI")
async def test_trigger_llm_timeout(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """LLM timeout returns 504."""
    from openai import APITimeoutError

    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = APITimeoutError(
        request=MagicMock()
    )

    tokens = await register_and_get_token(client)
    token = tokens["access_token"]

    resume = await _upload_txt(client, token, doc_type="resume")
    jd = await _upload_txt(client, token, doc_type="job_description", filename="jd.txt")

    response = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={"resume_id": resume["data"]["id"], "jd_id": jd["data"]["id"]},
    )
    assert response.status_code == 504
    assert response.json()["error"]["code"] == "LLM_TIMEOUT"


@patch("app.services.analyzer.AsyncOpenAI")
async def test_trigger_rate_limit(
    mock_openai_cls: MagicMock, client: AsyncClient
) -> None:
    """Rate limit returns 429."""
    from openai import RateLimitError

    mock_client = AsyncMock()
    mock_openai_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}
    mock_client.chat.completions.create.side_effect = RateLimitError(
        message="Rate limited",
        response=mock_response,
        body=None,
    )

    tokens = await register_and_get_token(client)
    token = tokens["access_token"]

    resume = await _upload_txt(client, token, doc_type="resume")
    jd = await _upload_txt(client, token, doc_type="job_description", filename="jd.txt")

    response = await client.post(
        "/api/v1/analysis/match",
        headers=auth_headers(token),
        json={"resume_id": resume["data"]["id"], "jd_id": jd["data"]["id"]},
    )
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT"
