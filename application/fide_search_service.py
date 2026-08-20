"""
FIDE Search Service.
Handles searching the local FIDE database.
"""
from typing import List, Dict, Optional
from infrastructure.repositories import FidePlayerRepository

class FideSearchService:

    @staticmethod
    def search(query: str, federation: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        Searches for players and returns formatted data including latest ratings.
        """
        players = FidePlayerRepository.search_players(query, federation, limit)
        results = []
        
        for p in players:
            # Fetch latest ratings for each type
            std = FidePlayerRepository.get_latest_rating(p.fide_id, "standard")
            rapid = FidePlayerRepository.get_latest_rating(p.fide_id, "rapid")
            blitz = FidePlayerRepository.get_latest_rating(p.fide_id, "blitz")
            
            results.append({
                "fide_id": p.fide_id,
                "name": p.name,
                "federation": p.federation,
                "title": p.title or "",
                "birth_year": p.birth_year or "",
                "sex": p.sex,
                "standard": std.rating if std else 0,
                "rapid": rapid.rating if rapid else 0,
                "blitz": blitz.rating if blitz else 0,
                "period": std.period if std else "" # Period of the standard rating
            })
            
        return results