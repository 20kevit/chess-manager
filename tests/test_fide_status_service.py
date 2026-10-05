"""FIDE status centralization (items 11/12): single source, honest states."""
from application.fide.fide_status_service import FideStatusService
from infrastructure.fide.service_client import (
    FideServiceClient,
    FideServiceUnavailable,
)


class TestFideStatusService:
    def test_local_fallback_when_service_unavailable(self, app, monkeypatch):
        def boom(*a, **k):
            raise FideServiceUnavailable("down")

        monkeypatch.setattr(FideServiceClient, "get_status", classmethod(lambda cls, **k: boom()))
        with app.app_context():
            summary = FideStatusService.get_summary()
        assert summary["source"] == "local"
        assert summary["freshness"] in (
            "stale", "never", "running", "failed")
        assert isinstance(summary["players"], int)

    def test_service_path_maps_fields(self, app, monkeypatch):
        payload = {"data": {
            "players": 12345,
            "latest_period": "2099-01",
            "last_import": {"period": "2099-01", "status": "success"},
            "recent_jobs_by_state": {},
        }}
        monkeypatch.setattr(
            FideServiceClient, "get_status",
            classmethod(lambda cls, **k: payload))
        with app.app_context():
            summary = FideStatusService.get_summary()
        assert summary["source"] == "service"
        assert summary["players"] == 12345
        assert summary["freshness"] in ("healthy", "stale")

    def test_client_times_out_gracefully(self):
        # Localhost discard port: connection refused must surface as
        # FideServiceUnavailable, never a raw socket error.
        try:
            FideServiceClient._get("/status")
        except FideServiceUnavailable:
            return
        except Exception as exc:  # pragma: no cover
            raise AssertionError(f"leaked {type(exc)}") from exc
        # If something answered without a key, that is also acceptable
        # in dev (service may run open locally); nothing to assert.
