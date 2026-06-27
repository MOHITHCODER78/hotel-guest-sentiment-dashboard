import io

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "healthy"


def test_register_and_login(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newmanager@hotel.com",
            "password": "securepass123",
            "full_name": "New Manager",
        },
    )
    assert register_response.status_code == 200
    assert register_response.json()["data"]["email"] == "newmanager@hotel.com"

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "newmanager@hotel.com", "password": "securepass123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["data"]["access_token"]


def test_analyze_requires_auth(client):
    response = client.post(
        "/api/v1/analyze",
        json={"text": "The staff was amazing and the room was spotless."},
    )
    assert response.status_code == 401


def test_analyze_review(client, auth_headers):
    response = client.post(
        "/api/v1/analyze",
        json={"text": "The staff was amazing and the room was spotless."},
        headers=auth_headers,
    )
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["review"].startswith("The staff")
    assert len(payload["sentiments"]) >= 1
    assert all("aspect" in item for item in payload["sentiments"])


def test_analyze_rejects_empty_text(client, auth_headers):
    response = client.post("/api/v1/analyze", json={"text": ""}, headers=auth_headers)
    assert response.status_code == 422


def test_bulk_upload_and_job_status(client, auth_headers):
    upload_response = client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room.", "Terrible wifi connection."]},
        headers=auth_headers,
    )
    assert upload_response.status_code == 200

    task_id = upload_response.json()["data"]["task_id"]
    status_response = client.get(f"/api/v1/jobs/{task_id}", headers=auth_headers)
    assert status_response.status_code == 200

    status_payload = status_response.json()["data"]
    assert status_payload["task_id"] == task_id
    assert status_payload["status"] == "COMPLETED"
    assert status_payload["processed_reviews"] == 2


def test_csv_upload(client, auth_headers):
    csv_content = (
        "Hotel_Name,Full_Review\n"
        "Test Hotel,Great staff and clean room.\n"
        "Another Hotel,Terrible wifi connection.\n"
    )
    response = client.post(
        "/api/v1/jobs/csv-upload",
        files={"file": ("reviews.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200

    task_id = response.json()["data"]["task_id"]
    status_response = client.get(f"/api/v1/jobs/{task_id}", headers=auth_headers)
    assert status_response.json()["data"]["status"] == "COMPLETED"
    assert status_response.json()["data"]["processed_reviews"] == 2


def test_job_not_found_returns_structured_error(client, auth_headers):
    response = client.get("/api/v1/jobs/non-existent-id", headers=auth_headers)
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "job_not_found"


def test_latest_reviews_empty_database(client, auth_headers):
    response = client.get("/api/v1/reviews/latest", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_stats_empty_database(client, auth_headers):
    response = client.get("/api/v1/analytics/stats", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["total_reviews"] == 0
    assert payload["critical_issues"][0]["issue"] == "Platform Healthy"


def test_user_cannot_access_other_user_job(client, auth_headers):
    upload_response = client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room."]},
        headers=auth_headers,
    )
    task_id = upload_response.json()["data"]["task_id"]

    client.post(
        "/api/v1/auth/register",
        json={
            "email": "other@hotel.com",
            "password": "securepass123",
            "full_name": "Other Manager",
        },
    )
    other_login = client.post(
        "/api/v1/auth/login",
        data={"username": "other@hotel.com", "password": "securepass123"},
    )
    other_headers = {
        "Authorization": f"Bearer {other_login.json()['data']['access_token']}"
    }

    response = client.get(f"/api/v1/jobs/{task_id}", headers=other_headers)
    assert response.status_code == 404
