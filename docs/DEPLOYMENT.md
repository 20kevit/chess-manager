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

## 11. Configure Telegram/Bale webhooks
After first successful page load (HTTPS):
```bash
curl -F "url=https://YOURDOMAIN/api/telegram/webhook" \
     -F "secret_token=<TELEGRAM_WEBHOOK_SECRET>" \
     https://api.telegram.org/bot<TOKEN>/setWebhook

curl -F "url=https://YOURDOMAIN/api/bale/webhook" \
     https://tapi.bale.ai/bot<TOKEN>/setWebhook   # verify Bale secret_token support
```

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

## Writable directories (Passenger user)
| Path | Purpose |
|---|---|
| `instance/uploads/receipts/` | bank receipts (private, auto-created) |
| `instance/data/fide/<YYYY-MM>/` | FIDE XML downloads (auto-created) |
| `instance/*.log` | telegram/bale debug logs (lazy, optional) |
| `tmp/` | Passenger restart signal |

All are anchored to the Flask instance path — never CWD-dependent.
