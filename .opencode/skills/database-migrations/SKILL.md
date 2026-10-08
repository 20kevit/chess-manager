---
name: database-migrations
description: Migration safety for chess-manager — Alembic chain, fresh-install versus existing-database versus dev-reset paths, released-revision discipline, and schema verification. Load before any model, migration, or deployment-schema change.
---

# Database & Migrations — Chain Discipline

The chain has a squashed baseline with folded-in columns: the stamp alone does
not tell you the schema. The wrong command silently no-ops on production.

## Chain (`migrations/versions/`)

`bb0160eefd6b` (squashed baseline) → `c41a9e2b07d3` (beta delta) →
`f3d8a1c47e2b` (healing delta, head). Details and guarded SQL:
`docs/DEPLOYMENT.md` §6–7, §14. Config: `config.py` (MySQL utf8mb4 via `DB_*`,
else local SQLite; production fail-fast).

## Three targets — pick exactly one

- **Fresh install (empty MySQL):** `flask --app run.py db upgrade`, then
  `flask --app run.py db check` must report no pending operations.
- **Existing production DB:** `db upgrade` may be a **no-op** (already stamped
  at head). Apply additive NULLable `ADD COLUMN` / `CREATE TABLE IF NOT EXISTS`
  manually via the guarded idempotent pattern in `DEPLOYMENT.md` §14. No drops,
  no type changes. Verify row counts before/after, then `db check`, then
  restart Passenger.
- **Dev reset only:** `python reset_db.py` (`drop_all` + `create_all`, no
  migration). Local/throwaway environments only — NEVER production or beta.

## Rules

- NEVER edit a released revision. Model changes: `flask --app run.py db
  migrate -m "..."` (review the file; SQLite ALTERs may need batch mode) →
  `db upgrade` → `db check`.
- New models: correct domain module under `infrastructure/models/`, `db.Model`,
  `__table_args__` with mysql charset/collate, exports, matching flush-only
  repository. No business logic in models; no `commit`/`rollback` in
  repositories (`docs/INFRASTRUCTURE.md` §8–9).
- Confirm actual columns (e.g. `player_profiles.phone/photo_path/
  id_document_path`, `tournaments.registration_requirements/rulebook_sections/
  rulebook_pdf_path/notification_prefs`, `fide_imports.stage/progress_percent`)
  — never infer schema from the stamp.
- Runtime-writable paths are instance-anchored, never CWD-dependent.

## Validation

`db check` → no pending operations; `test_deployment_schema.py`,
`test_baseline_checkpoint.py`, `test_deployment_paths.py` (known drift cases
are recorded in `testing-validation` — do not re-baseline tests to hide
drift). Production Path-B ALTERs have no automatic downgrade — plan restores
from backups.

## Escalation

Escalate drops/renames/type changes, stamp-vs-columns disagreement, pending
operations after upgrade, or any non-additive production change. Mark schema
state `UNVERIFIED` until inspected directly.
