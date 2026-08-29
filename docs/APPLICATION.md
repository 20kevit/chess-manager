# Application Layer Architecture

## 1. Responsibility

The `application/` layer orchestrates business use-cases. It acts as the bridge between the Web/UI layer and the Domain/Infrastructure layers.

This layer is **the exclusive owner of database transactions**. It retrieves data via Repositories, passes it to the Domain layer for pure calculations, and then persists the results.

## 2. Dependency Direction

Dependencies must strictly point inward toward the Domain and Infrastructure layers.

```
interfaces (Web)  ──>  application (Services)  ──>  domain (Pure)
interfaces (Web)  ──>  application (Services)  ──>  infrastructure (DB)
application  ──X──>  interfaces  (STRICTLY PROHIBITED)
```

No application module may import from `interfaces/web/`.

## 3. Package Tree

```
application/
├── __init__.py                          # Central re-export hub (all package-level names)
│
│  ── Legacy Facade Modules (backward-compatible imports) ──
├── admin_service.py                     # Facade → application.admin
├── auth_service.py                      # Facade → application.auth
├── tournament_service.py                # Facade → application.tournament
├── registration_service.py              # Facade → application.registration
├── player_service.py                    # Facade → application.player
├── payment_service.py                   # Facade → application.payment
├── verification_service.py              # Facade → application.verification
├── fide_import_service.py               # Facade → application.fide
├── fide_search_service.py               # Facade → application.fide
├── import_export_service.py             # Facade → application.import_export
├── prize_service.py                     # Facade → application.prize
├── round_service.py                     # Facade → application.round
├── telegram_service.py                  # Facade → application.telegram
├── bale_service.py                      # Facade → application.bale
│
│  ── Standalone Modules (no package, kept as-is) ──
├── notification_service.py              # Core notification CRUD + dispatch trigger
├── notification_dispatcher.py           # Dispatches to registered providers
├── notification_types.py                # NotificationType enum
├── notification_policy.py               # Tournament-level notification gates
├── notification_provider_interface.py   # Abstract provider contract
├── payment_gateway_interface.py         # Abstract gateway contract
├── import_export_interface.py           # Abstract I/E provider contract
├── provider_registry.py                 # Provider lookup registry
├── player_profile_service.py            # Profile data + FIDE info orchestration
│
│  ── Domain-Organized Packages ──
├── admin/
│   ├── __init__.py
│   ├── dashboard_stats_service.py       # Admin dashboard statistics
│   ├── system_health_service.py         # System health checks
│   ├── user_management_service.py       # User CRUD & role management
│   └── tournament_admin_service.py      # Tournament-level admin ops
│
├── auth/
│   ├── __init__.py
│   ├── authentication_service.py        # Register / authenticate
│   ├── profile_creation_service.py      # Create player profile for user
│   └── profile_linking_service.py       # Link profile to user account
│
├── tournament/
│   ├── __init__.py
│   ├── tournament_config_service.py     # Basic settings (identity, competition, tiebreaks)
│   ├── tournament_pricing_service.py    # Pricing, discounts, bank/payment, rulebook
│   ├── tournament_registration_rules_service.py  # Entry requirements (eligibility rules)
│   ├── tournament_rulebook_service.py   # Rulebook text/sections/PDF
│   ├── tournament_admin_service.py      # Tournament admin operations
│   └── standings_service.py             # Standings & tiebreak computation
│
├── round/
│   ├── __init__.py
│   ├── round_lifecycle_service.py       # create_next_round / finish_round / delete_round
│   ├── pairing_generation_service.py    # Swiss engine invocation, pairing persistence
│   ├── result_recording_service.py      # Save results, finish round
│   ├── manual_adjustment_service.py     # Color swaps, player swaps, manual locks, byes
│   ├── stats_rebuild_service.py         # Full Swiss state reconstruction
│   └── round_notification_service.py    # Notification fan-out for round events
│
├── registration/
│   ├── __init__.py
│   ├── registration_creator.py          # Create registration with eligibility + pricing
│   ├── eligibility_checker.py           # Tournament eligibility enforcement
│   ├── pricing_calculator.py            # Price computation with discounts
│   ├── registration_approver.py         # Approve registration → participant
│   └── receipt_handler.py              # Bank transfer receipt lifecycle
│
├── player/
│   ├── __init__.py
│   ├── participant_management.py        # Create / update / withdraw / delete participants
│   └── fide_rating_fetcher.py           # Auto-fetch FIDE rating for snapshot
│
├── verification/
│   ├── __init__.py
│   ├── verification_request_service.py  # Submit / list pending requests
│   ├── verification_approver.py         # Approve / reject verification
│   └── verification_status_updater.py   # Per-aspect verification updates
│
├── fide/
│   ├── __init__.py
│   ├── fide_import_orchestrator.py      # Full FIDE XML import pipeline
│   └── fide_search_service.py           # Search local FIDE database
│
├── import_export/
│   ├── __init__.py
│   ├── export_service.py                # Export tournament to provider format
│   ├── import_service.py                # Import tournament from provider format
│   └── preview_service.py              # Preview backup file contents
│
├── prize/
│   ├── __init__.py
│   ├── prize_definition_service.py      # Prize CRUD
│   ├── prize_allocation_service.py      # Deterministic allocation over standings
│   └── prize_summary_service.py         # Public prize summary DTO
│
├── payment/
│   ├── __init__.py
│   └── payment_initiator.py             # Initiate Zarinpal payment
│
├── telegram/
│   ├── __init__.py
│   ├── telegram_service.py              # Telegram bot API (send, link, generate token)
│   └── telegram_link_service.py         # Telegram account linking workflow
│
├── bale/
│   ├── __init__.py
│   ├── bale_service.py                  # Bale bot API (send, link, generate token)
│   └── bale_link_service.py             # Bale account linking workflow
│
└── providers/
    ├── web_provider.py                  # Web in-app notification provider
    ├── telegram_provider.py             # Telegram message provider
    ├── bale_provider.py                 # Bale message provider
    ├── coronate_provider.py             # Coronate import/export format
    ├── coronate_parser.py               # Coronate JSON parser
    └── coronate_generator.py            # Coronate JSON generator
```

