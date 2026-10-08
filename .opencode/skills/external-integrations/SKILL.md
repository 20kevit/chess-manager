---
name: external-integrations
description: Integration boundaries for pairing-core, tiebreak-core, fide-service, Zarinpal payments, Telegram and Bale notifications, and Coronate import-export — ownership, pins, failure semantics, validation, and upgrade rules. Load when touching integrations or bumping pins.
---

# External Integrations — First-Class Boundaries

## pairing-core / tiebreak-core (correctness-critical)

Both are independent, stdlib-only, framework-free libraries (`20kevit/`);
neither imports the other or chess-manager.

- **Pins** (`requirements.txt`): `pairing-core@v0.4.1`,
  `tiebreak-core@v1.2.0`. Released tags only; clean-environment installs (no
  `PYTHONPATH`, editable, or local paths).
- **pairing-core boundary**: `application/round/round_lifecycle_service.py`
  (`SwissEngine`, `PlayerData`, `validate_round`) + `compute_color` helpers.
  `PlayerData` in → `RoundResult`/`PairingCard` out, nothing else. Repo owns
  adapter-building, persistence, seeding, withdrawal filtering, `pairing_no`.
  Zero pairing math locally (see `fide-compliance`).
- **tiebreak-core boundary**: `tiebreak_adapter.build_tiebreak_data` (the ONLY
  DB-reading adapter) → `calculate_all` / `rank_standings` →
  `StandingsService`. Production uses the frozen legacy behavior; the core's
  strict/ruleset APIs are NOT consumed — adopting one is a per-tournament
  config decision, never a silent global switch.
- **Upgrade process** (`NEW PROCESS — not previously documented`): pin a
  released tag; confirm clean install and API surface (`SwissEngine`,
  `PlayerData`, `validate_round`, determinism); for tiebreak-core also prove
  legacy-path byte-stability via
  `tests/application/test_standings_ranking_equivalence.py`.

## fide-service

Read-only HTTP client (`infrastructure/fide/service_client.py`): timeout +
TTL cache; any failure raises `FideServiceUnavailable` and callers fall back
to local importer data — admin pages never crash, never hard-depend on it.
Consumed via `application/fide/fide_status_service.py` (single status source).
The client never writes or triggers imports; local importer is the write path.
Config in `config.py`: `FIDE_SERVICE_URL` (default `127.0.0.1:5001`),
`FIDE_SERVICE_API_KEY`, `TIMEOUT=5`, `CACHE_TTL=300`.

## Concise operational rules

- **Zarinpal:** idempotent `process_callback`; `code 101` = success; Rial =
  Toman×10; overbook → manual-refund metadata, no auto-refunds; server-side
  `final_price` only. Production needs `ZARINPAL_SANDBOX=false` + real merchant
  UUID (startup guard). Verify per `docs/DEPLOYMENT.md` §13.
- **Notifications:** `NotificationService → NotificationDispatcher → providers`.
  Dispatcher checks tournament gates + user prefs; provider failure never
  crashes dispatch. When webhook secrets are set, registration with the matching
  `secret_token` is mandatory (`docs/DEPLOYMENT.md` §11); mismatch 403s every
  update. Links are 32-byte urlsafe tokens, 10-min expiry, single-use.
- **Coronate:** lossy for forfeits — never the authoritative backup for
  forfeit-heavy tournaments. 5 MB + `.json` checks, version check, rollback on
  `ImportExportError`.

## Source of truth

`docs/ARCHITECTURE.md`, `docs/INFRASTRUCTURE.md` §6, `docs/DEPLOYMENT.md`
§11/§13, `requirements.txt`, `config.py`.

## Validation

Cores: `tests/domain` + `test_round_lifecycle.py` +
`test_standings_ranking_equivalence.py` + `test_coronate_tiebreak_mapping.py`.
fide-service: `test_fide_status_service.py` + admin FIDE pages with the service
stopped. Payments: adjacent suites (mind the known `gateway` baseline cases in
`testing-validation`).

## Escalation

Escalate before bumping either pin, consuming a new core API/ruleset,
hard-depending on fide-service, or changing payment/notification semantics.
Unverifiable external behavior is marked `UNVERIFIED`.
