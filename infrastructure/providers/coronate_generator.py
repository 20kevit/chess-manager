"""
Generation logic for Coronate JSON format.
"""
import json
import re
import secrets
import string
from datetime import datetime
from typing import Dict, Any
from application.import_export_interface import BackupFileData


def _generate_random_id(length: int = 21) -> str:
    """Generate a random string ID similar to Coronate format."""
    chars = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(chars) for _ in range(length))


def _sanitize_name(name: str) -> str:
    """Sanitize player name for ID generation."""
    sanitized = re.sub(r'[^a-zA-Z0-9]', '', name)
    return sanitized or "Unknown"


def _map_internal_result_to_coronate(result: str) -> Dict[str, Any]:
    """
    Map internal 9 result types to Coronate format.

    Coronate only supports: whiteWon, blackWon, draw.
    For byes, blackId is " DUMMY ".

    LIMITATION: "+/-" and "-/+" collapse to "1-0"/"0-1" (no forfeit
    distinction) and "+/+" collapses to "bye" (DUMMY whiteWon). This is
    lossy by design — Coronate has no forfeit vocabulary. Export is not
    a lossless backup of the 9-type vocabulary; see docs/INFRASTRUCTURE.md §6.
    """
    if result == "1-0" or result == "+/-":
        return {"result": "whiteWon", "is_bye": False}
    elif result == "0-1" or result == "-/+":
        return {"result": "blackWon", "is_bye": False}
    elif result == "1/2":
        return {"result": "draw", "is_bye": False}
    elif result == "+/+":
        # NOTE: Coronate does not support double forfeit (+/+).
        # We map it to a bye (whiteWon with DUMMY opponent) as a workaround.
        return {"result": "whiteWon", "is_bye": True}
    elif result == "bye":
        return {"result": "whiteWon", "is_bye": True}
    elif result == "half-bye":
        return {"result": "draw", "is_bye": True}
    elif result == "zero-bye":
        return {"result": "blackWon", "is_bye": True}
    
    # Fallback for unknown results
    return {"result": "draw", "is_bye": False}


def generate_coronate_json(backup_data: BackupFileData) -> str:
    """
    Generate Coronate JSON string from BackupFileData containing multiple tournaments.
    
    Each tournament in BackupFileData is converted to a separate entry in the JSON.
    """
    # Build global player dict (all players from all tournaments)
    players_dict = {}
    internal_to_coronate_id = {}  # Maps internal identifier to Coronate ID
    
    # Collect all unique players across all tournaments
    all_players = []
    for tournament in backup_data.tournaments:
        all_players.extend(tournament.players)
    
    # Remove duplicates based on identifier
    seen_identifiers = set()
    unique_players = []
    for p in all_players:
        if p.identifier not in seen_identifiers:
            seen_identifiers.add(p.identifier)
            unique_players.append(p)
    
    # Build player dict with Coronate-style IDs
    for p in unique_players:
        # Generate Coronate-style ID: FirstNameLastName_randomString
        first_sanitized = _sanitize_name(p.first_name)
        last_sanitized = _sanitize_name(p.last_name)
        random_suffix = _generate_random_id(10)
        coronate_player_id = f"{first_sanitized}{last_sanitized}_{random_suffix}"
        
        internal_to_coronate_id[p.identifier] = coronate_player_id
        
        # Count matches for this player
        match_count = 0
        for tournament in backup_data.tournaments:
            for round_pairings in tournament.rounds:
                for pairing in round_pairings:
                    if pairing.white_identifier == p.identifier or pairing.black_identifier == p.identifier:
                        match_count += 1
        
        player_data = {
            "firstName": p.first_name,
            "lastName": p.last_name,
            "id": coronate_player_id,
            "rating": p.rating,
            "type_": "person",
            "matchCount": match_count
        }
        
        # Add fide_id if available
        if p.fide_id:
            player_data["fideId"] = p.fide_id
        
        players_dict[coronate_player_id] = player_data
    
    # Build tournaments dict
    tournaments_dict = {}
    
    for tournament in backup_data.tournaments:
        # Generate Coronate-style tournament ID
        tournament_key = _generate_random_id(21)
        
        # Map tiebreaks to Coronate format
        # Coronate uses: median, solkoff, cumulative, cumulativeOfOpposition
        coronate_tiebreaks = ["median", "solkoff", "cumulative", "cumulativeOfOpposition"]
        
        # Build round list for this tournament
        round_list = []
        for round_idx, round_pairings in enumerate(tournament.rounds, start=1):
            current_round = []
            for pairing in round_pairings:
                mapped = _map_internal_result_to_coronate(pairing.result)
                
                # Map internal identifiers to Coronate IDs
                white_cor_id = internal_to_coronate_id.get(pairing.white_identifier, pairing.white_identifier)
                
                if pairing.black_identifier:
                    black_cor_id = internal_to_coronate_id.get(pairing.black_identifier, pairing.black_identifier)
                else:
                    # For byes, use " DUMMY " as black opponent
                    black_cor_id = " DUMMY " if mapped["is_bye"] else None
                
                # Generate Coronate-style match ID
                match_id = _generate_random_id(21)
                
                current_round.append({
                    "id": match_id,
                    "whiteId": white_cor_id,
                    "blackId": black_cor_id,
                    "whiteOrigRating": pairing.white_orig_rating,
                    "blackOrigRating": pairing.black_orig_rating,
                    "whiteNewRating": pairing.white_orig_rating,
                    "blackNewRating": pairing.black_orig_rating,
                    "result": mapped["result"]
                })
            round_list.append(current_round)
        
        # Get player IDs for this tournament
        tournament_player_ids = [
            internal_to_coronate_id.get(p.identifier, p.identifier)
            for p in tournament.players
        ]
        
        # Build tournament entry
        tournaments_dict[tournament_key] = {
            "id": tournament_key,
            "name": tournament.name,
            "date": datetime.utcnow().isoformat() + "Z",
            "playerIds": tournament_player_ids,
            "byeQueue": [],
            "tieBreaks": coronate_tiebreaks,
            "roundList": round_list,
            "scoreAdjustments": []
        }
    
    # Construct final Coronate structure
    output = {
        "config": {
            "avoidPairs": backup_data.tournaments[0].avoid_pairs if backup_data.tournaments else [],
            "byeValue": 1,
            "lastBackup": datetime.utcnow().isoformat() + "Z",
            "whiteAlias": None,
            "blackAlias": None
        },
        "players": players_dict,
        "tournaments": tournaments_dict
    }
    
    return json.dumps(output, indent=2, ensure_ascii=False)