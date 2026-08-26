# Production Deployment Runbook — CLEAN/FRESH install (cPanel + Passenger)

Strategy: **clean/fresh production deployment**. The database is created empty and
migrated with a single squashed baseline (`bb0160eefd6b`). No historical schema or
uploaded files need to be preserved or migrated.

---

## 0. Prerequisites

| Requirement | Value |
|---|---|
| Python | **3.12** (dependency resolution verified for cp312; dev suite also validated on 3.14) |
| Database | Empty MySQL 5.7+/MariaDB 10.2+ database + dedicated user (utf8mb4 capable — default on modern cPanel) |
| App server | Phusion Passenger (cPanel "Setup Python App" or manual) |

## 1. Upload code
Upload the project (excluding `venv/`, `.env`, `instance/`, `data/`) to e.g.
`/home/CPANELUSER/swiss_app_dev`.

## 2. Create virtualenv (Python 3.12)
```bash
cd ~/swiss_app_dev
python3.12 -m venv python312_app_venv
```

## 3. Install dependencies
```bash
~/swiss_app_dev/python312_app_venv/bin/pip install --upgrade pip
~/swiss_app_dev/python312_app_venv/bin/pip install -r requirements.txt
```
(Resolution verified offline-compatible: all pins resolve as cp312 wheels.)

## 4. Configure environment variables
Create `~/swiss_app_dev/.env`:

| Variable | Required | Notes |
|---|---|---|
| `FLASK_ENV` | YES | `production` — activates Secure cookies + all fail-fast guards |
| `SECRET_KEY` | YES | `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` | YES | Empty MySQL DB from step 5 |
| `ZARINPAL_SANDBOX` | YES (prod) | **Must be `false`** — startup guard enforces this |
| `ZARINPAL_MERCHANT_ID` | YES (prod) | Real merchant UUID — placeholder/empty is rejected at startup |
| `TELEGRAM_WEBHOOK_SECRET` / `BALE_WEBHOOK_SECRET` | recommended | Random strings; required by the webhook `setWebhook secret_token` step (§11) |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_BOT_USERNAME` / `BALE_BOT_TOKEN` / `BALE_BOT_USERNAME` | optional | Only if messenger notifications are wanted |

Fail-fast reminders (app refuses to boot otherwise): missing `SECRET_KEY`/`DB_NAME`
in production, sandbox-enabled or placeholder Zarinpal merchant in production.

## 5. Create empty MySQL database/user
Via cPanel MySQL Wizard. Grant ALL on that single database only.

## 6. Run migrations
```bash
cd ~/swiss_app_dev
FLASK_ENV=production .venv-shim-not-needed: \
~/swiss_app_dev/python312_app_venv/bin/flask --app run.py db upgrade
```
Baseline `bb0160eefd6b` creates all 20 tables (utf8mb4). Verified locally:
upgrade → schema == models → `db check` clean → full MySQL DDL render.

## 7. Verify migrations (`db check`)
```bash
~/swiss_app_dev/python312_app_venv/bin/flask --app run.py db check
```
Expected output: `No new upgrade operations detected.`

## 8. Create the first system admin
Register a normal account via the web UI first, then:
```bash
~/swiss_app_dev/python312_app_venv/bin/flask --app run.py create-admin <email>
```

## 9. Configure Passenger
Copy `.htaccess.example` → `.htaccess` in the document root and replace the
`CPANELUSER` / venv-path placeholders (see file header). Ensure cPanel's
"Setup Python App" points at the same venv, or rely on `PassengerPython`.
`passenger_wsgi.py` needs no edits.

## 10. Restart Passenger
```bash
mkdir -p ~/swiss_app_dev/tmp && touch ~/swiss_app_dev/tmp/restart.txt
```
(or use the cPanel "Restart" button).

## 11. Configure Telegram/Bale webhooks (canonical procedure)

This is the ONLY webhook setup procedure; `docs/NOTIFICATIONS.md` links here.
Whenever `TELEGRAM_WEBHOOK_SECRET` / `BALE_WEBHOOK_SECRET` are set in `.env`,
the application rejects (HTTP 403) every incoming update whose
`X-*-Bot-Api-Secret-Token` header does not match — so registration below is
MANDATORY whenever the secrets exist.

```bash
# Telegram — secret_token is required:
curl -F "url=https://YOURDOMAIN/api/telegram/webhook" \
     -F "secret_token=<TELEGRAM_WEBHOOK_SECRET>" \
     https://api.telegram.org/bot<TOKEN>/setWebhook

# Bale — same shape against the Bale API:
curl -F "url=https://YOURDOMAIN/api/bale/webhook" \
     -F "secret_token=<BALE_WEBHOOK_SECRET>" \
     https://tapi.bale.ai/bot<TOKEN>/setWebhook
