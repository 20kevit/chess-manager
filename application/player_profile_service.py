# application/player_profile_service.py
from typing import Optional, Dict, List
from infrastructure.repositories import (
    PlayerProfileRepository, 
    FidePlayerRepository, 
    FideRatingRepository, 
    ParticipantRepository, 
    PairingRepository, 
    PairingRepository, 
    ParticipantRepository,
)

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

    @staticmethod
    def get_statistics(profile_id: int) -> Dict:
        """
        Calculates cross-tournament statistics for a player.
        """
        participants = ParticipantRepository.get_all_by_profile_id(profile_id)
        participant_ids = [p.id for p in participants]
        
        pairings = PairingRepository.get_all_games_for_participants(participant_ids)
        
        stats = {
            "tournament_count": len(participants),
            "game_count": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "win_rate": 0.0,
            "score_percentage": 0.0,
            "white_games": 0,
            "white_wins": 0,
            "white_score": 0.0,
            "black_games": 0,
            "black_wins": 0,
            "black_score": 0.0
        }
        
        total_score = 0.0
        valid_results = ["1-0", "0-1", "1/2", "+/-", "-/+", "+/+"]
        
        for p in pairings:
            if p.result not in valid_results:
                continue # Skip byes and unplayed games for W/D/L stats
                
            is_white = (p.white_participant_id in participant_ids)
            is_black = (p.black_participant_id in participant_ids)
            
            if not is_white and not is_black:
                continue
                
            stats["game_count"] += 1
            
            score = 0.0
            if p.result == "1-0":
                if is_white: score = 1.0; stats["wins"] += 1; stats["white_wins"] += 1
                else: score = 0.0; stats["losses"] += 1
            elif p.result == "0-1":
                if is_black: score = 1.0; stats["wins"] += 1; stats["black_wins"] += 1
                else: score = 0.0; stats["losses"] += 1
            elif p.result == "1/2":
                score = 0.5
                stats["draws"] += 1
            elif p.result == "+/-":
                if is_white: score = 1.0; stats["wins"] += 1; stats["white_wins"] += 1
                else: score = 0.0; stats["losses"] += 1
            elif p.result == "-/+":
                if is_black: score = 1.0; stats["wins"] += 1; stats["black_wins"] += 1
                else: score = 0.0; stats["losses"] += 1
            elif p.result == "+/+":
                score = 0.0
                stats["losses"] += 1 # Count double forfeit as loss for both for stats simplicity
                
            total_score += score
            
            if is_white:
                stats["white_games"] += 1
                stats["white_score"] += score
            elif is_black:
                stats["black_games"] += 1
                stats["black_score"] += score
                
        if stats["game_count"] > 0:
            stats["win_rate"] = round((stats["wins"] / stats["game_count"]) * 100, 1)
            stats["score_percentage"] = round((total_score / stats["game_count"]) * 100, 1)
            
        return stats

    @staticmethod
    def get_game_history(profile_id: int) -> List[Dict]:
        """
        Fetches and formats the complete game history for a player profile.
        """
        participants = ParticipantRepository.get_all_by_profile_id(profile_id)
        participant_ids = [p.id for p in participants]
        
        # Create a map to quickly find tournament info for each pairing
        tournament_map = {p.tournament_id: p.tournament for p in participants}
        
        pairings = PairingRepository.get_all_games_for_participants(participant_ids)
        
        games = []
        for p in pairings:
            is_white = p.white_participant_id in participant_ids
            is_black = p.black_participant_id in participant_ids
            
            if not is_white and not is_black:
                continue
                
            opponent = None
            player_color = ""
            score = None
            
            if is_white:
                player_color = "white"
                opponent = p.black_participant
                if p.result == "1-0" or p.result == "+/-": score = 1.0
                elif p.result == "1/2": score = 0.5
                elif p.result == "0-1" or p.result == "-/+" or p.result == "+/+": score = 0.0
            elif is_black:
                player_color = "black"
                opponent = p.white_participant
                if p.result == "0-1" or p.result == "-/+": score = 1.0
                elif p.result == "1/2": score = 0.5
                elif p.result == "1-0" or p.result == "+/-" or p.result == "+/+": score = 0.0
                
            games.append({
                "tournament_name": tournament_map.get(p.tournament_id).name if tournament_map.get(p.tournament_id) else "Unknown",
                "round_number": p.round.round_number if p.round else 0,
                "board_number": p.board_number,
                "color": player_color,
                "result": p.result,
                "score": score,
                "opponent_name": opponent.full_name if opponent else "Bye/Forfeit",
                "opponent_rating": opponent.rating_snapshot if opponent else 0,
                "opponent_id": opponent.player_profile_id if opponent else None
            })
            
        return games