## 4. Compatibility Facade Strategy

Every old monolithic service file (`tournament_service.py`, `registration_service.py`, etc.) has been **converted to a thin backward-compatibility facade**. These facades:

1. Import the focused sub-services from the new domain-organized package.
2. Delegate each public method 1:1 to the appropriate sub-service.
3. Re-export any module-level names (constants, exceptions, helper functions) that callers depend on.
4. Preserve the original class name and API surface so **no route or test imports need to change**.

Routes and tests continue importing from `application.<name>_service` — the facade transparently delegates to the package underneath.

### Facade Delegation Tables

#### `round_service.py` → `application.round`

| Facade Method | Delegates To |
|---|---|
| `RoundService.create_next_round` | `RoundLifecycleService.create_next_round` |
| `RoundService.finish_round` | `RoundLifecycleService.finish_round` |
| `RoundService.save_results` | `ResultRecordingService.save_results` |
| `RoundService.swap_colors_in_board` | `ManualAdjustmentService.swap_colors_in_board` |
| `RoundService.swap_players_between_boards` | `ManualAdjustmentService.swap_players_between_boards` |
| `RoundService.add_manual_pairing` | `ManualAdjustmentService.add_manual_pairing` |
| `RoundService.add_manual_bye` | `ManualAdjustmentService.add_manual_bye` |
| `RoundService.remove_manual_pairing` | `ManualAdjustmentService.remove_manual_pairing` |
| `RoundService.cancel_bye_request` | `ManualAdjustmentService.cancel_bye_request` |
| `RoundService.delete_round` | `RoundLifecycleService.delete_round` |
| `RoundService.rebuild_swiss_state` | `StatsRebuildService.rebuild_swiss_state` |

#### `tournament_service.py` → `application.tournament`

| Facade Method | Delegates To |
|---|---|
| `TournamentService.create` | `TournamentConfigService.create` |
| `TournamentService.update_basic_settings` | `TournamentConfigService.update_basic_settings` |
| `TournamentService.update_pricing_settings` | `TournamentPricingService.update_pricing_settings` |
| `TournamentService.update_registration_requirements` | `TournamentRegistrationRulesService.update_registration_requirements` |
| `TournamentService.update_rulebook_settings` | `TournamentRulebookService.update_rulebook_settings` |
| `TournamentService.get_standings` | `StandingsService.get_standings` |
| `TournamentService._build_tiebreak_data` | `StandingsService._build_tiebreak_data` |
| `TournamentService._calculate_rating_changes` | `StandingsService._calculate_rating_changes` |

