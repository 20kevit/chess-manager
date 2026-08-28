"""
FIDE Repositories.
"""
from typing import Optional, List, Dict, Tuple

from app.extensions import db

from infrastructure.models.fide import FideImportModel, FidePlayerModel, FideRatingModel


class FidePlayerRepository:
    @staticmethod
    def get_by_fide_id(fide_id: str) -> Optional[FidePlayerModel]:
        return FidePlayerModel.query.get(fide_id)

    @staticmethod
    def get_by_fide_ids(fide_ids: List[str]) -> Dict[str, FidePlayerModel]:
        """Bulk fetch mapped by fide_id. Missing IDs are simply absent."""
        if not fide_ids:
            return {}
        rows = FidePlayerModel.query.filter(FidePlayerModel.fide_id.in_(fide_ids)).all()
        return {p.fide_id: p for p in rows}

    @staticmethod
    def save(player: FidePlayerModel) -> FidePlayerModel:
        db.session.add(player)
        db.session.flush()
        return player

    @staticmethod
    def search_players(query: str, federation: Optional[str] = None, limit: int = 20) -> List[FidePlayerModel]:
        """
        Search players by FIDE ID or Name.
        - If query is numeric, it searches for FIDE IDs starting with that number.
        - Otherwise, it splits the query by spaces and matches ALL parts (case-insensitive).
        """
        q = FidePlayerModel.query

        if query:
            if query.isdigit():
                # Partial match on FIDE ID
                q = q.filter(FidePlayerModel.fide_id.like(f"{query}%"))
            else:
                # Split query by spaces and require all parts to be present in the name
                search_terms = query.split()
                for term in search_terms:
                    if term:
                        # ilike is case-insensitive in SQLAlchemy
                        q = q.filter(FidePlayerModel.name.ilike(f"%{term}%"))

        if federation:
            q = q.filter(FidePlayerModel.federation == federation)

        return q.limit(limit).all()

    @staticmethod
    def get_latest_rating(fide_id: str, rating_type: str = "standard") -> Optional[FideRatingModel]:
        """Fetches the most recent rating record for a player."""
        return FideRatingModel.query.filter_by(
            fide_id=fide_id,
            rating_type=rating_type
        ).order_by(FideRatingModel.period.desc()).first()

    @staticmethod
    def get_all_latest_ratings(fide_id: str) -> Dict[str, Optional[Dict]]:
        """
        Fetches the most recent rating records for all types (standard, rapid, blitz).
        Returns a dictionary with rating types as keys.
        """
        ratings = {
            "standard": None,
            "rapid": None,
            "blitz": None
        }

        if not fide_id:
            return ratings

        for r_type in ["standard", "rapid", "blitz"]:
            record = FideRatingModel.query.filter_by(
                fide_id=fide_id,
                rating_type=r_type
            ).order_by(FideRatingModel.period.desc()).first()

            if record:
                ratings[r_type] = {
                    "rating": record.rating,
                    "games": record.games,
                    "k_factor": record.k_factor,
                    "period": record.period
                }

        return ratings

class FideRatingRepository:
    @staticmethod
    def get(fide_id: str, period: str, rating_type: str) -> Optional[FideRatingModel]:
        return FideRatingModel.query.filter_by(
            fide_id=fide_id, period=period, rating_type=rating_type
        ).first()

    @staticmethod
    def save(rating: FideRatingModel) -> FideRatingModel:
        db.session.add(rating)
        db.session.flush()
        return rating

    @staticmethod
    def get_latest_for_fide_ids(fide_ids: List[str]) -> Dict[Tuple[str, str], FideRatingModel]:
        """Bulk variant of get_latest_rating: one query returning the latest-
        period row per (fide_id, rating_type) for the given IDs."""
        if not fide_ids:
            return {}
        rows = (
            FideRatingModel.query.filter(FideRatingModel.fide_id.in_(fide_ids))
            .order_by(FideRatingModel.period.asc())
            .all()
        )
        # Ascending order + overwrite => the surviving value per key is the
        # latest period. Periods are unique per key (DB unique constraint).
        latest: Dict[Tuple[str, str], FideRatingModel] = {}
        for row in rows:
            latest[(row.fide_id, row.rating_type)] = row
        return latest

    @staticmethod
    def get_rating_history(fide_id: str) -> Dict[str, List[Dict]]:
        """
        Fetches full rating history for a player, grouped by rating type.
        Ordered by period ascending (oldest first) for charting purposes.
        """
        history = {
            "standard": [],
            "rapid": [],
            "blitz": []
        }

        if not fide_id:
            return history

        records = FideRatingModel.query.filter_by(
            fide_id=fide_id
        ).order_by(FideRatingModel.period.asc()).all()

        for rec in records:
            if rec.rating_type in history:
                history[rec.rating_type].append({
                    "period": rec.period,
                    "rating": rec.rating,
                    "games": rec.games
                })

        return history

class FideImportRepository:
    @staticmethod
    def get_by_period(period: str) -> Optional[FideImportModel]:
        return FideImportModel.query.filter_by(period=period).first()

    @staticmethod
    def save(import_record: FideImportModel) -> FideImportModel:
        db.session.add(import_record)
        db.session.flush()
        return import_record

    @staticmethod
    def get_all() -> List[FideImportModel]:
        """Returns all import records, newest first."""
        return FideImportModel.query.order_by(FideImportModel.downloaded_at.desc()).all()