# AGENTS.md — Swiss Tournament Manager (PRO CHESS)

Pure Python/Flask web app for FIDE Swiss-system chess tournaments (modern alternative to Swiss Manager). UI is 100% Persian/RTL. Domain targets **100% FIDE Dutch System compliance** (C.04.2 + C.04.3). Deterministic pairing — never introduce randomness.

## Commands

```bash
# Setup
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# Run (debug=True)
python run.py

# Tests — function-scoped in-memory SQLite, CSRF disabled
pytest tests                          # full suite
pytest tests/test_phase8.py -v        # subset

# Database
flask --app run.py db upgrade
flask --app run.py db migrate -m "..."
python reset_db.py                    # DEV ONLY: drop_all + create_all

# Promote existing user to System Admin
flask --app run.py create-admin <email>
```

No linter/formatter config, no CI pipeline.

## Configuration (`config.py`)

Reads `.env` via `python-dotenv`.

- **DB:** `DB_NAME` set → MySQL `mysql+pymysql` utf8mb4 (pool_pre_ping, recycle 280); otherwise SQLite `sqlite:///local.db`.
- **Production fail-fast:** raises if `SECRET_KEY` or `DB_NAME` missing when `FLASK_ENV=production`.
- **Security:** `SESSION_COOKIE_SAMESITE=Lax` always; `SESSION_COOKIE_SECURE` auto-enabled only in production (HTTPS). `MAX_CONTENT_LENGTH=8MB`.
- **Uploads:** all runtime-writable dirs anchored to `app.instance_path` (never CWD): `uploads/receipts/`, `uploads/profile_photos/`, `uploads/id_documents/`, `uploads/rulebooks/`, `data/fide/<YYYY-MM>/`. `telegram_debug.log`/`bale_debug.log` are lazy (handler never at import time).
- **FIDE:** `FIDE_DATA_DIR` (instance-anchored), `FIDE_RAW_RETENTION_DAYS=90`, `FIDE_ALLOWED_FEDERATIONS=["IRI"]`, `FIDE_XML_URL`.
- **Payments:** `ZARINPAL_MERCHANT_ID`, `ZARINPAL_SANDBOX` (default true; production guard requires `false` + real UUID).
- **Messengers:** `TELEGRAM_BOT_TOKEN`/`TELEGRAM_BOT_USERNAME`, `BALE_BOT_TOKEN`/`BALE_BOT_USERNAME`, `TELEGRAM_WEBHOOK_SECRET`/`BALE_WEBHOOK_SECRET` (when set, webhook `secret_token` is enforced — mismatched registration 403s every update).

## Architecture & Dependency Rules (STRICT)

```
run.py → app/create_app()  (app/__init__.py)
interfaces/web  →  application  →  domain  +  infrastructure
```

- `domain/` — pure Python. **MUST NOT** import `flask`, `sqlalchemy`, `infrastructure`, `interfaces/web`.
- `application/` — use-case orchestration. **Exclusive owner of transactions** (`commit`/`rollback`). **MUST NOT** import `interfaces/web` or `flask.request`.
- `infrastructure/` — SQLAlchemy models, repositories, external I/O (FIDE download, Zarinpal, Coronate). No business logic. Repositories use `db.session.flush()` **only** — never `commit`/`rollback`.
- `interfaces/web/` — Flask blueprints. HTTP concerns only (parse request, auth check, delegate to service, render/flash/redirect). **MUST NOT** contain business rules, direct `Model.query.*`, or transaction management. Prefer repositories via services; direct model queries are grandfathered tech-debt to fix, not a pattern to copy.

Circular dependencies between `application` packages are forbidden.

Details: `docs/AGENT_INSTRUCTIONS.txt`, `docs/DOMAIN.md`, `docs/APPLICATION.md`, `docs/INFRASTRUCTURE.md`, `docs/WEB_ROUTES_LAYER.md`, `docs/FRONTEND_UI_LAYER.md`, `docs/NOTIFICATIONS.md`. Keep `AGENTS.md` and those docs consistent.

## Layers

### `app/` — Flask factory

`create_app()` in `app/__init__.py`: inits `db`/`migrate`/`csrf`/`login_manager` (`login_view=auth.login`), registers 13 blueprints (no `url_prefix`), registers CLI `create-admin`, wires notification providers (Web/Telegram/Bale), registers error handlers (403/404/500/413), `toman_formatter` filter, `unread_notifications_count` context processor.

