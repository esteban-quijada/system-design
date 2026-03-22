from datetime import datetime, timedelta, timezone

from url_shortener import URLRecord


class TestShortenEndpoint:
    def test_shorten_success(self, client):
        response = client.post("/shorten", json={"url": "https://example.com/"})
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert "short_url" in data
        assert "created_at" in data
        assert data["expires_at"] is None

    def test_short_url_contains_short_code(self, client):
        response = client.post("/shorten", json={"url": "https://example.com/"})
        data = response.json()
        assert data["short_code"] in data["short_url"]

    def test_shorten_with_expiry(self, client):
        response = client.post("/shorten", json={"url": "https://example.com/", "expires_in_hours": 24})
        assert response.status_code == 200
        assert response.json()["expires_at"] is not None

    def test_shorten_invalid_url(self, client):
        response = client.post("/shorten", json={"url": "not-a-url"})
        assert response.status_code == 422

    def test_shorten_missing_url(self, client):
        response = client.post("/shorten", json={})
        assert response.status_code == 422


class TestRedirectEndpoint:
    def test_redirect_success(self, client):
        shorten = client.post("/shorten", json={"url": "https://example.com/"})
        short_code = shorten.json()["short_code"]
        response = client.get(f"/{short_code}", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "https://example.com/"

    def test_redirect_not_found(self, client):
        response = client.get("/nonexistent", follow_redirects=False)
        assert response.status_code == 404

    def test_redirect_expired(self, client, db_session):
        record = URLRecord(
            short_code="expiredcode",
            original_url="https://example.com/",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(record)
        db_session.commit()
        response = client.get("/expiredcode", follow_redirects=False)
        assert response.status_code == 410

    def test_redirect_increments_click_count(self, client):
        shorten = client.post("/shorten", json={"url": "https://example.com/"})
        short_code = shorten.json()["short_code"]
        client.get(f"/{short_code}", follow_redirects=False)
        client.get(f"/{short_code}", follow_redirects=False)
        stats = client.get(f"/stats/{short_code}")
        assert stats.json()["click_count"] == 2


class TestStatsEndpoint:
    def test_stats_success(self, client):
        shorten = client.post("/shorten", json={"url": "https://example.com/"})
        short_code = shorten.json()["short_code"]
        response = client.get(f"/stats/{short_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == short_code
        assert data["original_url"] == "https://example.com/"
        assert data["click_count"] == 0

    def test_stats_not_found(self, client):
        response = client.get("/stats/nonexistent")
        assert response.status_code == 404

    def test_stats_reflects_click_count(self, client):
        shorten = client.post("/shorten", json={"url": "https://example.com/"})
        short_code = shorten.json()["short_code"]
        for _ in range(3):
            client.get(f"/{short_code}", follow_redirects=False)
        stats = client.get(f"/stats/{short_code}")
        assert stats.json()["click_count"] == 3