#### `registration_service.py` → `application.registration`

| Facade Method | Delegates To |
|---|---|
| `RegistrationService.create_registration` | `RegistrationCreator.create_registration` |
| `RegistrationService.approve_registration` | `RegistrationApprover.approve_registration` |
| `RegistrationService.reject_registration` | `RegistrationApprover.reject_registration` |
| `RegistrationService.discard_receipt` | `ReceiptHandler.discard_receipt` |
| `RegistrationService.reject_receipt` | `ReceiptHandler.reject_receipt` |

Re-exports: `BLOCKING_REGISTRATION_STATUSES`, `OPEN_SLOT_STATUSES`.

Private helper methods (`_map_profile_to_eligibility`, `_map_tournament_to_pricing_data`, etc.) are also forwarded to the appropriate sub-service.

#### `player_service.py` → `application.player`

| Facade Method | Delegates To |
|---|---|
| `PlayerService.create` | `ParticipantManagement.create` |
| `PlayerService.update` | `ParticipantManagement.update` |
| `PlayerService.toggle_withdraw` | `ParticipantManagement.toggle_withdraw` |
| `PlayerService.delete` | `ParticipantManagement.delete` |

Re-exports: `_detect_age_category`.

#### `admin_service.py` → `application.admin`

| Facade Method | Delegates To |
|---|---|
| `AdminService.get_all_users` | `UserManagementService.get_all_users` |
| `AdminService.get_users_paginated` | `UserManagementService.get_users_paginated` |
| `AdminService.get_user_detail` | `UserManagementService.get_user_detail` |
| `AdminService.add_role` | `UserManagementService.add_role` |
| `AdminService.remove_role` | `UserManagementService.remove_role` |
| `AdminService.toggle_role` | `UserManagementService.toggle_role` |
| `AdminService.toggle_admin` | `UserManagementService.toggle_admin` |
| `AdminService.get_dashboard_stats` | `DashboardStatsService.get_dashboard_stats` |
| `AdminService.get_tournaments_paginated` | `TournamentAdminService.get_tournaments_paginated` |
| `AdminService.get_notification_stats` | `DashboardStatsService.get_notification_stats` |
| `AdminService.get_system_health` | `SystemHealthService.get_system_health` |

Class attribute: `VALID_ROLES`.

#### `auth_service.py` → `application.auth`

| Facade Method | Delegates To |
|---|---|
| `AuthService.register` | `AuthenticationService.register` |
| `AuthService.authenticate` | `AuthenticationService.authenticate` |
| `AuthService.link_player_profile` | `ProfileLinkingService.link_player_profile` |
| `AuthService.claim_profile` | `ProfileLinkingService.claim_profile` |
| `AuthService.create_profile_for_user` | `ProfileCreationService.create_profile_for_user` |

#### `payment_service.py` → `application.payment`

| Facade Method | Delegates To |
|---|---|
| `PaymentService.initiate_payment` | `PaymentInitiator.initiate_payment` |
| `PaymentService.process_callback` | `PaymentInitiator.process_callback` |

Re-exports: `OPEN_SLOT_STATUSES`, `gateway`.

#### `verification_service.py` → `application.verification`

| Facade Method | Delegates To |
|---|---|
| `VerificationService.submit_request` | `VerificationRequestService.submit_request` |
| `VerificationService.get_pending_requests` | `VerificationRequestService.get_pending_requests` |
| `VerificationService.approve_request` | `VerificationStatusUpdater.approve_request` |
| `VerificationService.verify_fide_id` | `VerificationApprover.verify_fide_id` |
| `VerificationService.verify_dob` | `VerificationApprover.verify_dob` |
| `VerificationService.verify_photo` | `VerificationApprover.verify_photo` |
| `VerificationService.reject_request` | `VerificationStatusUpdater.reject_request` |

#### `fide_import_service.py` → `application.fide`

