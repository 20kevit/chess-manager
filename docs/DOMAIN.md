# Domain Layer Context (Core Chess Logic)

## 1. Responsibility
The `domain/` layer encapsulates the absolute core of the business logic: The Swiss Pairing Engine (FIDE Dutch), Tiebreak Calculations, and Rating Calculations.
This layer is **pure Python**. It represents the rules of chess and tournaments independently of how data is saved or displayed.

## 2. Dependency Direction
Dependencies must strictly point outward from this layer (or rather, nothing depends inward, Domain depends on nothing).

* `infrastructure (DB)` ──X──> `domain (Pure)` <── `application (Services)`
* `domain` ──X──> `infrastructure` (STRICTLY PROHIBITED)
* `domain` ──X──> `application` (STRICTLY PROHIBITED)
* `domain` ──X──> `flask` / `sqlalchemy` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Import `db`, `SQLAlchemy`, or any models from `infrastructure/db_models.py`.
- Import `session`, `request`, or anything from `flask`.
- Use `print()` for debugging in production code (use logging or `ValidationReports`).
- Introduce randomness (`random.choice`, `shuffle`) in the pairing algorithm. FIDE Dutch is 100% deterministic.
- Attempt to mutate input objects directly if they are meant to be immutable Data Classes.

**MUST:**
- Use Python standard library only (e.g., `dataclasses`, `typing`, `enum`, `itertools`).
- Ensure all public functions accept pure Python objects (`PlayerData`, `dict`, `list`) and return pure Python objects (`RoundResult`, `dict`).
- Maintain the strict FIDE rules implementation: Backtracking with exact Bipartite Matching for pruning.

## 4. Module Specifications

### A. Pairing Engine (`domain/pairing/`)
A fully self-contained, deterministic implementation of the FIDE Dutch pairing system (C.04.2 + C.04.3).
- **Entry Points:** `pair_round(players, round_number)` or `SwissEngine(players, round_number).generate()`.
- **Input Contract:** `PlayerData` dataclass (requires `pairing_no`, `color_hist`, `float_hist`, `opponents`).
- **Output Contract:** `RoundResult` containing `PairingCard` objects (includes `white_float` and `black_float` tags for database persistence).
- **Key Constraints Maintained:**
  - *Absolute:* No repeat opponents, Max color balance ±2, No 3 consecutive same colors.
  - *Transpositions/Exchanges:* Handled in exact lexicographic and FIDE-specified order (`transposition.py`, `exchange.py`).

### B. Tiebreak Calculators (`domain/tiebreak/`)
Calculates various tiebreaks based on the player's game history.
- **Entry Point:** `calculate_all(player_data, all_players, tiebreak_list)`.
- **Input Contract:** `PlayerTiebreakData` (includes a list of `GameRecord` objects).
- **Registry:** `TIEBREAK_REGISTRY` holds all supported tiebreaks (e.g., `buchholz_cut1`, `sonneborn_berger`, `arpo`).
- **Rule:** Do not add database queries here to find opponent data. All required data must be passed in the `all_players` dictionary.

### C. Rating Calculators (`domain/rating/`)
Calculates FIDE Elo rating changes and Performance Rating (Rp).
- **Entry Point:** `calculate_tournament_ratings(players)`.
- **Input Contract:** `RatingPlayerData` (includes current rating, k_factor, and list of `RatingGameRecord`).
- **Logic:** Uses standard FIDE Win Expectancy (`win_expectancy`) and DP tables (`_DP_TABLE`).

### D. FIDE Parser (`domain/fide/`)
- **Entry Point:** `parse_fide_html(html_string)`.
- **Logic:** Pure regex/string parsing of FIDE profile pages. Returns `FidePlayerData`. It does not execute HTTP requests (that belongs to infrastructure).

## 5. Error Handling
- Domain functions use standard Python exceptions (`ValueError`) for logical violations (e.g., impossible pairings).
- The pairing engine includes a standalone `ValidationReport` (`validator.py`) to report FIDE rule violations without crashing.

## 6. Testing Requirements
- Because this layer is pure Python, it MUST be heavily tested using standard `unittest` or `pytest` without needing Flask application contexts or Database fixtures.