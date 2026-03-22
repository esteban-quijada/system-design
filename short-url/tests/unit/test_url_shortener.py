from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from url_shortener import ShortenRequest, StatsResponse


class TestShortenRequest:
    def test_valid_url(self):
        req = ShortenRequest(url="https://example.com/")
        assert str(req.url) == "https://example.com/"

    def test_invalid_url_raises(self):
        with pytest.raises(ValidationError):
            ShortenRequest(url="not-a-url")

    def test_expires_in_hours_defaults_to_none(self):
        req = ShortenRequest(url="https://example.com/")
        assert req.expires_in_hours is None

    def test_expires_in_hours_set(self):
        req = ShortenRequest(url="https://example.com/", expires_in_hours=24)
        assert req.expires_in_hours == 24


class TestExpiryLogic:
    def test_expiry_is_in_the_future(self):
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=1)
        assert expires_at > now

    def test_past_expiry_is_expired(self):
        now = datetime.now(timezone.utc)
        expires_at = now - timedelta(hours=1)
        assert now > expires_at

    def test_no_expiry_never_expires(self):
        expires_at = None
        assert expires_at is None


class TestStatsResponse:
    def test_fields_populated_correctly(self):
        now = datetime.now(timezone.utc)
        stats = StatsResponse(
            short_code="abc123",
            original_url="https://example.com/",
            created_at=now,
            click_count=5,
        )
        assert stats.short_code == "abc123"
        assert stats.original_url == "https://example.com/"
        assert stats.click_count == 5
        assert stats.expires_at is None

    def test_expires_at_optional(self):
        now = datetime.now(timezone.utc)
        stats = StatsResponse(
            short_code="abc123",
            original_url="https://example.com/",
            created_at=now,
            click_count=0,
            expires_at=now + timedelta(hours=24),
        )
        assert stats.expires_at is not None