```

Both calls must answer `{"ok":true,"result":true,...}`. Then verify:

```bash
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
curl https://tapi.bale.ai/bot<TOKEN>/getWebhookInfo
```

`last_error_message` mentioning a bad/missing secret header means the
registered webhook and the `.env` secret do not match — re-run setWebhook
with the exact value from `.env`.

Contingency: if a messenger platform rejects the `secret_token` parameter,
remove that platform's `*_WEBHOOK_SECRET` from `.env` (endpoint then accepts
unsigned updates) and restart. Never leave a secret configured while the
webhook was registered without it — that combination silently drops all
updates with 403s visible only in `<instance>/telegram_debug.log`.

## 12. Smoke tests
- `/` loads 200; `/login`, `/register` render over HTTPS
- Register user → dashboard; unread-count badge renders (notifications tables exist)
- Create tournament (organizer role) → add players → generate Round 1
- FIDE admin import (`/admin/fide`) completes and search returns rows
- Preferences page saves web/telegram/bale switches

## 13. Zarinpal production verification
1. Confirm `.env`: `ZARINPAL_SANDBOX=false` + real merchant ID (boot fails otherwise).
2. Controlled real transaction: register → pay small amount → complete OTP at
   gateway → callback must land on `/payment/callback?Authority=…&Status=OK`.
3. Verify DB: `payments.status='successful'`, `ref_id/card_pan` populated,
   registration `paid`; duplicate callback refresh does NOT flip state (101-safe).
4. Test cancel path once (`Status=NOK`) → payment `cancelled`, registration back
   to `pending`.

## 14. Database schema: the three paths (Phase-8 checkpoint)

The schema is maintained by ONE squashed baseline revision
(`bb0160eefd6b`, `down_revision = None`, 20 tables). P0-A…P0-G added four
nullable columns to that same baseline in place:

| Table | Added columns |
|---|---|
| `player_profiles` | `phone VARCHAR(20) NULL`, `photo_path VARCHAR(255) NULL`, `id_document_path VARCHAR(255) NULL` |
| `tournaments` | `registration_requirements TEXT NULL`, `rulebook_sections TEXT NULL`, `rulebook_pdf_path VARCHAR(255) NULL` |

Because the revision ID was preserved, Alembic cannot distinguish a
pre-P0 database from a post-P0 one — both are stamped
`bb0160eefd6b`. Pick exactly one of the three paths below.

### Path A — Fresh installation (empty MySQL database)
1. Create empty DB + user; fill `.env` (`DB_*`, `SECRET_KEY`,
   `FLASK_ENV=production`).
2. `flask --app run.py db upgrade` → creates all 20 tables at current shape.
3. Verify: `flask --app run.py db check` reports no pending operations;
   log in and create a tournament.

### Path B — EXISTING production database (created before the P0 release)
`flask db upgrade` is a **no-op** here (already stamped at head). Apply the
additive ALTERs once via cPanel phpMyAdmin or the MySQL CLI — they are
NULLable ADD COLUMN statements only: no drop, no type change, no data loss,
and safe to re-run after a guarded check:

```sql
-- Guarded idempotent pattern (repeat per column):
SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'player_profiles' AND COLUMN_NAME = 'phone');
SET @ddl := IF(@col_exists = 0,
  'ALTER TABLE player_profiles ADD COLUMN phone VARCHAR(20) NULL',
  'SELECT ''player_profiles.phone already present''');
PREPARE stmt FROM @ddl; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'player_profiles' AND COLUMN_NAME = 'photo_path');
SET @ddl := IF(@col_exists = 0,
  'ALTER TABLE player_profiles ADD COLUMN photo_path VARCHAR(255) NULL',
  'SELECT ''player_profiles.photo_path already present''');
PREPARE stmt FROM @ddl; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'player_profiles' AND COLUMN_NAME = 'id_document_path');
SET @ddl := IF(@col_exists = 0,
  'ALTER TABLE player_profiles ADD COLUMN id_document_path VARCHAR(255) NULL',
  'SELECT ''player_profiles.id_document_path already present''');
PREPARE stmt FROM @ddl; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'tournaments' AND COLUMN_NAME = 'registration_requirements');
SET @ddl := IF(@col_exists = 0,
  'ALTER TABLE tournaments ADD COLUMN registration_requirements TEXT NULL',
  'SELECT ''tournaments.registration_requirements already present''');
PREPARE stmt FROM @ddl; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- P1-D rulebook columns:
SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'tournaments' AND COLUMN_NAME = 'rulebook_sections');
SET @ddl := IF(@col_exists = 0,
  'ALTER TABLE tournaments ADD COLUMN rulebook_sections TEXT NULL',
  'SELECT ''tournaments.rulebook_sections already present''');
PREPARE stmt FROM @ddl; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'tournaments' AND COLUMN_NAME = 'rulebook_pdf_path');
SET @ddl := IF(@col_exists = 0,
  'ALTER TABLE tournaments ADD COLUMN rulebook_pdf_path VARCHAR(255) NULL',
  'SELECT ''tournaments.rulebook_pdf_path already present''');
PREPARE stmt FROM @ddl; EXECUTE stmt; DEALLOCATE PREPARE stmt;
```

Post-checks:
1. `flask --app run.py db check` → no pending operations.
2. Spot-check data survived (row counts on `users`, `tournaments`,
   `registrations`, `payments` before vs after).
3. Restart Passenger (`tmp/restart.txt`), then smoke-test §12.
4. Do NOT run `reset_db.py` on production — it drops everything.

### Path C — Local development reset (DEV ONLY)
`python reset_db.py` performs `drop_all()` + `create_all()` from the models
directly (no migration involved). Local SQLite/throwaway environments only.

> Rule of thumb for future schema work: additive nullable columns may keep
> being folded into the baseline WITH their ALTER statements added to this
> section. Anything destructive requires a NEW alembic revision instead.

## Writable directories (Passenger user)
| Path | Purpose |
|---|---|
| `instance/uploads/receipts/` | bank receipts (private, auto-created) |
| `instance/uploads/profile_photos/` | player photos (private, auto-created) |
| `instance/uploads/id_documents/` | identity documents (private, auto-created) |
| `instance/data/fide/<YYYY-MM>/` | FIDE XML downloads (auto-created) |
| `instance/*.log` | telegram/bale debug logs (lazy, optional) |
| `tmp/` | Passenger restart signal |

All are anchored to the Flask instance path — never CWD-dependent.