| Facade Method | Delegates To |
|---|---|
| `FideImportService.run_import` | `FideImportOrchestrator.run_import` |
| `FideImportService.start_async` | `FideImportOrchestrator.start_async` |
| `FideImportService.execute_import` | `FideImportOrchestrator.execute_import` |
| `FideImportService.latest_status` | `FideImportOrchestrator.latest_status` |

Re-exports: `STALE_RUN_MINUTES`, `BATCH_SIZE`.

#### `fide_search_service.py` → `application.fide`

| Facade Method | Delegates To |
|---|---|
| `FideSearchService.search` | `FideSearchService.search` (package-level) |

#### `import_export_service.py` → `application.import_export`

| Facade Method | Delegates To |
|---|---|
| `ImportExportService.export_tournament` | `ExportService.export_tournament` |
| `ImportExportService.import_tournament` | `ImportService.import_tournament` |
| `ImportExportService.preview_tournaments_in_file` | `PreviewService.preview_tournaments_in_file` |
| `ImportExportService.create_tournament_from_backup` | `ImportService.create_tournament_from_backup` |

Re-exports: `ImportExportError`.

#### `prize_service.py` → `application.prize`

| Facade Method | Delegates To |
|---|---|
| `PrizeService.save_prizes` | `PrizeDefinitionService.save_prizes` |
| `PrizeService.get_definitions` | `PrizeDefinitionService.get_definitions` |
| `PrizeService.build_candidates` | `PrizeAllocationService.build_candidates` |
| `PrizeService.allocate_for_tournament` | `PrizeAllocationService.allocate_for_tournament` |
| `PrizeService.refresh_for_tournament` | `PrizeAllocationService.refresh_for_tournament` |
| `PrizeService.get_public_prize_summary` | `PrizeSummaryService.get_public_prize_summary` |
| `PrizeService.get_editor_rows` | `PrizeSummaryService.get_editor_rows` |

#### `telegram_service.py` → `application.telegram`

Pure re-export facade — no wrapper class. Re-exports: `TelegramService`, `_log_file_path`, `_ensure_log_handler`, `_mask`, `logger`.

#### `bale_service.py` → `application.bale`

Pure re-export facade — no wrapper class. Re-exports: `BaleService`, `_log_file_path`, `_ensure_log_handler`, `_mask`, `logger`.

## 5. Package Decomposition Details

### `application/round/` — Round Lifecycle

- **`RoundLifecycleService`** — Core round lifecycle: `create_next_round`, `finish_round`, `delete_round`. Handles validation, SwissEngine invocation, pairing persistence, and state transitions.
- **`PairingGenerationService`** — Swiss pairing generation, pairing number initialization, opponent tracking, color swap validation, and incremental stat updates.
- **`ResultRecordingService`** — Saving round results from form data and finalizing rounds.
- **`ManualAdjustmentService`** — Arbiter operations: color swaps, player swaps between boards, manual pairing locks, bye requests, and cancellation.
- **`StatsRebuildService`** — Full Swiss state reconstruction from stored results. Used after imports, restores, or round deletion.
- **`RoundNotificationService`** — Notification fan-out for round lifecycle events (currently: `notify_round_created`). Consults the tournament-level notification gate before dispatching.

### `application/tournament/` — Tournament Management

- **`TournamentConfigService`** — Basic tournament settings (identity, competition, tiebreaks, dates).
- **`TournamentPricingService`** — Pricing, discounts, bank/payment, early bird, veteran, title discounts.
- **`TournamentRegistrationRulesService`** — Entry requirements (eligibility rules).
- **`TournamentRulebookService`** — Rulebook text, sections, PDF management.
- **`StandingsService`** — Standings computation with tiebreaks.
- **`TournamentAdminService`** — Tournament-level admin operations.

### `application/registration/` — Registration Workflow

- **`RegistrationCreator`** — Full registration creation workflow (deadline check, eligibility, capacity, profile lookup/create, duplicate check, promo code validation, price calculation, notification).
- **`EligibilityChecker`** — Enforces tournament-configured entry requirements.
- **`PricingCalculator`** — Computes registration price with discounts.
- **`RegistrationApprover`** — Approves pending registrations, creates participants.
- **`ReceiptHandler`** — Bank transfer receipt upload, discard, and reject lifecycle.

### `application/player/` — Participant Management

