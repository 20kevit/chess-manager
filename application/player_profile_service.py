# application/player_profile_service.py
from typing import Optional, Dict, List
from infrastructure.repositories import PlayerProfileRepository, FidePlayerRepository, FideRatingRepository, ParticipantRepository

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

    @staticmethod
    def get_tournament_history(profile_id: int) -> List[Dict]:
        """
        Fetches tournament history for a player profile.
        """
        participants = ParticipantRepository.get_all_by_profile_id(profile_id)
        
        history = []
        for p in participants:
            tournament = p.tournament
            if not tournament:
                continue
                
            history.append({
                "tournament_id": tournament.id,
                "public_id": tournament.public_id,
                "name": tournament.name,
                "city": tournament.city,
                "start_date": tournament.start_date,
                "status": tournament.status,
                "time_control_type": tournament.time_control_type,
                "participant_id": p.id,
                "rating_snapshot": p.rating_snapshot,
                "points": p.points,
                "start_number": p.start_number
            })
            
        return history