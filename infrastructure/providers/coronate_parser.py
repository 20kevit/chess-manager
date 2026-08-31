"""
Parsing logic for Coronate JSON format.
"""
import json
from typing import Optional
from application.import_export_interface import (
    TournamentData, PlayerImportExportData, PairingImportExportData, BackupFileData
)


class CoronateFormatError(Exception):
    """Custom exception for invalid Coronate format."""
    pass


def _map_coronate_result_to_internal(result: str, black_id: Optional[str]) -> str:
    """
    Map Coronate result strings to internal 9 result types.

    Coronate only supports: whiteWon, blackWon, draw.
    For byes, blackId is " DUMMY ".

    LIMITATION: This mapping is intentionally lossy. Forfeit results
    ("+/-", "-/+") collapse to "1-0"/"0-1" and double-forfeit "+/+"
    collapses to "bye" on import. Callers must not assume lossless
    round-trip of the 9-type vocabulary via Coronate. See
    docs/INFRASTRUCTURE.md §6 for the full contract.
    """
    is_bye = black_id == " DUMMY "
    
    if is_bye:
        # Map bye variants
        if result == "whiteWon":
            return "bye"
        elif result == "draw":
            return "half-bye"
        elif result == "blackWon":
            return "zero-bye"
    
    # Normal game mapping
    if result == "whiteWon":
        return "1-0"
    elif result == "blackWon":
        return "0-1"
    elif result == "draw":
        return "1/2"
    
    raise CoronateFormatError(f"Unknown result type: {result}")


def parse_coronate_json(file_content: str) -> BackupFileData:
    """
    Parse Coronate JSON string into BackupFileData containing multiple tournaments.
    
    Each tournament in the JSON is parsed separately with its own players and rounds.
    Players are filtered based on playerIds in each tournament.
    """
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError as e:
        raise CoronateFormatError(f"Invalid JSON format: {e}")

    if "tournaments" not in data or "players" not in data:
        raise CoronateFormatError("Missing 'tournaments' or 'players' in Coronate JSON")

    all_players_data = data["players"]
    config = data.get("config", {})
    
    # Parse all tournaments
    tournaments = []
    
    for tournament_key, t_data in data["tournaments"].items():
        # Get player IDs for this tournament
        tournament_player_ids = set(t_data.get("playerIds", []))
        
        # Parse players for this tournament only
        players = []
        coronate_id_to_internal = {}  # Maps Coronate ID to internal identifier
        
        for p_id in tournament_player_ids:
            if p_id not in all_players_data:
                continue  # Skip if player not found in global players dict
            
            p_info = all_players_data[p_id]
            
            # Extract fide_id if available
            fide_id = p_info.get("fideId") or p_info.get("fide_id")
            
            # Use fide_id as identifier if available, otherwise use name-based identifier
            if fide_id:
                identifier = fide_id
            else:
                # Create a stable identifier from name for matching during import
                identifier = f"{p_info.get('firstName', '')}_{p_info.get('lastName', '')}"
            
            coronate_id_to_internal[p_id] = identifier
            
            players.append(PlayerImportExportData(
                identifier=identifier,
                first_name=p_info.get("firstName", ""),
                last_name=p_info.get("lastName", ""),
                rating=int(p_info.get("rating", 0) or 0),
                fide_id=fide_id,
                federation=p_info.get("federation", "IRI"),
                gender=p_info.get("gender", "M")
            ))
        
        # Parse rounds and pairings for this tournament
        rounds = []
        round_list = t_data.get("roundList", [])
        
        for round_idx, round_pairings in enumerate(round_list, start=1):
            current_round_pairings = []
            for board_idx, match in enumerate(round_pairings, start=1):
                white_id = match.get("whiteId")
                black_id = match.get("blackId")
                result = match.get("result", "draw")
                
                # Map Coronate IDs to internal identifiers
                white_identifier = coronate_id_to_internal.get(white_id, white_id)
                black_identifier = coronate_id_to_internal.get(black_id, black_id) if black_id else None
                
                # Map result to internal format
                internal_result = _map_coronate_result_to_internal(result, black_id)
                
                current_round_pairings.append(PairingImportExportData(
                    round_number=round_idx,
                    board_number=board_idx,
                    white_identifier=white_identifier,
                    black_identifier=black_identifier,
                    result=internal_result,
                    white_orig_rating=int(match.get("whiteOrigRating", 0) or 0),
                    black_orig_rating=int(match.get("blackOrigRating", 0) or 0)
                ))
            rounds.append(current_round_pairings)
        
        # Map tiebreaks from Coronate names to internal names
        tb_mapping = {
            "median": "median_system",
            "solkoff": "solkoff",
            "cumulative": "cumulative",
            "cumulativeOfOpposition": "cumulative_progressive_scores_of_opponents"
        }
        raw_tiebreaks = t_data.get("tieBreaks", [])
        mapped_tiebreaks = [tb_mapping.get(tb, tb) for tb in raw_tiebreaks]
        
        # Extract avoid pairs (not used in this version, but preserved for future)
        avoid_pairs = config.get("avoidPairs", [])
        
        # Create TournamentData for this tournament
        tournament_data = TournamentData(
            internal_id=tournament_key,  # Use the key from JSON as internal_id
            name=t_data.get("name", "Imported Tournament"),
            players=players,
            rounds=rounds,
            tiebreaks=mapped_tiebreaks,
            avoid_pairs=avoid_pairs,
            total_rounds=len(rounds) if rounds else 5,
            time_control_type="standard"  # Default, can be updated by service
        )
        
        tournaments.append(tournament_data)
    
    return BackupFileData(tournaments=tournaments)