- **`ParticipantManagement`** — Participant CRUD: create (with auto-FIDE rating fetch), update, toggle withdraw, delete (with renumbering).
- **`FideRatingFetcher`** — Auto-fetches FIDE rating for participant snapshots.

### `application/verification/` — FIDE Verification

- **`VerificationRequestService`** — Submit verification requests, list pending requests.
- **`VerificationApprover`** — Per-aspect verification (FIDE ID, DOB, photo) with approve/reject.
- **`VerificationStatusUpater`** — Top-level approve/reject that coordinates per-aspect updates.

### `application/auth/` — Authentication

- **`AuthenticationService`** — User registration and password-based authentication.
- **`ProfileLinkingService`** — Link player profiles to user accounts (claim workflow).
- **`ProfileCreationService`** — Create player profiles for authenticated users.

### `application/admin/` — System Administration

- **`UserManagementService`** — User CRUD, role management, admin toggle.
- **`DashboardStatsService`** — Admin dashboard statistics and notification stats.
- **`SystemHealthService`** — System health checks.
- **`TournamentAdminService`** — Tournament listing/pagination for admin dashboard.

### `application/payment/` — Payment Processing

- **`PaymentInitiator`** — Initiates Zarinpal payment and handles callback processing.

### `application/fide/` — FIDE Data

- **`FideImportOrchestrator`** — Full FIDE XML import pipeline (download, parse, upsert).
- **`FideSearchService`** — Search local FIDE player database.

### `application/import_export/` — Import/Export

- **`ExportService`** — Export tournament to provider format (e.g., Coronate JSON).
- **`ImportService`** — Import tournament from provider format.
- **`PreviewService`** — Preview backup file contents before import.

### `application/prize/` — Prize System

- **`PrizeDefinitionService`** — Prize CRUD (save/load from tournament JSON).
- **`PrizeAllocationService`** — Deterministic allocation over standings.
- **`PrizeSummaryService`** — Public prize summary DTO and editor rows.

### `application/telegram/` and `application/bale/` — Messaging

- **`TelegramService`** / **`BaleService`** — Bot API: token generation, account linking, message sending.
- **`TelegramLinkService`** / **`BaleLinkService`** — Account linking workflow (token, webhook).

## 6. Notification Architecture

Notifications follow a three-tier dispatch pattern:

```
Business Service  ──>  NotificationService  ──>  NotificationDispatcher  ──>  Providers
                                                  (web, telegram, bale)
```

- **`NotificationService`** (`notification_service.py`) — Single entry point: `create_notification(user_id, type, title, message, link_url)`.
- **`NotificationDispatcher`** (`notification_dispatcher.py`) — Fan-out to enabled providers based on user preferences.
- **`NotificationType`** (`notification_types.py`) — Enum of all notification types (WELCOME, REGISTRATION_SUBMITTED, ROUND_CREATED, etc.).
- **`notification_policy.py`** — Tournament-level gate (`tournament_allows`) and preference serialization.
- **`NotificationProviderInterface`** — Abstract contract for providers.

Providers (`application/providers/`):
- `WebProvider` — Stores in DB for in-app display.
- `TelegramProvider` — Sends via Telegram Bot API.
- `BaleProvider` — Sends via Bale Bot API.

**Round-specific notification fan-out** is handled by `RoundNotificationService` (in `application/round/`), which `RoundLifecycleService` calls after persisting pairings.

## 7. Standalone Modules

These modules were not decomposed into packages because they are either:
- Already cohesive and small (notification infrastructure).
- Orchestration-only with no meaningful sub-domain to split.

- **`notification_service.py`** — Core notification CRUD and dispatch trigger. Used by all business services.
- **`notification_dispatcher.py`** — Fan-out to providers based on user preferences.
- **`notification_types.py`** — Notification type enums and Persian display names.
- **`notification_policy.py`** — Tournament-level notification gate.
- **`player_profile_service.py`** — Profile data + FIDE info orchestration. No decomposition needed.

## 8. Clean Architecture Rules

**Application layer MUST NOT:**
- Import from `interfaces/web/` (no Flask request/session/render_template)
- Re-implement Swiss pairing, tiebreak, or rating logic (delegate to `domain/`)
- Write raw SQL or execute migrations
- Import from `domain/` for infrastructure concerns or vice versa

