"""
FIDE Import Orchestration Service.
Downloads, parses, and stores FIDE rating data into the database.
"""
from datetime import datetime
from typing import List, Optional
from app.extensions import db
from infrastructure.repositories import FidePlayerRepository, FideRatingRepository, FideImportRepository
from infrastructure.db_models import FidePlayerModel, FideRatingModel, FideImportModel
from infrastructure.fide.storage import FideStorageManager
from domain.fide.parser import parse_fide_xml
from flask import current_app

class FideImportService:

    @staticmethod
    def run_import() -> dict:
        """
        Main entry point for importing FIDE data.
        Returns a dictionary with import results.
        """
        period = FideStorageManager.get_period_string()
        allowed_feds = current_app.config.get("FIDE_ALLOWED_FEDERATIONS")
        
        # 1. Check if already imported
        existing_import = FideImportRepository.get_by_period(period)
        if existing_import and existing_import.status == "success":
            return {
                "status": "skipped",
                "message": f"Period {period} already imported successfully."
            }

        # 2. Get or create import record
        import_record = existing_import or FideImportModel(period=period)
        import_record.status = "pending"
        import_record.downloaded_at = datetime.utcnow()
        FideImportRepository.save(import_record)
        db.session.commit()

        try:
            # 3. Download and extract XML
            xml_path = FideStorageManager.download_and_extract_xml()
            if not xml_path:
                raise Exception("Failed to download or extract FIDE XML file.")

            # 4. Parse and store data
            processed = 0
            imported = 0
            
            for player_data in parse_fide_xml(xml_path, allowed_federations=allowed_feds):
                processed += 1
                
                # Update or create player identity
                player = FidePlayerRepository.get_by_fide_id(player_data.fide_id)
                if player:
                    # Update existing record
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
                    # Create new record
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

                # Save ratings (Standard, Rapid, Blitz)
                # We save all three types as they appear in the XML
                FideImportService._save_rating(
                    fide_id=player_data.fide_id,
                    period=period,
                    rating_type="standard",
                    rating=player_data.rating_standard,
                    games=player_data.games_standard,
                    k_factor=player_data.k_standard
                )
                FideImportService._save_rating(
                    fide_id=player_data.fide_id,
                    period=period,
                    rating_type="rapid",
                    rating=player_data.rating_rapid,
                    games=player_data.games_rapid,
                    k_factor=player_data.k_rapid
                )
                FideImportService._save_rating(
                    fide_id=player_data.fide_id,
                    period=period,
                    rating_type="blitz",
                    rating=player_data.rating_blitz,
                    games=player_data.games_blitz,
                    k_factor=player_data.k_blitz
                )

                # Commit in batches to avoid huge transactions
                if processed % 500 == 0:
                    db.session.commit()
                    current_app.logger.info(f"FIDE Import Progress: {processed} processed...")

            # 5. Final commit and update record
            db.session.commit()
            
            import_record.status = "success"
            import_record.imported_at = datetime.utcnow()
            import_record.records_processed = processed
            import_record.records_imported = imported
            FideImportRepository.save(import_record)
            db.session.commit()

            # 6. Cleanup old files
            deleted_files = FideStorageManager.cleanup_old_files()
            
            return {
                "status": "success",
                "processed": processed,
                "imported": imported,
                "deleted_old_files": deleted_files
            }

        except Exception as e:
            db.session.rollback()
            import_record.status = "failed"
            import_record.error_message = str(e)
            FideImportRepository.save(import_record)
            db.session.commit()
            current_app.logger.error(f"FIDE Import failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    @staticmethod
    def _save_rating(fide_id: str, period: str, rating_type: str, rating: int, games: int, k_factor: int):
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