`extensions.py` owns `db`, `migrate`, `csrf`, `login_manager`. `cli.py` implements `flask create-admin`.

### `domain/` — pure business rules

- `pairing/` — FIDE Dutch engine. Public API (`__init__.py`): `PlayerData`, `PairingCard`, `RoundResult`, `pair_round(...)`, `SwissEngine(...).generate()`, `validate_round(...)`. `engine.py` = orchestrator; `pairer.py` = C.04.3 solver (bracket recursion, lazy lexicographic transpositions w/ bipartite-matching pruning, exchanges, downfloaters, 2M-node cap); `bracket.py`, `color.py`, `floats.py`, `exchange.py`, `transposition.py`, `bye.py`, `validator.py` (independent GEN/COL/FLO checker). Fully deterministic. Pairing numbers fixed at Round 1 (rating DESC, start_number ASC).
- `tiebreak/calculators.py` — Buchholz family, Sonneborn-Berger, progressive, wins/black-games, ARO/ARPO, Koya, direct encounter; `ALL_TIEBREAKS` + Persian names.
- `rating/calculator.py` — FIDE win-expectancy/dp tables, Elo change, performance rating.
- `pricing/engine.py` — additive percent discounts (early bird, veteran, women, FIDE title, promo), capped at 100%.
- `prizes.py` / `rulebook.py` — category titles, section vocabulary/parse/serialize.
- `fide/parser.py` — streaming `iterparse` of official FIDE XML → `FidePlayerData` (federation filter).
- `registration/__init__.py` — `normalize_phone`, eligibility helpers.

**Result vocabulary (9 types, everywhere):** `"1-0", "0-1", "1/2", "+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"`.

### `infrastructure/` — persistence & external I/O

**Models** (`infrastructure/models/` + legacy `db_models.py` facade): `UserModel` (pbkdf2:sha256, `is_admin`, telegram/bale link tokens), `UserRoleModel` (`player|organizer|arbiter`), `PlayerProfileModel`, `TournamentModel` (`public_id` 8-digit, status/pricing/rulebook/notification_prefs JSON), `TournamentParticipantModel` (`start_number`, `pairing_no`, `points`/`color_history`/`float_history`), `RoundModel`+`PairingModel` (float tags, `result`), `ByeRequestModel`, `ManualPairingModel`, `RegistrationModel`+`PaymentModel`+`PromoCodeModel`, `TournamentStaffModel`, `TempImportDataModel`, `FidePlayerModel`/`FideRatingModel`/`FideImportModel`, `PlayerVerificationModel`, `NotificationModel`/`NotificationPreferenceModel`, `TournamentPrizeModel`/`PrizeAllocationModel`.

**Repositories** (`infrastructure/repositories/` + legacy `repositories.py` facade): 16 static-method repos (Tournament, PlayerProfile, Participant, Round, Pairing, ManualPairing, User, Registration, PromoCode, Payment, Fide*, Notification*, Staff, Verification). Flush-only.

**External I/O:** `fide/storage.py` (HTTP download+unzip to `data/fide/<YYYY-MM>/`, retention); `gateways/zarinpal_gateway.py` (implements `PaymentGatewayInterface`, Toman→Rial ×10, sandbox default); `providers/coronate_*.py` (parser/generator — see mapping in `docs/INFRASTRUCTURE.md`); `file_storage.py` (private instance-anchored storage for receipts/photos/ID docs/rulebook PDFs, basename-only, magic-byte image check, `secure_filename`).

### `application/` — use-case services (owns transactions)

Entry hub: `application/__init__.py` re-exports all service names; `docs/APPLICATION.md` is the detailed reference.

