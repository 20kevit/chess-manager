"""
FIDE Rating Fetcher Service.

Handles automatic FIDE rating fetching for player profiles.
"""
from datetime import date
from typing import Optional

from app.extensions import db

from infrastructure.repositories.fide import FidePlayerRepository


class FideRatingFetcher:
    """Handles automatic FIDE rating fetching for player profiles."""

    @staticmethod
    def auto_fetch_rating(profile, tournament) -> tuple:
        """Auto-fetch FIDE rating for a profile based on tournament time control.
        
        Returns:
            tuple: (rating, k_factor) - Updated rating and k_factor
        """
        rating = 0
        k_factor = 20
        
        # Only auto-fetch if no rating provided and profile has FIDE ID
        if profile.fide_id:
            rating_type = getattr(tournament, "time_control_type", "standard")
            if rating_type not in ["standard", "rapid", "blitz"]:
                rating_type = "standard"
            
            fide_rating = FidePlayerRepository.get_latest_rating(profile.fide_id, rating_type)
            if fide_rating:
                rating = fide_rating.rating or 0
                k_factor = fide_rating.k_factor or 20
        
        return rating, k_factor