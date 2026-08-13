# Application Layer — Agent Context

## Purpose
Orchestrates use-cases. Bridges domain logic with infrastructure.
Owns transaction boundaries (commits happen here).

## Files
- round_service.py — Round lifecycle, pairing orchestration
- tournament_service.py — Tournament CRUD, standings, rating changes
- player_service.py — Player CRUD, FIDE lookup

## Key Function: _build_snapshots()
In round_service.py. Converts DB data to PlayerSnapshot for pairing engine.
Populates: points, color_balance, last_color, played_against,
received_bye, float history (downfloat/upfloat tracking).

## Key Function: _build_tiebreak_data()
In tournament_service.py. Converts DB data to PlayerTiebreakData.
Uses round_id → round_number lookup for correct ordering.
Uses player.rating property for correct rating type.

## Transaction Pattern
- Repositories flush()
- Services commit()
- If operation fails, data is not partially committed

## Dependencies
- domain/pairing/ (SwissEngine)
- domain/tiebreak/ (calculate_all)
- domain/rating/ (calculate_tournament_ratings)
- infrastructure/ (repositories, db_models)
- app/extensions (db.session for commit)