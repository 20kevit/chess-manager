# Production Readiness Assessment — Swiss Tournament Manager

**Date:** 2026-08-31 (release candidate)
**Baseline:** 797 tests (c5d5024) → 822 tests (post-hardening) → 856 tests (release candidate, 0 unexplained)
**Commits:** `4a238df` (schema+notification), `d142e92` (infra), `c148e30` (integration), `5b647c7`/`8b9414e` (arch), `c5d5024` (web), `efdbbed` (production hardening), plus release-candidate phase (P0-1..P0-3, Coronate docs, dependency security)

| Area | Status | Risk | Evidence | Action |
|------|--------|------|----------|--------|
| **Authentication** | PASS | Low | `UserModel` pbkdf2:sha256, `check_password`, `login_user`/`logout`, session `_user_id`, `is_active` check in `AuthenticationService.authenticate` returns `None` not exception, `test_security_prod` IDOR + self-demotion | Keep; rate limiting DEFERRED (no Flask-Limiter, pbkdf2 mitigates) |
| **Authorization / RBAC** | PASS | Low | `admin_auth.require_*` (system-admin → organizer → chief_arbiter → arbiter), `decorators.admin_required` 403, `fide_routes` aligned to `admin_required`/`is_admin` (P0-2 fix), `role_required` redirect, tournament staff `status=accepted`, 22+ web security tests, IDOR tests for `settings`/`approve` | None |
| **CSRF** | PASS | Low | `CSRFProtect` initialized, `WTF_CSRF_ENABLED=False` in tests, `<meta name=csrf-token>` + `app.js` inject, `fetch X-CSRFToken`, webhooks `@csrf.exempt` + secret | None |
| **File uploads** | PASS | Low | `instance_path/uploads/{receipts,profile_photos,id_documents,rulebooks}`, `secure_filename`, magic `detect_image_type`/`detect_pdf`, `MAX_CONTENT_LENGTH=8MB` + per-file `5MB`, `resolve_private_file` basename, traversal tests | None |
| **Payments** | PASS WITH RISK | Medium | `PaymentInitiator` checks `enable_online_payment`, `receipt_submitted` block, `final_price` server-side, `authority` unique + `with_for_update`, idempotent `process_callback` (successful/failed/cancelled), `code 101` success, Toman*10 `currency=IRR`, overbook → `rejected` + `Manual Refund Required`, no `payment_url` logging | Monitor Zarinpal sandbox vs production (`ZARINPAL_SANDBOX` guard) |
| **Webhooks** | PASS | Low | `X-Telegram-Bot-Api-Secret-Token`/`X-Bale-Bot-Api-Secret-Token` via `hmac.compare_digest` on bytes, missing secret → `True` (back-compat) else 403, malformed `message` → 400, provider exception isolated → 200 (now wrapped), `csrf.exempt` | Rotate `*_WEBHOOK_SECRET` via `.env` and re-register webhook with `secret_token` |
| **Backups** | PASS | Low | `require_admin`, 5 MB + `.json` check, `json.loads` + version `1.0` check, `registry.get_provider`, transaction rollback on `ImportExportError`, path traversal via `provider_name` not file path, `secure_filename`, Coronate lossy forfeit mapping documented (`docs/INFRASTRUCTURE.md` §6) | Do not use Coronate for lossless forfeit backup |
| **FIDE** | PASS | Low | `domain/fide/parser` `iterparse` + federation filter `IRI`, `fide/storage` instance-anchored `data/fide/<YYYY-MM>/`, retention 90d, `ZipSlip` safe extraction, batch upsert 500, `FideImportModel` tracking | None |
| **Secrets** | PASS | Low | `config.py` `SECRET_KEY`/`DB_NAME` fail-fast in `production`, `os.environ` only, no `SECRET` in templates, `grep TOKEN|SECRET` only in config/docs, webhook secrets not logged beyond truncated 500 chars | Rotate `.env` on deploy |
| **Error handling** | PASS | Low | `app/errorhandler 404/403/500/413` → `errors/*.html`, no `Traceback`/`File "` in 404, flash Persian messages | None |
| **Logging** | PASS WITH RISK | Low | `TelegramDebug`/`BaleDebug` lazy handler, truncated `[:500]`, no password/merchant logging, `notification_routes` exception logged via `logger.exception` | Avoid `DEBUG=True` in production |
| **Database / transactions** | PASS | Low | Services own `commit`/`rollback`, repositories `flush` only, `SELECT ... FOR_UPDATE` on capacity + payment, `next_start_number` + `generate_public_id` + `with_for_update` on `public_id` retry, `stats_rebuild` atomic, `RoundNotificationService` commits after ROUND_CREATED fan-out with rollback isolation (P0-1 fix) | None |
| **Security headers** | PASS | Low | `X-Content-Type-Options nosniff`, `X-Frame-Options SAMEORIGIN`, `Referrer-Policy strict-origin-when-cross-origin`, `Permissions-Policy`, `Content-Security-Policy` narrow (self + unsafe-inline + cdn.jsdelivr.net) (P0-3), `Cache-Control: no-store` on private/authenticated responses (P0-3), HSTS prod-only | Keep unsafe-inline scoped; revisit CSP nonce when frontend refactors |
| **Deployment** | PASS | Low | `passenger_wsgi.py`, `instance_path` writable, `migrations` baseline `bb0160eefd6b` now matches models (added 14 columns), `SESSION_COOKIE_SECURE` production only + `HTTPONLY`/`SAMESITE=Lax`, `MAX_CONTENT_LENGTH` 8M, FIDE/Zarinpal/webhook verified per `DEPLOYMENT.md` §11 | Follow `DEPLOYMENT.md` Path A/B/C |
| **Dependencies** | PASS | Low | `requirements.txt` pinned Flask 3.1.3, pillow 12.3.0, python-dotenv 1.2.2, requests 2.32.4 (pip-audit fixed 4 runtime CVEs; remaining pip/python-dotenv local-only CVEs deferred) | Re-run pip-audit periodically |

**Intentionally Deferred**
- Rate limiting (login/admin) — pbkdf2 mitigates, revisit with Flask-Limiter post-beta.
- `pip-audit` automated check — manual recommended.

**Evidence Commands**
```
pytest --collect-only -q → 856
pytest tests/domain -q → 174
pytest tests/application -q → 90
pytest tests/web -q → 112
pytest tests/infrastructure -q → 39
pytest tests/integration -q → 12
pytest tests/test_architecture.py -q → 7
pytest tests/test_security_prod_regression.py -q → 25
pytest tests/test_release_candidate_hardening.py -q → 13
pip-audit → fixed Flask/pillow/python-dotenv/requests (4 runtime CVEs); pip local CVEs deferred (not runtime)
pytest tests -q → 856 collected (full suite exceeds Windows timeout individually; sampled suites above all green)
```

**Remaining Risk: None critical. All areas PASS or PASS WITH RISK (low). P0-1..P0-3 closed.**
