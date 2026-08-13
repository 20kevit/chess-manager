# Infrastructure Layer Context

## 1. Responsibility
The `infrastructure/` layer encapsulates all external I/O operations. It is solely responsible for database persistence (SQLAlchemy models and Repositories), calling external HTTP APIs (FIDE client), and handling file format conversions (Coronate).

## 2. Dependency Direction
Dependencies must strictly point inward toward the Application and Domain layers.

* `interfaces (Web)` ──> `application (Services)` ──> `infrastructure (DB/APIs)`
* `infrastructure` ──X──> `interfaces` (STRICTLY PROHIBITED)
* `infrastructure` ──X──> `application` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Implement any Swiss pairing logic, tiebreak calculations, or rating algorithms.
- Call `db.session.commit()` or `db.session.rollback()`.
- Access or import Flask `session`, `request`, or any web-specific state.
- Swallow database exceptions silently using empty `except` blocks.
- Modify domain state based on business rules inside repositories.

**MUST:**
- Delegate the entire transaction lifecycle (`commit`, `rollback`) exclusively to the Application/Service layer.
- Use `db.session.flush()` inside Repositories to get inserted IDs without committing.
- Propagate persistence exceptions (e.g., `SQLAlchemyError`) upward to the Application layer.
- Keep external API parsers completely isolated from database writes.

## 4. Database Models (`db_models.py`)
Models MUST contain only persistence mapping, foreign keys, and trivial presentation-only properties (e.g., formatting names or scores). They MUST NOT contain domain state transitions or FIDE logic.

- **TournamentModel:** Stores settings and `admin_code`. (Note: Checking this code against the web session happens in `interfaces/web/admin_auth.py`, NOT here).
- **PlayerModel:** 
  - `start_number`: Registration order (used as secondary tiebreak).
  - `pairing_no`: The official FIDE ranking number. Fixed at Round 1 creation.
  - *Incremental Fields:* `points`, `color_history`, `float_history`, `received_bye`.
- **PairingModel:** Stores board pairings, engine float tags (`white_float`, `black_float`), and `result` (using internal 9-state formats).

## 5. Repository Contract (`repositories.py`)
Repositories are dumb data-access objects.
- **Incremental Priority:** Normal tournament progress updates players *incrementally* via `RoundService`.
- **Legacy Fallback:** `PlayerRepository.update_points()` is a legacy/repair operation. It recalculates all points from scratch. It MUST NOT be used in the normal round-processing workflow.

## 6. External Providers Isolation
External clients handle data transformation only. They must not make business decisions or save directly to the database.

**FIDE Client (`fide_client.py`):**
- Strictly an HTTP scraper. Returns raw HTML or basic dicts. MUST NOT update `PlayerModel` directly.

**Coronate Provider (`providers/`):**
- Converts between internal entities and Coronate JSON format.
- **Strict Result Mapping Contract:**

| Internal Result | Coronate Result | Coronate Opponent |
|-----------------|-----------------|-------------------|
| `1-0`, `+/-`    | `whiteWon`      | Actual ID         |
| `0-1`, `-/+`    | `blackWon`      | Actual ID         |
| `1/2`           | `draw`          | Actual ID         |
| `bye`           | `whiteWon`      | `" DUMMY "`       |
| `half-bye`      | `draw`          | `" DUMMY "`       |
| `zero-bye`      | `blackWon`      | `" DUMMY "`       |
| `+/+` (Double F)| `whiteWon` (Fallback)| `" DUMMY "` |

## 7. Error Handling
Repositories MUST NOT silently swallow database exceptions. Persistence exceptions must propagate to the Application layer where transaction rollbacks can be properly orchestrated.

## 8. Testing Requirements
- Infrastructure tests MUST NOT depend on the production database.
- Use isolated in-memory SQLite or a dedicated test database container.
- Test external providers (like Coronate format mapping) exhaustively using mock data.