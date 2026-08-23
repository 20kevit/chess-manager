# AGENTS.md — Swiss Tournament Manager (PRO CHESS)

Pure Python/Flask web application for managing chess (Swiss-system) tournaments, intended as a modern alternative to Swiss Manager. UI is 100% Persian/RTL. Domain rules target **100% FIDE Dutch System compliance** (C.04.2 + C.04.3).

## Commands

```bash
# Setup
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# Run (dev server, debug=True)
python run.py

# Tests (pytest; function-scoped in-memory SQLite, CSRF disabled)
pytest tests

# Database
flask --app run.py db upgrade          # apply migrations (Flask-Migrate/Alembic)
flask --app run.py db migrate -m "..." # autogenerate revision
python reset_db.py                     # DEV ONLY: drop_all + create_all

# Promote a registered user to System Admin
flask --app run.py create-admin <email>
```

There is no linter/formatter config and no CI pipeline in this repository.

## Configuration (`config.py`)

- Reads `.env` via `python-dotenv`.
- If `DB_NAME` is set → MySQL (`mysql+pymysql`, `utf8mb4`, pool_pre_ping/recycle 280). Otherwise → SQLite `sqlite:///local.db` (dev default).
- Production fail-fast: raises if `SECRET_KEY` or `DB_NAME` missing when `FLASK_ENV=production`.
- FIDE settings: `FIDE_DATA_DIR` (default `data/fide`), `FIDE_RAW_RETENTION_DAYS=90`, `FIDE_ALLOWED_FEDERATIONS=["IRI"]`, `FIDE_XML_URL`.
- Other env vars: `ZARINPAL_MERCHANT_ID`, `ZARINPAL_SANDBOX` (default true), `TELEGRAM_BOT_TOKEN`/`TELEGRAM_BOT_USERNAME`, `BALE_BOT_TOKEN`/`BALE_BOT_USERNAME`.

## Architecture & Dependency Rules (STRICT)

```
run.py ─> app/create_app() factory (app/__init__.py)
interfaces/web  ──>  application  ──>  domain  +  infrastructure
```

- `domain/` — pure Python only. MUST NOT import flask/sqlalchemy/infrastructure.
- `application/` — use-case services. Owns all transactions (`commit`/`rollback`). MUST NOT import from `interfaces/web/`.
- `infrastructure/` — SQLAlchemy models, repositories, external I/O. No business logic. Repositories use `db.session.flush()` only.
- `interfaces/web/` — Flask blueprints/controllers. No direct `Model.query...`; always go through repositories/services.

More detail in `docs/` (AGENT_INSTRUCTIONS.txt, DOMAIN.md, APPLICATION.md, INFRASTRUCTURE.md, WEB_ROUTES_LAYER.md, FRONTEND_UI_LAYER.md, NOTIFICATIONS.md) — keep them consistent when changing architecture.

## Layers

### `app/` — Flask factory
- `__init__.py`: `create_app()` — init extensions, register user_loader, register 14 blueprints (no url_prefixes), CLI, notification providers (Web/Telegram/Bale), error handlers (403/404/500), `toman_formatter` filter, unread-notification context processor.
- `extensions.py`: `db`, `migrate`, `csrf` (CSRFProtect global), `login_manager` (login_view=`auth.login`).
- `cli.py`: `flask create-admin <email>` (sets `is_admin=True`; user must exist first).

### `domain/` — pure business rules
- `pairing/`: FIDE Dutch pairing engine. Public API in `__init__.py`: `PlayerData`, `PairingCard`, `RoundResult`, `pair_round(...)`, `SwissEngine(...).generate()`, `validate_round(...)`. `engine.py` = orchestrator (input normalization, locked pairs, bye selection); `pairer.py` = C.04.3 solver (bracket recursion, lazy lexicographic transpositions with bipartite-matching pruning, exchanges, downfloaters, 2M-node search cap). Supporting modules: `bracket.py`, `color.py`, `floats.py`, `exchange.py`, `transposition.py`, `bye.py`. `validator.py` is an independent legality checker (GEN/COL/FLO rule IDs). Fully deterministic — NEVER introduce randomness. Pairing numbers are fixed at Round 1 (rating DESC, start_number ASC).
- `tiebreak/calculators.py`: Buchholz family, Sonneborn-Berger, progressive, wins/black-games, ARO/ARPO, Koya, direct encounter; registry `ALL_TIEBREAKS` + Persian display names.
- `rating/calculator.py`: FIDE win-expectancy/dp tables, Elo rating change, performance rating.
- `pricing/engine.py`: additive percent discounts (early bird, veteran, women, FIDE title, promo), capped at 100%.
- `fide/parser.py`: streaming (`iterparse`) parser for official FIDE players-list XML with federation filter → `FidePlayerData`.

Result vocabulary everywhere (9 types): `"1-0", "0-1", "1/2", "+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"`.