| Package | Responsibility | Key services | Must NOT contain |
|---------|---------------|--------------|------------------|
| `admin/` | System-admin ops | `UserManagementService`, `DashboardStatsService`, `SystemHealthService`, `TournamentAdminService` | Web logic |
| `auth/` | Auth & profile linking | `AuthenticationService`, `ProfileCreationService`, `ProfileLinkingService` | Flask `request` |
| `tournament/` | Tournament config | `TournamentConfigService`, `TournamentPricingService`, `TournamentRegistrationRulesService`, `TournamentRulebookService`, `StandingsService` | Pairing logic (→ `domain`) |
| `round/` | Round lifecycle | `RoundLifecycleService`, `PairingGenerationService`, `ResultRecordingService`, `ManualAdjustmentService`, `StatsRebuildService`, `RoundNotificationService`, `RoundDisplayService` | HTTP handling |
| `registration/` | Registration flow | `RegistrationCreator`, `EligibilityChecker`, `PricingCalculator`, `RegistrationApprover`, `ReceiptHandler` | Pricing engine duplication (→ `domain.pricing`) |
| `player/` | Participant CRUD | `ParticipantManagement`, `PlayerCsvImportService` (+ `FideRatingFetcher`) | Tiebreak/rating |
| `verification/` | FIDE verification | `VerificationRequestService`, `VerificationApprover`, `VerificationStatusUpdater` | Web flash |
| `fide/` | FIDE data | `FideImportOrchestrator`, `FideSearchService` | HTTP download (→ `infrastructure.fide`) |
| `import_export/` | Backup I/O | `ExportService`, `ImportService`, `PreviewService` + `custom_json_provider` | — |
| `prize/` | Prize system | `PrizeDefinitionService`, `PrizeAllocationService`, `PrizeSummaryService` | — |
| `payment/` | Payments | `PaymentInitiator` | Gateway details (→ `infrastructure.gateways`) |
| `telegram/` / `bale/` | Messenger | `TelegramService`+`TelegramLinkService`, `BaleService`+`BaleLinkService` | — |
| `providers/` | Notification + Coronate | `WebProvider`, `TelegramProvider`, `BaleProvider`, `CoronateProvider`/`Parser`/`Generator` | — |
| Standalone | Cross-cutting | `NotificationService`→`NotificationDispatcher`→providers; `NotificationType`/`notification_policy`/`provider_registry`; `PlayerProfileService`; `DashboardAvailabilityService`; `PaymentGatewayInterface`/`ImportExportInterface` | — |

**Legacy facades:** 14 thin modules (`admin_service.py`, `auth_service.py`, `tournament_service.py`, `round_service.py`, `registration_service.py`, `player_service.py`, `payment_service.py`, `verification_service.py`, `fide_import_service.py`, `fide_search_service.py`, `import_export_service.py`, `prize_service.py`, `telegram_service.py`, `bale_service.py`, plus `infrastructure/db_models.py`/`repositories.py`) preserve the original import path and class name while delegating 1:1 to the new packages (see delegation tables in `docs/APPLICATION.md`). **New code must import from the package** (`from application.tournament import TournamentConfigService`); **never add business logic to a facade** — it is a compatibility shim, removed only when all callers have migrated.

### `interfaces/web/` — controllers (13 blueprints, no `url_prefix`)

Blueprint modules: `tournament/__init__.py`, `round_routes.py`, `player_routes.py`, `registration_routes.py`, `dashboard_routes.py`, `admin_routes.py`, `fide_routes.py`, `notification_routes.py`, `payment_routes.py`, `backup_routes.py`, `print_routes.py`, `player_profile_routes.py`, `auth_routes.py` (+ empty package stubs `admin/__init__.py`, `api/__init__.py`, `dashboard/__init__.py`, `registration/__init__.py`, `round/__init__.py`) + helpers `admin_auth.py` (`require_admin`/`require_tournament_manager`/`require_result_editor` — order: system admin → organizer → accepted `TournamentStaffModel` → legacy `session["admin_<public_id>"]`), `decorators.py` (`role_required(*roles)`, `admin_required`).

**Pattern:** parse/validate request → capability check → call `application.*` service → `db.session` never touched here → `flash()`+`redirect()` or `render_template()` with `url_for('bp.endpoint', public_id=...)`. Unified UI: public `tournament.view` doubles as arbiter console (`can_manage`/`can_edit_results`/`is_admin` flags) — never create separate admin templates/routes. Details: `docs/WEB_ROUTES_LAYER.md`.

## Frontend Architecture

Full map: **`docs/FRONTEND_UI_LAYER.md`** is the authoritative reference. Summary below.

**Stack:** Jinja2 + HTML5 + CSS3 (CSS Variables) + vanilla JS. No Bootstrap/Tailwind/jQuery/React. RTL Persian, Vazirmatn, `dir="rtl"`.

**Template inheritance:**

