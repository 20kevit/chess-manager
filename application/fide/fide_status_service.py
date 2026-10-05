"""Centralized FIDE source-of-truth for admin reads (items 11/12).

Single entry point: FideStatusService.get_summary().

Preferred source is the independent fide-service (read-only HTTP);
the local importer database is the fallback. Freshness is explicit —
never report "healthy" from stale or missing data.

Freshness values: healthy | stale | running | failed | never | unavailable
"""
import logging
from datetime import datetime
from typing import Any, Dict

from infrastructure.fide.service_client import (
    FideServiceClient,
    FideServiceUnavailable,
)
from infrastructure.models.fide import FideImportModel, FidePlayerModel

logger = logging.getLogger(__name__)


def _current_period() -> str:
    return datetime.utcnow().strftime("%Y-%m")


class FideStatusService:
    """Single source of truth for admin FIDE reads."""

    @staticmethod
    def get_summary() -> Dict[str, Any]:
        """Return {source, players, latest_period, last_import, freshness}.

        source: "service" | "local" | "unavailable"
        last_import: {period, status, imported_at, records_processed} | None
        """
        try:
            status = FideServiceClient.get_status()
            return FideStatusService._from_service(status)
        except FideServiceUnavailable as exc:
            logger.warning("fide-service unavailable, using local data: %s", exc)
            return FideStatusService._from_local()
        except Exception:  # never break admin pages
            logger.exception("unexpected fide-service failure")
            return FideStatusService._from_local()

    # -- service path ----------------------------------------------------
    @staticmethod
    def _from_service(status: dict) -> Dict[str, Any]:
        data = status.get("data", status)
        players = data.get("players", 0) or 0
        latest_period = data.get("latest_period")
        last_import = data.get("last_import")
        freshness = FideStatusService._service_freshness(data)
        return {
            "source": "service",
            "players": players,
            "latest_period": latest_period,
            "last_import": last_import,
            "freshness": freshness,
        }

    @staticmethod
    def _service_freshness(data: dict) -> str:
        states = data.get("recent_jobs_by_state", {}) or {}
        if states.get("running", 0) > 0 or states.get("pending", 0) > 0:
            return "running"
        if states.get("failed", 0) > 0:
            return "failed"
        last_import = data.get("last_import") or {}
        if not data.get("latest_period"):
            return "never"
        if last_import.get("status") == "failed":
            return "failed"
        if last_import.get("status") != "success":
            return "stale"
        if last_import.get("period") != _current_period():
            return "stale"
        return "healthy"

    # -- local fallback --------------------------------------------------
    @staticmethod
    def _from_local() -> Dict[str, Any]:
        players = FidePlayerModel.query.count()
        last = (
            FideImportModel.query.order_by(FideImportModel.downloaded_at.desc()).first()
        )
        if players == 0 and last is None:
            freshness = "never"
        elif last is None:
            freshness = "stale"
        elif last.status == "pending":
            freshness = "running"
        elif last.status == "failed":
            freshness = "failed"
        elif last.status == "success" and (last.imported_at is None):
            freshness = "running"
        else:
            freshness = "stale"  # local data, service unreachable: honest
        last_import = None
        if last is not None:
            last_import = {
                "period": last.period,
                "status": last.status,
                "imported_at": (
                    last.imported_at.strftime("%Y-%m-%d %H:%M")
                    if last.imported_at
                    else None
                ),
                "records_processed": last.records_processed,
            }
        return {
            "source": "local",
            "players": players,
            "latest_period": last.period if last else None,
            "last_import": last_import,
            "freshness": freshness,
        }
