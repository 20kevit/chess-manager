# External Integrations — First-Class Boundaries

## Purpose

Keep the three correctness-critical external boundaries intact and give concise
operational rules for payments, notifications, and Coronate. Most integration
bugs here are silent FIDE or money bugs — verify at the boundary.

## When to use

Touching `pairing_core` / `tiebreak_core` imports, `requirements.txt` pins,
`FideServiceClient`, Zarinpal flow, notification dispatch, or Coronate
import/export. Read with `fide-compliance.md` for pairing/tiebreak tasks.

## Source of truth

- Boundary map: `docs/ARCHITECTURE.md` (ownership, data flow, integration table)
- Pins: `requirements.txt` (`pairing-core@v0.4.1`, `tiebreak-core@v1.2.0`)
- Infra contracts: `docs/INFRASTRUCTURE.md` §6 (incl. lossy Coronate table)
- Deployment: `docs/DEPLOYMENT.md` §11 (webhooks), §13 (Zarinpal verification)

## pairing-core (first-class)

- Ownership: independent `20kevit/pairing-core`, stdlib-only, framework-free.
  Neither core imports the other or chess-manager.
- Pinned source: `pairing-core @ git+https://github.com/20kevit/pairing-core.git@v0.4.1`.
- Integration point: `application/round/round_lifecycle_service.py`
  (`SwissEngine`, `PlayerData`, `validate_round`) plus `compute_color` helpers in
  `pairing_generation_service.py`. `PlayerData` in → `RoundResult`/`PairingCard`
  out; nothing else crosses.
- chess-manager owns: building `PlayerData` from Participant/Round/Pairing rows,
  persisting `PairingModel`/`RoundModel`, seeding, withdrawal filtering,
  `pairing_no` assignment. It owns zero pairing math.
- Upgrade process (`NEW PROCESS — not previously documented`): pin a released
  tag only; verify clean-environment install (no `PYTHONPATH`, no editable, no
  local path); confirm `SwissEngine`, `PlayerData`, `validate_round`,
  deterministic behavior still hold; then run the validation below.

## tiebreak-core (first-class)

- Ownership: independent `20kevit/tiebreak-core` (calculations + `rank_standings`
  comparator + rulesets). Pinned source: `.../tiebreak-core.git@v1.2.0`.
- Integration point: `application/tournament/tiebreak_adapter.py`
  (ONLY DB-reading adapter; owns `RESULT_SCORES` mapping and the virtual-opponent
  convention) → `tiebreak_core.calculate_all` / `rank_standings` →
  `StandingsService` (`application/tournament/standings_service.py`). Display
  names only may be imported by web code (`tiebreak_core.display`).
- Ruleset isolation: production uses the frozen legacy behavior; the core's
  strict/ruleset APIs (`fide-2024`, `fide-2026`) are NOT consumed. Adopting one
  is a per-tournament config decision, never a silent global switch.
- Upgrade process (`NEW PROCESS — not previously documented`): same discipline
  as pairing-core; additionally prove legacy-path byte-stability via
  `tests/application/test_standings_ranking_equivalence.py` before merging.

## fide-service (first-class)

- HTTP boundary: `infrastructure/fide/service_client.py` — thin read-only client
  (timeout + short TTL memoization). Failures raise `FideServiceUnavailable`;
  callers MUST fall back to local importer data and never crash an admin page.
- Consumed via `application/fide/fide_status_service.py` (single status source:
  healthy/stale/running/failed/never). Local importer remains the write path;
  the client never writes or triggers imports.
- Config (`config.py`, overridable via `.env`): `FIDE_SERVICE_URL` (default
  `http://127.0.0.1:5001`), `FIDE_SERVICE_API_KEY`, `FIDE_SERVICE_TIMEOUT=5`,
  `FIDE_STATUS_CACHE_TTL=300`.
- Validation: `tests/test_fide_status_service.py`; render admin FIDE pages with
  the service stopped to prove fallback.

## Concise operational rules (evidence-backed only)

- **Payments (Zarinpal):** idempotent `PaymentInitiator.process_callback`;
  `code 101` counts as success; Rial = Toman×10 (`currency=IRR`); overbook flags
  manual-refund metadata, no auto-refunds; server-side `final_price` only.
  Production requires `ZARINPAL_SANDBOX=false` + real merchant UUID (startup
  guard). Verify per `docs/DEPLOYMENT.md` §13.
- **Notifications:** `NotificationService → NotificationDispatcher → providers
  (Web/Telegram/Bale)`; dispatcher checks tournament gates + user prefs; a
  provider failure never crashes dispatch. Webhook secrets
  (`TELEGRAM/BALE_WEBHOOK_SECRET`), when set, are enforced via
  `hmac.compare_digest` — registration with the matching `secret_token` is
  mandatory (`docs/DEPLOYMENT.md` §11); mismatched registration 403s every
  update. Account links are 32-byte urlsafe tokens, 10-min expiry, single-use.
- **Coronate:** lossy for forfeits (see `fide-compliance.md`). 5 MB + `.json`
  checks, version check, transaction rollback on `ImportExportError`. Never use
  as the authoritative backup for forfeit-heavy tournaments.

## Validation

- Core changes: full `tests/domain` + `tests/application/test_round_lifecycle.py`
  + `tests/application/test_standings_ranking_equivalence.py` +
  `tests/application/test_coronate_tiebreak_mapping.py`.
- fide-service changes: `test_fide_status_service.py` + admin FIDE pages with
  service down. Payments: `tests/test_payment_flow.py`-adjacent suites
  (note the known `gateway` baseline failures — `testing-validation.md`).

## Escalation

Escalate before: bumping either core pin; consuming a new core API/ruleset;
making admin pages hard-depend on fide-service; or changing payment/notification
semantics. Mark any unverifiable external behavior `UNVERIFIED`.
