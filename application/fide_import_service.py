"""
FIDE Import Orchestration Service.
Downloads (or picks up a server-placed ZIP/XML), parses, and stores FIDE
rating data into the database.

P1-G: honest stage/percent progress persisted on the import row, a
row-locked concurrency claim, retained stale-run recovery, and a
background-thread launcher so the HTTP request returns immediately.
The synchronous core remains callable directly (tests / CLI).
"""
import logging
import threading
from datetime import datetime, timedelta

from app.extensions import db

from infrastructure.fide.storage import (
    FideStorageManager, FideStorageError, count_players_in_xml,
    get_period_string,
)
from infrastructure.fide import storage as _fide_storage
from domain.fide.parser import parse_fide_xml
from flask import current_app

from infrastructure.models.fide import (FideImportModel, FidePlayerModel, FideRatingModel)
from infrastructure.repositories.fide import (FideImportRepository, FidePlayerRepository, FideRatingRepository)
STALE_RUN_MINUTES = 15
BATCH_SIZE = 500

class FideImportService:

    # ── Public entries ────────────────────────────────────────────────

    @staticmethod
    def run_import() -> dict:
        """Synchronous entry point (kept for tests/CLI compatibility)."""
        return FideImportService.execute_import()

    @staticmethod
    def start_async() -> str:
        """Spawn the import on a background thread bound to this app.

        Returns one of: 'started' | 'skipped' | 'already_running'.
        The claiming itself happens inside execute_import under lock, so
        'started' means the thread was launched; the dashboard polls the
        status endpoint for the real outcome.
        """
        app = current_app._get_current_object()
        period = get_period_string()
        latest = FideImportRepository.get_by_period(period)
        if latest and latest.status == "success":
            return "skipped"
        if (
            latest and latest.status == "pending"
            and latest.downloaded_at
            and (datetime.utcnow() - latest.downloaded_at)
            < timedelta(minutes=STALE_RUN_MINUTES)
        ):
            return "already_running"

        def _runner():
            with app.app_context():
                FideImportService.execute_import()

        threading.Thread(target=_runner, name="fide-import",
                         daemon=True).start()
        return "started"

    @staticmethod
    def execute_import(source_label: str = "auto_download") -> dict:
        """Full pipeline. Safe to call from a background thread that holds
        an application context."""
        period = get_period_string()
        allowed_feds = current_app.config.get("FIDE_ALLOWED_FEDERATIONS")

        # 1-1b/1c: locked claim of the period record (closes the old
        # advisory race) with identical skip/stale semantics as before.
        existing = FideImportModel.query.filter_by(period=period) \
            .with_for_update().first()
        if existing and existing.status == "success":
            db.session.rollback()
            return {"status": "skipped",
                    "message": f"Period {period} already imported."}
        if (
            existing and existing.status == "pending"
            and existing.downloaded_at
            and (datetime.utcnow() - existing.downloaded_at)
            < timedelta(minutes=STALE_RUN_MINUTES)
        ):
            db.session.rollback()
            return {"status": "already_running",
                    "message": "An import for this period is in progress."}
        if existing and existing.status == "pending":
            existing.status = "failed"
            existing.error_message = \
                "Marked failed: previous run did not complete."

        record = existing or FideImportModel(period=period)
        record.status = "pending"
        record.stage = None
        record.progress_percent = 0
        record.download_progress = 0
        record.processing_progress = 0
        record.source_url = source_label
        record.error_message = None
        record.records_processed = 0
        record.records_imported = 0
        record.downloaded_at = datetime.utcnow()
        FideImportRepository.save(record)
        db.session.commit()

        try:
            # ── Stage: acquire XML (download OR server-placed file) ──
            record.stage = "download"
            record.download_progress = 0
            db.session.commit()

            def _download_progress(fraction):
                if fraction is not None:
                    record.download_progress = max(
                        record.download_progress or 0,
                        min(100, int(fraction * 100)),
                    )
                    db.session.commit()
                elif (record.download_progress or 0) < 100:
                    record.download_progress = \
                        min(100, (record.download_progress or 0) + 10)
                    db.session.commit()

            # Late-bound module call so tests (and future callers) can
            # patch acquisition at the storage-module level.
            provenance, xml_path = _fide_storage.ensure_players_xml(
                progress_cb=_download_progress)

            # Download complete - set to 100
            record.download_progress = 100
            record.stage = "extract"
            record.processing_progress = 0
            db.session.commit()

            if source_label == "auto_download" and provenance != "downloaded":
                # Keep provenance truthful for server-placed files even
                # when the trigger came from the admin UI button.
                record.source_url = f"server_file:{provenance}"
                # Manual cPanel file: download is effectively complete
                record.download_progress = 100
                db.session.commit()

            total_players = count_players_in_xml(xml_path)

            # ── Stage: parse/persist ──
            record.stage = "parse"
            record.processing_progress = 0 if total_players else None
            db.session.commit()

            processed = 0
            imported = 0

            for player_data in parse_fide_xml(
                    xml_path, allowed_federations=allowed_feds):
                processed += 1

                player = FidePlayerRepository.get_by_fide_id(
                    player_data.fide_id)
                if player:
                    player.name = player_data.name
                    player.sex = player_data.sex
                    player.federation = player_data.federation
                    player.title = player_data.title or ""
                    player.wtitle = player_data.wtitle or ""
                    player.otitle = player_data.otitle or ""
                    player.foatitle = player_data.foatitle or ""
                    player.birth_year = player_data.birth_year or ""
                    player.inactive = player_data.inactive
                else:
                    player = FidePlayerModel(
                        fide_id=player_data.fide_id,
                        name=player_data.name,
                        federation=player_data.federation,
                        sex=player_data.sex,
                        title=player_data.title or "",
                        wtitle=player_data.wtitle or "",
                        otitle=player_data.otitle or "",
                        foatitle=player_data.foatitle or "",
                        birth_year=player_data.birth_year or "",
                        inactive=player_data.inactive
                    )
                    FidePlayerRepository.save(player)
                    imported += 1

                FideImportService._save_rating(
                    fide_id=player_data.fide_id, period=period,
                    rating_type="standard",
                    rating=player_data.rating_standard,
                    games=player_data.games_standard,
                    k_factor=player_data.k_standard)
                FideImportService._save_rating(
                    fide_id=player_data.fide_id, period=period,
                    rating_type="rapid",
                    rating=player_data.rating_rapid,
                    games=player_data.games_rapid,
                    k_factor=player_data.k_rapid)
                FideImportService._save_rating(
                    fide_id=player_data.fide_id, period=period,
                    rating_type="blitz",
                    rating=player_data.rating_blitz,
                    games=player_data.games_blitz,
                    k_factor=player_data.k_blitz)

                if processed % BATCH_SIZE == 0:
                    db.session.commit()
                    record.records_processed = processed
                    if total_players:
                        pct = int(100 * processed / total_players)
                        record.processing_progress = min(95, pct)
                    else:
                        record.processing_progress = min(
                            95, (record.processing_progress or 0) + 5)
                    db.session.commit()
                    current_app.logger.info(
                        "FIDE Import Progress (%s): %s processed",
                        period, processed)

            # ── Stage: finalize ──
            db.session.commit()
            record.stage = "finalize"
            record.processing_progress = 100
            db.session.commit()

            record.status = "success"
            record.imported_at = datetime.utcnow()
            record.records_processed = processed
            record.records_imported = imported
            record.progress_percent = 100
            FideImportRepository.save(record)
            db.session.commit()

            deleted_files = FideStorageManager.cleanup_old_files()
            return {
                "status": "success",
                "processed": processed,
                "imported": imported,
                "source": provenance,
                "deleted_old_files": deleted_files,
            }

        except Exception as e:
            db.session.rollback()
            record.status = "failed"
            record.error_message = str(e)
            FideImportRepository.save(record)
            db.session.commit()
            current_app.logger.error(f"FIDE Import failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    def latest_status() -> dict:
        """Payload for the admin status polling endpoint."""
        latest = FideImportModel.query.order_by(
            FideImportModel.id.desc()).first()
        if not latest:
            return {"status": "idle"}
        return {
            "status": latest.status,
            "stage": latest.stage,
            "progress_percent": latest.progress_percent,
            "download_progress": latest.download_progress,
            "processing_progress": latest.processing_progress,
            "records_processed": latest.records_processed or 0,
            "records_imported": latest.records_imported or 0,
            "error_message": latest.error_message,
        }

    @staticmethod
    def _save_rating(fide_id: str, period: str, rating_type: str,
                     rating: int, games: int, k_factor: int):
        """Saves a rating record if it doesn't already exist for this period."""
        existing = FideRatingRepository.get(fide_id, period, rating_type)
        if not existing:
            rating_record = FideRatingModel(
                fide_id=fide_id,
                period=period,
                rating_type=rating_type,
                rating=rating,
                games=games,
                k_factor=k_factor
            )
            FideRatingRepository.save(rating_record)

# Module-level logger convenience for the fire-safe hooks above.
logger = logging.getLogger(__name__)