**Application layer MUST:**
- Own all database transactions (`db.session.commit()` / `rollback()`)
- Use repository methods for data access (never direct model queries from routes)
- Use `db.session.flush()` before querying freshly inserted objects
- Use `@staticmethod` for stateless service orchestration

## 9. Migration from Monoliths

The refactoring followed this pattern for each legacy monolith:

1. **Extract** — Move business logic into focused sub-services under a domain package.
2. **Fix cross-dependencies** — Redirect internal imports to point at the new package modules.
3. **Convert to facade** — Replace the monolith file with a thin delegation layer.
4. **Preserve API** — Ensure the facade re-exports all public methods, constants, and helper functions that callers depend on.
5. **Verify** — Run the full test suite to confirm zero regressions.

The `round_service.py` conversion was done first as a template. The remaining 13 facades were converted in a single batch, with cross-dependency fixes applied to the new packages (e.g., `application/payment/payment_initiator.py` importing `OPEN_SLOT_STATUSES` from `application.registration.registration_creator`).

## 10. Backward-Compatible Imports

For new code, prefer the package-level imports over legacy facade imports:

| Legacy Import | Package Import |
|---|---|
| `from application.round_service import RoundService` | `from application.round import RoundLifecycleService, ...` |
| `from application.tournament_service import TournamentService` | `from application.tournament import TournamentConfigService, ...` |
| `from application.registration_service import RegistrationService` | `from application.registration import RegistrationCreator, ...` |
| `from application.admin_service import AdminService` | `from application.admin import UserManagementService, ...` |
| `from application.auth_service import AuthService` | `from application.auth import AuthenticationService, ...` |
| `from application.player_service import PlayerService` | `from application.player import ParticipantManagement, ...` |
| `from application.payment_service import PaymentService` | `from application.payment import PaymentInitiator, ...` |
| `from application.verification_service import VerificationService` | `from application.verification import VerificationRequestService, ...` |
| `from application.fide_import_service import FideImportService` | `from application.fide import FideImportOrchestrator, ...` |
| `from application.fide_search_service import FideSearchService` | `from application.fide import FideSearchService` |
| `from application.import_export_service import ImportExportService` | `from application.import_export import ImportService, ExportService, ...` |
| `from application.prize_service import PrizeService` | `from application.prize import PrizeAllocationService, ...` |
| `from application.telegram_service import TelegramService` | `from application.telegram import TelegramService` |
| `from application.bale_service import BaleService` | `from application.bale import BaleService` |

The legacy facade imports continue to work and will be preserved until all callers migrate.

## 11. Testing

- Service layer tests use the in-memory SQLite database fixture (`tests/conftest.py`).
- Tests verify state changes (e.g., `create_next_round` reduces active `ByeRequests`).
- The facade layer passes all existing tests that previously tested the monoliths.
- Two test monkeypatch paths were updated to point at the new package modules:
  - `tests/test_tournament_service.py` → patches `application.tournament.tournament_config_service.TournamentRepository`
  - `tests/test_fide_import_flow.py` → patches `application.fide.fide_import_orchestrator.threading.Thread`

### Pre-existing Test Failures (8 total, unrelated to application-layer refactoring)

| Test | Root Cause |
|---|---|
| `test_deployment_schema::test_upgrade_produces_exactly_the_model_schema` | Baseline migration drift — model has columns not in the migration |
| `test_deployment_schema::test_flask_db_check_reports_no_pending_operations` | Same drift detected by `flask db check` |
| `test_phase10::test_self_demotion_protection` | Stale error message pattern — admin API changed wording |
| `test_phase9a::test_create_notification` | Pre-dates provider-based dispatch redesign (`create_notification` returns `None`) |
| `test_phase9a::test_mark_as_read` | Same root cause as above |
| `test_phase9a::test_user_isolation_on_read` | Same root cause as above |
| `test_phase9d::test_default_preferences` | Same root cause as above |
| `test_phase9h::test_user_isolation_mark_read` | Same root cause as above |

The 6 notification tests (phase9a/9d/9h) predate the fire-and-forget provider-based dispatch redesign and need contract updates, not product changes. The 2 schema tests reflect a deployment migration that has not been regenerated.
