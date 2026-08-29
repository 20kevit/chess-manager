# Infrastructure Layer Context

## 1. Responsibility
The `infrastructure/` layer encapsulates all external I/O operations. It is solely responsible for database persistence (SQLAlchemy models and Repositories), calling external HTTP APIs (FIDE client, payment gateway), and handling file format conversions (Coronate).

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

## 4. Database Models (`infrastructure/models/`)

Models are organized into domain-specific modules under `infrastructure/models/`. Each module contains related models. Models MUST contain only persistence mapping, foreign keys, and trivial presentation-only properties (e.g., formatting names or scores). They MUST NOT contain domain state transitions or FIDE logic.

**Model Modules:**

| Module | Models |
|--------|--------|
| `models/user.py` | `UserModel`, `UserRoleModel` |
| `models/profile.py` | `PlayerProfileModel` |
| `models/tournament.py` | `TournamentModel`, `RoundModel`, `PairingModel`, `ByeRequestModel`, `ManualPairingModel` |
| `models/participant.py` | `TournamentParticipantModel` |
| `models/registration.py` | `RegistrationModel`, `PaymentModel`, `PromoCodeModel` |
| `models/staff.py` | `TournamentStaffModel` |
| `models/fide.py` | `FidePlayerModel`, `FideRatingModel`, `FideImportModel` |
| `models/verification.py` | `PlayerVerificationModel` |
| `models/notification.py` | `NotificationModel`, `NotificationPreferenceModel` |
| `models/prize.py` | `TournamentPrizeModel`, `PrizeAllocationModel` |
| `models/temp.py` | `TempImportDataModel` |

**Key Model Notes:**
- `TournamentParticipantModel` stores snapshots at registration time: `start_number` (registration order, secondary tiebreak), `pairing_no` (official FIDE ranking number, fixed at Round 1 creation), and incremental fields: `points`, `color_history`, `float_history`, `received_bye`.
- `PairingModel` stores board pairings, engine float tags (`white_float`, `black_float`), and `result` (using internal 9-state formats).
- Models MUST NOT contain domain state transitions or FIDE logic.

## 5. Repository Contract (`infrastructure/repositories/`)

Repositories are organized into domain-specific modules under `infrastructure/repositories/`. Repositories are dumb data-access objects that use `db.session.flush()` for ID retrieval and never call `commit()` or `rollback()`.

**Repository Modules:**

| Module | Repositories |
|--------|--------------|
| `repositories/user.py` | `UserRepository` |
| `repositories/profile.py` | `PlayerProfileRepository` |
| `repositories/tournament.py` | `TournamentRepository`, `RoundRepository`, `PairingRepository`, `ManualPairingRepository` |
| `repositories/participant.py` | `ParticipantRepository` |
| `repositories/registration.py` | `RegistrationRepository`, `PromoCodeRepository`, `PaymentRepository` |
| `repositories/staff.py` | `TournamentStaffRepository` |
| `repositories/fide.py` | `FidePlayerRepository`, `FideRatingRepository`, `FideImportRepository` |
| `repositories/verification.py` | `PlayerVerificationRepository` |
| `repositories/notification.py` | `NotificationRepository`, `NotificationPreferenceRepository` |

**Repository Contract:**
- **Incremental Priority:** Normal tournament progress updates players *incrementally* via `RoundService`.
- **Legacy Fallback:** `ParticipantRepository.update_points()` is a legacy/repair operation. It recalculates all points from scratch. It MUST NOT be used in the normal round-processing workflow.
- **Flush Only:** Repositories use `db.session.flush()` only. Transaction lifecycle (`commit`, `rollback`) is owned by the Application/Service layer.
- **Exceptions:** Repositories MUST NOT silently swallow database exceptions. Persistence exceptions must propagate to the Application layer.

## 6. External Providers & Integrations

External clients handle data transformation only. They must not make business decisions or save directly to the database.

**FIDE Storage (`infrastructure/fide/storage.py`):**
- Strictly an HTTP downloader (monthly rating-list XML) plus file storage/retention.
- Parsing lives in `domain/fide/parser.py`. Neither updates player/participant models directly.

**Payment Gateway (`infrastructure/gateways/zarinpal_gateway.py`):**
- Implements `PaymentGatewayInterface` for Zarinpal (sandbox/production).
- Handles payment request/verify flows. Toman → Rial ×10 conversion is handled here.

**Coronate Provider (`infrastructure/providers/`):**
- `coronate_provider.py` — facade combining parser + generator.
- `coronate_parser.py` — parses Coronate JSON format to internal `BackupFileData`.
- `coronate_generator.py` — generates Coronate JSON from internal `BackupFileData`.

**Strict Result Mapping Contract (Coronate):**

| Internal Result | Coronate Result | Coronate Opponent |
|-----------------|-----------------|-------------------|
| `1-0`, `+/-`    | `whiteWon`      | Actual ID         |
| `0-1`, `-/+`    | `blackWon`      | Actual ID         |
| `1/2`           | `draw`          | Actual ID         |
| `bye`           | `whiteWon`      | `" DUMMY "`       |
| `half-bye`      | `draw`          | `" DUMMY "`       |
| `zero-bye`      | `blackWon`      | `" DUMMY "`       |
| `+/+` (Double F)| `whiteWon` (Fallback)| `" DUMMY "` |