```
base.html ──▶ admin/base.html ──▶ admin/*.html  (admin chrome)
    ├──▶ tournament/*.html, dashboard/*.html, auth/*.html, notifications/*.html, …
print/base.html (standalone, print-only)
```

- `base.html` owns `<head>` (meta, CSRF `<meta name="csrf-token">`, 6 global CSS, Vazirmatn, header/nav/notification bell, flash alerts, footer, `js/app.js`).
- `admin/base.html` adds sidebar shell via `{% block extra_css %}` (`admin.css`) and wraps `{% block admin_content %}` in `.admin-layout`.
- `print/base.html` is intentionally isolated (only `print.css`, no header/bell/responsive).

**Global vs feature assets:**

| Scope | CSS | Loaded by | JS | Loaded by |
|-------|-----|-----------|----|-----------|
| **Global** | `base.css` (tokens/reset), `layout.css` (container/header/footer/hero), `components.css` (buttons/badges/alerts/forms/notifications), `tables.css` (.data-table/.crosstable), `tournament.css` (tournament chrome + utility tail), `responsive.css` (single @media sheet) | `base.html` (every page) | `app.js` (CSRF injection, notification dropdown, generic `[data-target]` toggle; `window.AppUtils`) | `base.html` |
| **Feature** | `admin.css` (sidebar/toolbar/admin-table/stats), `dashboard.css` (dash-header/grid/cards/modals), `print.css` (A4 landscape, @page) | `admin/base.html` (+all admin pages), `dashboard/index.html`, `print/base.html` | `modal.js` (generic `Modal.open/close` + focus trap), `notifications.js` (inbox mark-read), `tournament-view.js` (tabs + highlight filter), `tiebreak-dnd.js`, `manual-pairing.js`, `registration.js` (debounced price preview), `backup_import.js` (Coronate wizard) | `dashboard/index.html`, `notifications/index.html`, `tournament/view.html`, `tournament/settings.html`, `tournament/manual_pairing.html`, `tournament/register.html`, `tournament/import_from_backup.html` via `{% block extra_js %}` |

Small inline `<style>` in `register.html` (`.reg-*`/`price-box`) and `manual_pairing.html` (`.board-row`) is intentionally kept — not worth a per-page file (see decision in `docs/FRONTEND_UI_LAYER.md` §19).

**Key conventions:** `extra_css`/`extra_js` are *additive* (global → feature order matters); `data-*` attributes are the Jinja→JS channel (`data-api-url`, `data-base-price`, `data-cumulative-age-category`, `data-id`, `data-target/data-action/data-class`, `data-modal-trigger/close`) — external `.js` must not contain `{{ }}` except one 3-line shim in `tournament/view.html`; CSRF via `<meta name="csrf-token">` + `app.js:injectCSRFToken()` (no `{{ csrf_token() }}` in body); always `url_for('bp.endpoint', public_id=...)`; keep RTL/Persian intact.

## Where Should This Code Go?

| If you are implementing… | Put it in… | See |
|--------------------------|------------|-----|
| Pure business rule / FIDE compliance | `domain/` | `docs/DOMAIN.md` |
| Use-case orchestration / transaction | `application/` (focused package) | `docs/APPLICATION.md` |
| DB query / persistence | `infrastructure/repositories/` (+ model in `models/`) | `docs/INFRASTRUCTURE.md` |
| External API / file format | `infrastructure/gateways/` or `providers/` or `fide/` | `docs/INFRASTRUCTURE.md` |
| HTTP request/response / auth check | `interfaces/web/` (blueprint) | `docs/WEB_ROUTES_LAYER.md` |
| HTML structure | `templates/` (inheritance-aware) | `docs/FRONTEND_UI_LAYER.md` §4 |
| Reusable styling | `static/css/components.css` or section file | `docs/FRONTEND_UI_LAYER.md` §8 |
| Client-side behaviour | `static/js/` (feature module) | `docs/FRONTEND_UI_LAYER.md` §7 |
| Server → JS config | template `data-*` attribute | `docs/FRONTEND_UI_LAYER.md` §10 |
| Cross-cutting frontend behaviour | global `app.js` / `base.css` | `docs/FRONTEND_UI_LAYER.md` §12 |

## Critical Invariants (do not break)

