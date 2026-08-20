# application/player_profile_service.py
from typing import Optional, Dict
from infrastructure.repositories import PlayerProfileRepository, FidePlayerRepository, FideRatingRepository

class PlayerProfileService:
    """
    Orchestrates player profile data combined with FIDE information.
    """

    @staticmethod
    def get_profile_data(profile_id: int) -> Optional[Dict]:
        """
        Fetches comprehensive profile data for a player.
        """
        profile = PlayerProfileRepository.get_by_id(profile_id)
        if not profile:
            return None
            
        data = {
            "profile": profile,
            "fide_player": None,
            "ratings": {
                "standard": None,
                "rapid": None,
                "blitz": None
            }
        }
        
        if profile.fide_id:
            fide_player = FidePlayerRepository.get_by_fide_id(profile.fide_id)
            data["fide_player"] = fide_player
            
            if fide_player:
                data["ratings"] = FidePlayerRepository.get_all_latest_ratings(profile.fide_id)
                
        return data

    @staticmethod
    def get_rating_history(profile_id: int) -> Dict[str, List[Dict]]:
        """
        Fetches rating history for a player profile.
        """
        profile = PlayerProfileRepository.get_by_id(profile_id)
        if not profile or not profile.fide_id:
            return {"standard": [], "rapid": [], "blitz": []}
            
        return FideRatingRepository.get_rating_history(profile.fide_id)