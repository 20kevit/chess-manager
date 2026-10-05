"""Client for the independent 20kevit/fide-service (read-only).

Preferred READ source for admin FIDE counts/status. All failures degrade
to FideServiceUnavailable — callers must fall back to the local importer
data, never crash an admin page. No writes, no import triggering here.
"""
import logging
import time
from typing import Any, Dict, List, Optional

import requests
from flask import current_app

logger = logging.getLogger(__name__)


class FideServiceUnavailable(Exception):
    """fide-service unreachable, unauthorized, or malformed response."""


def _conf(name: str, default=None):
    try:
        return current_app.config.get(name, default)
    except RuntimeError:  # outside app context (tests)
        return default


class FideServiceClient:
    """Thin HTTP client with timeout + short TTL memoization."""

    _cache: Dict[str, Any] = {}
    _cache_at: Dict[str, float] = {}

    @classmethod
    def _get(cls, path: str, params: Optional[dict] = None) -> dict:
        base = (_conf("FIDE_SERVICE_URL", "http://127.0.0.1:5001") or "").rstrip("/")
        api_key = _conf("FIDE_SERVICE_API_KEY", "") or ""
        timeout = _conf("FIDE_SERVICE_TIMEOUT", 5) or 5
        if not base:
            raise FideServiceUnavailable("FIDE_SERVICE_URL not configured")
        try:
            resp = requests.get(
                f"{base}/api/v1{path}",
                params=params or {},
                headers={"X-API-Key": api_key} if api_key else {},
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise FideServiceUnavailable(f"request failed: {exc}") from exc
        if resp.status_code == 401:
            raise FideServiceUnavailable("unauthorized (check FIDE_SERVICE_API_KEY)")
        if resp.status_code != 200:
            raise FideServiceUnavailable(f"HTTP {resp.status_code}")
        try:
            data = resp.json()
        except ValueError as exc:
            raise FideServiceUnavailable("invalid JSON") from exc
        if not isinstance(data, dict):
            raise FideServiceUnavailable("unexpected payload")
        return data

    @classmethod
    def get_status(cls, max_age: Optional[int] = None) -> dict:
        """Service + dataset status (players count, periods, last import).

        Memoized for FIDE_STATUS_CACHE_TTL seconds so admin pages never
        hammer the service. Raises FideServiceUnavailable on any problem.
        """
        ttl = max_age if max_age is not None else (_conf("FIDE_STATUS_CACHE_TTL", 300) or 300)
        now = time.monotonic()
        cached = cls._cache.get("status")
        if cached is not None and now - cls._cache_at.get("status", 0) < ttl:
            return cached
        data = cls._get("/status")
        cls._cache["status"] = data
        cls._cache_at["status"] = now
        return data

    @classmethod
    def search_players(cls, query: str, limit: int = 20) -> List[dict]:
        data = cls._get("/players/search", {"q": query, "limit": limit})
        players = data.get("players", data.get("data", []))
        return players if isinstance(players, list) else []

    @classmethod
    def get_player(cls, fide_id: str) -> dict:
        return cls._get(f"/players/{fide_id}")

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()
        cls._cache_at.clear()