- **Pairing is deterministic:** no `random`/`shuffle`; bipartite-matching pruning; 2M-node cap. `pairing_no` fixed at Round 1 (rating DESC, `start_number` ASC) and never changes. Bye selection via `domain.pairing.bye`.
- **Result vocabulary (9):** `"1-0","0-1","1/2","+/-","-/+","+/+","bye","half-bye","zero-bye"` — Coronate mapping is strict (see `docs/INFRASTRUCTURE.md` §6).
- **Lifecycle:** `Tournament.status` `setup→ongoing→finished` (first `create_next_round` → `ongoing`, last `finish_round` → `finished`); `Round.status` `pending→ongoing→finished`. Only `delete_round` / `rebuild_swiss_state` do full recompute; normal progress is incremental (`finish_round` updates `points`/`color_history`/`float_history`).
- **Tiebreaks:** configured order in `tournament.tiebreak_rules` (JSON), evaluated via `domain.tiebreak`; `StandingsService.get_standings` computes `player_standings` + `rating_changes`.
- **Payments are idempotent:** `PaymentInitiator.process_callback` handles duplicate callbacks; `code 101` counts as success; Rial = Toman×10; overbook flags manual-refund metadata, no auto-refunds.
- **Notifications are isolated:** `NotificationService → NotificationDispatcher → providers (Web/Telegram/Bale)`; dispatcher checks tournament gates + user prefs; provider failure never crashes the dispatcher.
- **FIDE data:** monthly XML, `fide/parser.py` streaming, default federation filter `IRI`, batch upsert every 500, tracked in `FideImportModel`, retention 90 days, instance-anchored storage.
- **IDs:** `TournamentModel.public_id` is the 8-digit URL key (never expose internal `id` in URLs).
- **RBAC:** `email+password` (pbkdf2), default `player`; system-admin via `is_admin`; tournament-manager = system-admin **or** organizer **or** accepted `TournamentStaffModel` (single `chief_arbiter` invariant); result-editor adds ordinary arbiter. No email/phone verification; Telegram/Bale links are 32-byte urlsafe, 10-min expiry, single-use, webhook-verified.
- **Unified UI:** `tournament.view` *is* the arbiter console (`can_manage`/`can_edit_results`), no parallel admin pages.

## Key Flows

**Setup → finish:** create tournament → add/import players → `RoundLifecycleService.create_next_round` (consumes bye/manual locks, runs `SwissEngine`, persists pairings) → arbiter edits results in `round_view.html` (`ResultRecordingService.save_results`) → `finish_round` (incremental stats) → repeat → last finished → `finished`. `delete_round` or import triggers `StatsRebuildService`.

**Auth:** `AuthService.register/authenticate` → `login_user` → `dashboard.index` hub (my_tournaments, invitations, registrations, participations). Arbiter via `dashboard.add_staff` (invite) → `accept_invitation`. FIDE verification via `VerificationRequestService` → system-admin `VerificationApprover`.

**Registration → payment:** `RegistrationCreator.create_registration` (eligibility+pricing+capacity checks) → `pending` → either `PaymentInitiator.initiate_payment` → Zarinpal → `callback` (idempotent → `paid`) **or** `ReceiptHandler.upload` → `receipt_submitted` → organizer `RegistrationApprover.approve` → participant. Price preview: `register.html data-api-url` → `registration.js fetch` → `registration.calculate_price` → JSON.

## Testing Conventions

```bash
pytest tests                                      # full suite
pytest tests/test_eligibility.py::TestX -v
```

- `tests/conftest.py`: `TestConfig` (in-memory SQLite, `TESTING=True`, `WTF_CSRF_ENABLED=False`), function-scoped fresh app.
- Styles: integration tests per phase (`test_phase8..10`, `test_fide_parser`, etc.) — class-based; plus service/route integrity tests (`test_pairing_flow`, `test_payment_flow`, `test_tournament_service`, …). No linter/CI.
- Baseline mirrors `docs/APPLICATION.md` §11 / `tests/conftest.py`: **8 pre-existing failures** are unrelated to recent refactors and need contract/migration fixes, not product changes:
  - `test_deployment_schema::test_upgrade_produces_exactly_the_model_schema` + `test_flask_db_check_reports_no_pending_operations` — baseline migration drift (models vs `bb0160eefd6b`).
  - `test_phase9a::test_create_notification/create`, `test_phase9a::test_mark_as_read`, `test_phase9a::test_user_isolation_on_read`, `test_phase9d::test_default_preferences`, `test_phase9h::test_user_isolation_mark_read`, `test_phase10::test_self_demotion_protection` — predate provider-based dispatch redesign (`create_notification` is fire-and-forget → `None`, wording changed).
