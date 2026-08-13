# Application Layer Context (Services & Use-Cases)

## 1. Responsibility
The `application/` layer orchestrates business use-cases. It acts as the bridge between the Web/UI layer and the Domain/Infrastructure layers.
This layer is **the exclusive owner of database transactions**. It retrieves data via Repositories, passes it to the Domain layer for pure calculations, and then persists the results.

## 2. Dependency Direction
Dependencies must strictly point inward toward the Domain and Infrastructure layers.

* `interfaces (Web)` ──> `application (Services)` ──> `domain (Pure)`
* `interfaces (Web)` ──> `application (Services)` ──> `infrastructure (DB)`
* `application` ──X──> `interfaces` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Import anything from `interfaces/web/` (e.g., `request`, `session`, `render_template`).
- Re-implement Swiss pairing, tiebreak, or rating logic here. Always delegate to the `domain/` layer.
- Access raw database query methods directly (e.g., `PlayerModel.query.filter`). Always use methods provided by `infrastructure/repositories.py`.
- Write raw SQL or execute DB migrations in this layer.

**MUST:**
- **Own the Transaction:** Call `db.session.commit()` or `db.session.rollback()` at the end of a successful or failed use-case.
- Use incremental updates where possible (e.g., `RoundService._update_player_stats_incremental()`) to maintain performance, rather than recalculating the entire tournament history every round.
- Use `db.session.flush()` before querying freshly inserted objects within the same transaction.
- Use the `@staticmethod` pattern for service classes, as they are stateless orchestrators.

## 4. Module Specifications

### A. Round Service (`round_service.py`)
Manages the lifecycle of rounds and pairings.
- **Key Responsibilities:** Creating rounds, finalizing rounds, handling manual pairings (locks), and post-pairing swaps.
- **Incremental Architecture:** On `finish_round()`, it updates `PlayerModel.points`, `color_history`, and `float_history` incrementally via `_update_player_stats_incremental()`.
- **Ranking Lock:** Ensures FIDE ranking numbers (`pairing_no`) are permanently locked when Round 1 is created via `_initialize_pairing_numbers()`.
- **Fallback Mechanism:** If a round is deleted, it triggers `_full_refresh_stats()` to safely rebuild all incremental data from scratch.

### B. Tournament Service (`tournament_service.py`)
Handles tournament configuration and the generation of standings.
- **Standings Generation:** Fetches tiebreak models and delegates to `domain.tiebreak.calculate_all`. 
- **Sorting Logic:** 
  - If Round == 0: Sorts strictly by `Rating DESC`, then `Start Number ASC`.
  - If Round > 0: Sorts by `Points DESC`, then `Tiebreaks DESC`, then `Pairing Number (Rank) ASC`.
- **Rating Update:** Builds payload for `domain.rating` to calculate Elo changes and Performance (Rp) for the leaderboard.

### C. Player Service (`player_service.py`)
Handles player registration and management.
- **Age Category Detection:** Automatically assigns U08-U20 or S50/S65 categories based on birthdate if not explicitly provided.
- **FIDE Integration:** Calls `infrastructure.fide_client` to scrape HTML, passes it to `domain.fide.parse_fide_html`, and returns structured JSON to the frontend.

### D. Import/Export Service (`import_export_service.py`)
Orchestrates moving data in and out of the system.
- **Provider/Adapter Pattern:** Uses `application.provider_registry` to dynamically find the correct format parser (e.g., Coronate).
- **Atomic Operations:** Wraps entire imports in a single `db.session` to ensure partial failures trigger a full rollback.
- **ID Matching:** When importing, attempts to match players first by `fide_id`, then by `first_name + last_name` to prevent duplicates.

## 5. Error Handling
- Service methods MUST raise standard Python exceptions (e.g., `ValueError`, `SwapError`, `ManualPairingError`) with clear, user-friendly messages.
- The `interfaces/web` layer is responsible for catching these exceptions and displaying them via Flask `flash()`.

## 6. Testing Requirements
- Service layer tests must use the in-memory SQLite database fixture.
- Tests should verify state changes (e.g., does calling `create_next_round` actually reduce the number of active `ByeRequests`?).