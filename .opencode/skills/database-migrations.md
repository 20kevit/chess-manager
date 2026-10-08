# Database & Migrations — Alembic Chain Discipline

## Purpose

Keep schema changes safe across three very different targets (fresh install,
existing production DB, dev reset). The migration chain has a squashed baseline
with folded-in columns — the wrong command here silently no-ops on production.

## When to use

Any model change, new table, migration edit, deployment involving schema, or
`flask db` command. Read before touching `infrastructure/models/`,
`migrations/versions/`, or production data.

## Source of truth

- Chain: `migrations/versions/` — `bb0160eefd6b` (squashed baseline, 22 tables)
  → `c41a9e2b07d3` (beta delta) → `f3d8a1c47e2b` (healing delta, current head).
- Runbook: `docs/DEPLOYMENT.md` §6-7 (upgrade + `db check`), §14 (chain + Path
  A/B/C + guarded ALTERs).
- Config: `config.py` (MySQL via `DB_*` utf8mb4 + pool options; else local
  SQLite; production fail-fast on missing `SECRET_KEY`/`DB_NAME`).
- Contracts: `docs/INFRASTRUCTURE.md` §4-5, §8-9 (model/repository rules).

## The three targets — pick exactly one

- **Path A — fresh install (empty MySQL):** `flask --app run.py db upgrade`
  runs the whole chain; then `flask --app run.py db check` must report no
  pending operations.
- **Path B — existing production DB:** `db upgrade` may be a **no-op** (already
  stamped at head, including DBs whose columns were folded into the baseline in
  place). Apply additive NULLable `ADD COLUMN` / `CREATE TABLE IF NOT EXISTS`
  statements manually via the guarded idempotent pattern in `DEPLOYMENT.md` §14.
  Guarded, re-runnable, no drops, no type changes, no data loss. Verify row
  counts before/after, then `db check`, then restart Passenger.
- **Path C — dev reset only:** `python reset_db.py` (`drop_all` + `create_all`
  from models, no migration involved). Local/throwaway environments only.
  NEVER run on production or beta.

## Rules

- NEVER edit a released revision. Model changes go through
  `flask --app run.py db migrate -m "..."` (review the generated file —
  SQLite ALTERs may need batch mode), then `db upgrade`, then `db check`.
- New models: correct domain module under `infrastructure/models/`, inherit
  `db.Model`, `__table_args__` with mysql charset/collate, export from
  `models/__init__.py` + `infrastructure/__init__.py`, add a matching
  flush-only repository. No business logic in models; no `commit`/`rollback`
  in repositories. No destructive migrations (drops, renames, type changes)
  without an explicitly approved, backed-up plan.
- Because the baseline revision ID was preserved while columns were folded in,
  Alembic cannot distinguish pre-fold from post-fold databases — always confirm
  actual columns (e.g. `player_profiles.phone/photo_path/id_document_path`,
  `tournaments.registration_requirements/rulebook_sections/rulebook_pdf_path/
  notification_prefs`, `fide_imports.stage/progress_percent`), never trust the
  stamp alone.
- All runtime-writable paths are instance-anchored (`instance/uploads/*`,
  `instance/data/fide/<YYYY-MM>/`); never CWD-dependent.

## Validation

- `flask --app run.py db check` → `No new upgrade operations detected.`
- `tests/test_deployment_schema.py`, `tests/test_baseline_checkpoint.py`,
  `tests/test_deployment_paths.py` (note: two baseline failures are known and
  documented in `testing-validation.md` — do not re-baseline tests to hide drift).
- Rollback is limited: Alembic downgrades exist per revision but production
  Path-B manual ALTERs have no automatic down-migration — plan restores from
  backups, not from `downgrade`.

## Escalation

Escalate when: a migration would drop/rename/alter a column type; the stamp
says current but columns disagree; `db check` reports pending operations after
an upgrade; or a production change cannot be expressed as additive + nullable.
Mark the schema state `UNVERIFIED` until inspected directly.