- New tests: follow existing class-based integration style; prefer service-layer SQLite fixtures. Unit tests for `domain/pairing`, `tiebreak`, `rating`, `pricing` are still absent — add when touching those areas.

## Frontend-Specific Development Rules

- **No large CSS/JS blocks in templates.** Significant inline CSS → `admin.css`/`dashboard.css`/`print.css` or the appropriate global. Significant inline JS → `static/js/` (`extra_js`). Small contextual `<style>` (register price-box, board rows) may stay if extracting would create a one-off file.
- **Do not duplicate shared styles.** Reuse `components.css` buttons/badges/alerts/forms/tables; `tables.css` screen tables vs `admin.css` `.admin-table`; check §9 canonical table in `docs/FRONTEND_UI_LAYER.md`.
- **Do not create a file per component.** 9 CSS / 9 JS is the steady state. A feature file only for a coherent *section* (admin, dashboard, print). Otherwise extend the owning global (`tournament.css` etc.).
- **Use `data-*` for server→JS values** (`data-api-url="{{ url_for(...) }}"`, `data-base-price`, `data-cumulative-age-category`, `data-id`) — never `{{ }}` inside `.js`.
- **Replace inline handlers** (`onclick="..."`) with `addEventListener` / `data-*` dispatch where practical (`data-modal-trigger`, `data-target`).
- **Preserve `url_for(...)`**, RTL/Persian/Vazirmatn, focus/ESC/overlay modal behaviour, `dir="rtl"` layout, and CSRF (`meta[name=csrf-token]` + `app.js`). Global decorators handle auth flash/redirect.
- **Page-specific stays scoped:** load via `{% block extra_css %}`/`{% block extra_js %}` only on pages that need it — do not load every asset globally.
- **Verify after UI changes:** 3 viewports (360/768/1200), RTL, Print Preview for print pages; check `base.html`/`components.css`/`app.js` blast radius per `docs/FRONTEND_UI_LAYER.md` §12/§18.

## Code Style

English for code/comments/commit messages; user-facing strings/flash in Persian. No TODO convention — surface via review.

## Deferred (known tech-debt)

- No login/admin rate limiting (pbkdf2 mitigates; revisit post-beta).
- The 8 pre-existing test failures above (contract/migration drift, not product bugs).

## Deployment

`passenger_wsgi.py` exposes `run.app` as `application` on Phusion Passenger (cPanel). See `docs/DEPLOYMENT.md` for the clean-install runbook: Python 3.12 (verified on 3.14 dev), empty MySQL → `db upgrade` baseline `bb0160eefd6b`, `.htaccess.example`, env vars, FIDE/Zarinpal/webhook verification (§11), smoke tests, and Path A/B/C schema upgrade. No Dockerfile/Procfile/nginx in repo. Runtime-writable `instance/` paths must exist and be Passenger-writable.

## Documentation Map

| Topic | Read | Authoritative for… |
|-------|------|---------------------|
| Agent/project rules | `AGENTS.md` (this file) | Onboarding, commands, dependency rules, invariants map |
| Detailed agent instructions | `docs/AGENT_INSTRUCTIONS.txt` | Strict MUST/MUST NOT checklist |
| Domain (pairing/tiebreak/rating) | `docs/DOMAIN.md` | FIDE rules, engine API |
| Application services | `docs/APPLICATION.md` | Package tree, facades, delegation tables |
| Infrastructure (models/repos/external) | `docs/INFRASTRUCTURE.md` | Model/repository contracts, result mapping |
| Web routes | `docs/WEB_ROUTES_LAYER.md` | Route responsibilities, auth rules |
| Frontend/UI | `docs/FRONTEND_UI_LAYER.md` | **Authoritative** frontend map (templates/CSS/JS/data-flow) |
| Notifications | `docs/NOTIFICATIONS.md` | Provider webhooks, linking flow |
| Deployment | `docs/DEPLOYMENT.md` | **Authoritative** Passenger/MySQL/migration/webhook runbook |

Start with `AGENTS.md` then follow the map to the deep doc for the layer you are changing. When in doubt about the web/frontend split, `docs/FRONTEND_UI_LAYER.md` §11–§13 is the fastest orientation.
