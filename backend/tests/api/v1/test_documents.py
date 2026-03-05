"""Document endpoint tests."""

from httpx import AsyncClient

from tests.conftest import FIXTURES_DIR, auth_headers, register_and_get_token


async def _upload_txt(
    client: AsyncClient,
    token: str,
    doc_type: str = "resume",
    filename: str = "sample.txt",
) -> dict:
    """Helper to upload the sample.txt fixture."""
    data = (FIXTURES_DIR / "sample.txt").read_bytes()
    return (
        await client.post(
            "/api/v1/documents/upload",
            headers=auth_headers(token),
            files={"file": (filename, data, "text/plain")},
            data={"doc_type": doc_type},
        )
    ).json()


async def test_upload_txt_success(client: AsyncClient) -> None:
    """Upload a TXT file returns 201 with extracted text."""
    tokens = await register_and_get_token(client)
    response = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers(tokens["access_token"]),
        files={
            "file": (
                "sample.txt",
                (FIXTURES_DIR / "sample.txt").read_bytes(),
                "text/plain",
            )
        },
        data={"doc_type": "resume"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["data"]["name"] == "sample.txt"
    assert "John Doe" in body["data"]["extracted_text"]


async def test_upload_unauthenticated(client: AsyncClient) -> None:
    """Upload without auth returns 401/403."""
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"content", "text/plain")},
        data={"doc_type": "resume"},
    )
    assert response.status_code in (401, 403)


async def test_upload_invalid_doc_type(client: AsyncClient) -> None:
    """Upload with invalid doc_type returns 422."""
    tokens = await register_and_get_token(client)
    response = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers(tokens["access_token"]),
        files={"file": ("test.txt", b"some content", "text/plain")},
        data={"doc_type": "invalid_type"},
    )
    assert response.status_code == 422


async def test_upload_unsupported_format(client: AsyncClient) -> None:
    """Upload unsupported file format returns 400."""
    tokens = await register_and_get_token(client)
    response = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers(tokens["access_token"]),
        files={"file": ("test.exe", b"MZ binary", "application/octet-stream")},
        data={"doc_type": "resume"},
    )
    assert response.status_code == 400


async def test_list_documents(client: AsyncClient) -> None:
    """List returns user's documents."""
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]
    await _upload_txt(client, token)

    response = await client.get(
        "/api/v1/documents/",
        headers=auth_headers(token),
    )
    assert response.status_code == 200
    docs = response.json()["data"]
    assert len(docs) == 1
    assert docs[0]["name"] == "sample.txt"


async def test_list_filter_by_type(client: AsyncClient) -> None:
    """List with doc_type filter returns matching documents."""
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]
    await _upload_txt(client, token, doc_type="resume")
    await _upload_txt(client, token, doc_type="job_description", filename="jd.txt")

    response = await client.get(
        "/api/v1/documents/?doc_type=resume",
        headers=auth_headers(token),
    )
    docs = response.json()["data"]
    assert len(docs) == 1
    assert docs[0]["doc_type"] == "resume"


async def test_delete_own_document(client: AsyncClient) -> None:
    """Delete own document returns success."""
    tokens = await register_and_get_token(client)
    token = tokens["access_token"]
    upload_resp = await _upload_txt(client, token)
    doc_id = upload_resp["data"]["id"]

    response = await client.delete(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers(token),
    )
    assert response.status_code == 200

    list_resp = await client.get(
        "/api/v1/documents/",
        headers=auth_headers(token),
    )
    assert len(list_resp.json()["data"]) == 0


async def test_delete_other_users_document(client: AsyncClient) -> None:
    """Delete another user's document returns 403."""
    tokens1 = await register_and_get_token(client)
    upload_resp = await _upload_txt(client, tokens1["access_token"])
    doc_id = upload_resp["data"]["id"]

    resp2 = await client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "password": "otherpassword1"},
    )
    token2 = resp2.json()["data"]["access_token"]

    response = await client.delete(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers(token2),
    )
    assert response.status_code == 403


async def test_delete_nonexistent_document(client: AsyncClient) -> None:
    """Delete nonexistent document returns 404."""
    tokens = await register_and_get_token(client)
    response = await client.delete(
        "/api/v1/documents/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(tokens["access_token"]),
    )
    assert response.status_code == 404
