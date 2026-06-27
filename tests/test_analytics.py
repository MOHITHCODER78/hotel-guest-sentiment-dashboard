def test_list_reviews_pagination(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={
            "reviews": [
                "Great staff and clean room at London Inn.",
                "Terrible wifi connection at Paris Hotel.",
                "Excellent breakfast and friendly staff.",
            ]
        },
        headers=auth_headers,
    )

    response = client.get("/api/v1/reviews?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json()["data"]
    assert len(payload["items"]) == 2
    assert payload["meta"]["total_items"] == 3
    assert payload["meta"]["total_pages"] == 2


def test_list_reviews_search_filter(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room.", "Terrible wifi connection."]},
        headers=auth_headers,
    )

    response = client.get("/api/v1/reviews?search=wifi", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["meta"]["total_items"] == 1


def test_list_reviews_hotel_filter_and_sort(client, auth_headers):
    client.post(
        "/api/v1/jobs/csv-upload",
        files={
            "file": (
                "reviews.csv",
                b"Hotel_Name,Full_Review\nLondon Inn,Great staff and clean room.\nParis Hotel,Terrible wifi connection.\n",
                "text/csv",
            )
        },
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/reviews?hotel=Paris&sort_by=hotel&sort_order=asc",
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["meta"]["total_items"] == 1
    assert payload["items"][0]["hotel"] == "Paris Hotel"


def test_keywords_endpoint(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room.", "Terrible wifi connection and dirty bathroom."]},
        headers=auth_headers,
    )

    response = client.get("/api/v1/analytics/keywords", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "overall_keywords" in payload
    assert isinstance(payload["overall_keywords"], list)


def test_review_csv_export(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room."]},
        headers=auth_headers,
    )

    response = client.get("/api/v1/reviews/export.csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "review_id" in response.text


def test_analytics_csv_export(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room."]},
        headers=auth_headers,
    )

    response = client.get("/api/v1/analytics/export.csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "section,name,value,count" in response.text


def test_trends_endpoint(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room."]},
        headers=auth_headers,
    )

    response = client.get("/api/v1/analytics/trends?period=weekly", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]["points"]) >= 1


def test_insights_endpoint(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room.", "Terrible wifi connection."]},
        headers=auth_headers,
    )

    response = client.get("/api/v1/analytics/insights", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["summary"]
    assert len(payload["recommendations"]) >= 1


def test_pdf_report_download(client, auth_headers):
    client.post(
        "/api/v1/jobs/bulk-upload",
        json={"reviews": ["Great staff and clean room."]},
        headers=auth_headers,
    )

    response = client.get("/api/v1/analytics/report/pdf", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