**File Storage (`infrastructure/file_storage.py`):**
- Private file storage for receipts, profile photos, ID documents, rulebook PDFs.
- Files live under instance-anchored directories, never under `static/`.
- Filenames are server-generated via `secure_filename`; user-supplied filenames are discarded.
- Image content verified by magic bytes; stored values are bare filenames.
- Path traversal impossible: resolution uses `os.path.basename` only.

## 7. Infrastructure ↔ Other Layers

| Layer | Relationship |
|-------|--------------|
| `domain/` | Infrastructure imports domain types (e.g., `domain.fide.parser` used by FIDE storage). Domain MUST NOT import infrastructure. |
| `application/` | Application services call repositories and external integrations. Application owns transactions (`commit`/`rollback`). |
| `interfaces/web/` | Web layer calls application services. Web layer MUST NOT import models/repositories directly (use application services). |

## 8. Rules for Adding New Models

1. **Place in correct domain module** under `infrastructure/models/` (e.g., `tournament.py`, `registration.py`). Create new file if no suitable domain exists.
2. **Follow existing patterns:** inherit from `db.Model`, use `__table_args__` with `mysql_charset/collate`, define `__tablename__`.
3. **No business logic:** Only persistence mapping, foreign keys, trivial properties (e.g., `full_name` property).
4. **Add to `models/__init__.py`** exports and `infrastructure/__init__.py` exports.
5. **Create corresponding repository** in matching `repositories/` module.
6. **Run tests** to verify no regressions.

## 9. Rules for Adding New Repositories

1. **Place in correct domain module** under `infrastructure/repositories/` matching the model's domain.
2. **Follow existing patterns:** static methods, `db.session.flush()` only, no `commit`/`rollback`.
3. **Type hints:** Use proper type annotations for parameters and returns.
4. **Add to `repositories/__init__.py`** exports and `infrastructure/__init__.py` exports.
6. **Run tests** to verify no regressions.

## 10. Rules for External Integrations/Gateways/Providers

- **Place in appropriate subdirectory:** `fide/` for FIDE-related, `gateways/` for payment gateways, `providers/` for import/export formats.
- **Implement interfaces** defined in `application/` (e.g., `PaymentGatewayInterface`).
- **No database writes** in external integrations. Data transformation only.
- **Parsing logic** belongs in `domain/` (e.g., `domain/fide/parser.py`), not in infrastructure.
- **Configuration** via environment variables / `config.py`, never hardcoded.

## 11. Important Architectural Constraints

**DO NOT place in infrastructure:**
- Swiss pairing logic, tiebreak calculations, rating algorithms → belongs in `domain/pairing/`, `domain/tiebreak/`, `domain/rating/`
- Business rule enforcement → belongs in `application/` services
- Web framework specifics (Flask `request`, `session`) → belongs in `interfaces/web/`
- Transaction management (`commit`, `rollback`) → belongs in `application/` services

**Model/Repository Constraints:**
- Models: no domain logic, no `commit`, no Flask imports
- Repositories: `flush` only, no `commit`/`rollback`, no business rules
- External integrations: read-only data transformation, no direct DB writes

## 12. Expected Import Style

```python
# Models — import from domain-specific modules
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.tournament import TournamentModel, RoundModel
from infrastructure.models.participant import TournamentParticipantModel

# Repositories — import from domain-specific modules
from infrastructure.repositories.tournament import TournamentRepository, RoundRepository
from infrastructure.repositories.participant import ParticipantRepository

# Infrastructure utilities — import from root or specific modules
from infrastructure.file_storage import save_image, resolve_private_file
from infrastructure.fide.storage import FideStorageManager, ensure_players_xml
from infrastructure.gateways.zarinpal_gateway import ZarinpalGateway
from infrastructure.providers.coronate_provider import CoronateProvider

# For tests/convenience, infrastructure root exports everything:
from infrastructure import UserModel, TournamentRepository, save_image, ZarinpalGateway
```

## 13. Why This Structure?

The infrastructure layer was refactored from two monolithic files (`db_models.py`, `repositories.py`) into domain-organized packages to:

- **Improve navigation:** Related models/repositories are colocated by domain.
- **Enable parallel work:** Teams can work on different domains without conflicts.
- **Enforce boundaries:** Clear separation between domains (tournament, registration, FIDE, etc.).
- **Reduce coupling:** Consumers import only what they need (`from infrastructure.models.tournament import TournamentModel` vs importing entire monolith).
- **Scalability:** New domains can be added as new files without bloating a single file.
- **Maintainability:** Smaller files are easier to review, test, and understand.

The structure follows Clean Architecture: infrastructure is the outer layer providing implementations for interfaces defined in application/domain layers, with strict inward dependency direction.

---

*Documentation updated to reflect the post-refactor architecture (models/ and repositories/ packages).*