### `infrastructure/` — persistence & external systems
- `db_models.py`: all SQLAlchemy models. Key ones: `UserModel` (password_hash pbkdf2:sha256, `is_admin`, telegram/bale link tokens), `UserRoleModel` (`player|organizer|arbiter`), `PlayerProfileModel` (FIDE id, verification status), `TournamentModel` (`public_id` 8-digit URL key, `admin_code` secret, status, pricing/rulebook JSON), `TournamentParticipantModel` (start_number, `pairing_no`, points/color_history/float_history), `RoundModel` + `PairingModel` (+ floats, result), `ByeRequestModel`, `ManualPairingModel`, `RegistrationModel`, `PaymentModel`, `TournamentStaffModel` (per-tournament arbiter invites), `TempImportDataModel`, `FidePlayerModel`/`FideRatingModel`/`FideImportModel`, `PlayerVerificationModel`, `NotificationModel`, `NotificationPreferenceModel`.
- `repositories.py`: ~16 static-method repositories (Tournament, PlayerProfile, Participant, Round, Pairing, ManualPairing, User, Registration, PromoCode, Payment, Fide*, Notification*). Flush-only contract; services commit.
- `fide/storage.py`: downloads/unzips monthly XML into `data/fide/<YYYY-MM>/`, retention cleanup.
- `gateways/zarinpal_gateway.py`: implements `PaymentGatewayInterface`; sandbox default; Toman→Rial ×10.
- `providers/coronate_*.py`: import/export of Coronate JSON backups (see result-mapping table in `docs/INFRASTRUCTURE.md`).

### `application/` — services (one module per use case)
auth, verification (FIDE-ID claims), tournament, round, registration (+ pricing/promo), payment, player/player_profile, admin, notification (+ dispatcher/provider interface/types/preferences), telegram/bale linking, fide_import/fide_search, import_export (+ provider registry, interface).

### `interfaces/web/` — controllers (14 blueprints)
tournament, player, round, print, admin_auth, backup, auth, admin (system-admin dashboard), dashboard, registration, payment, fide, player_profile, notification.
- Access helpers: `require_admin(public_id)` in `admin_auth.py` returns tournament or None; checks (in order) system admin → organizer → accepted `TournamentStaffModel` assignment → legacy `session["admin_<public_id>"] == admin_code`.
- Global decorators in `decorators.py`: `role_required(*roles)` (redirects/flashes), `admin_required` (403).
- Unified UI: public `tournament.view` page doubles as arbiter console (`is_admin` flag). Never create separate admin pages/routes; never put `admin_code` in URLs or redirects.

## Key flows

**Tournament lifecycle:** `setup` → first round creation sets `ongoing` → last round finished sets `finished`. Round: `pending → ongoing → finished`. Round creation (`round_service.create_next_round`) consumes bye requests + manual locks, runs `SwissEngine`, persists pairings + synthetic bye boards, then fans out notifications. Points/color/float history update **incrementally** on `finish_round`; full recompute (`ParticipantRepository.update_points`) only after imports or `delete_round`. Standings computed in `tournament_service.get_standings` (points → configured tiebreaks → rank).

**Auth/RBAC:** email+password (werkzeug pbkdf2), default role `player`. Roles managed by system admins (`admin_service`). Tournament-level arbiter access via staff invitations. No email/phone verification exists; only Telegram/Bale link tokens (32-byte urlsafe, 10-min expiry, single-use, webhook-based `/api/telegram/webhook`, `/api/bale/webhook`).

**Payments:** `payment_service.initiate_payment` → Zarinpal (sandbox by default) → callback `process_callback` is idempotent; success marks registration `paid`; overbook flags manual-refund-required metadata; no auto refunds.

**Notifications:** business services call `NotificationService.create_notification` → `NotificationDispatcher` → per-user channel preferences (default enabled) → providers (Web/Telegram/Bale); provider failures isolated.

**FIDE data:** monthly XML download → parse/filter (IRI default) → upsert `FidePlayerModel` + insert `FideRatingModel` (batch commit every 500) → tracked in `FideImportModel`.

## Testing conventions

- `tests/conftest.py`: `TestConfig` (in-memory SQLite, TESTING=True, WTF_CSRF_ENABLED=False); fresh app per test function.
- Existing tests are integration tests named per phase (`test_phase8..10`, `test_fide_parser`). **No unit tests yet for domain/pairing, tiebreak, rating, pricing.** When adding features, add tests following the existing class-based style.
- `scripts/test_fide_parser.py` is a standalone script duplicate of the pytest version.

## Frontend rules

Vanilla JS + custom CSS only (no Bootstrap/Tailwind/jQuery/React). RTL Persian, Vazirmatn font. CSRF token injected via `<meta name="csrf-token">` + auto-appended hidden inputs by base template JS. Use `url_for('bp.route', public_id=...)`; use `data-*` attributes for client-side filtering/highlighting. Templates under `templates/` (tournament/admin/dashboard/auth/player/print/notifications/errors), CSS under `static/css`, JS under `static/js`.

## Code style

English for code/comments/commit messages; user-facing strings and flash messages in Persian. No TODO markers convention currently — issues surface in code review.

## Deployment

`passenger_wsgi.py` targets Phusion Passenger (cPanel shared hosting): adds project root to `sys.path` and exposes `run.app` as `application`. No Dockerfile/Procfile/nginx config in repo. `telegram_debug.log` / `bale_debug.log` are written to CWD by the messenger services lazily on first use (handler init never happens at import time).
