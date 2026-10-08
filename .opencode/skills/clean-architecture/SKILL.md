---
name: clean-architecture
description: Layer boundaries for chess-manager changes — web to application to domain/infrastructure dependency direction, transaction ownership, repository flush-only rule, and facade delegation. Load before adding, moving, or editing any Python code outside tests.
---

# Clean Architecture — Layer Boundaries

## When to use

Any task that adds, moves, or edits Python code outside `tests/`. Classify the
change first (`AGENTS.md` §Where Should This Code Go), then read the deep doc
for the owning layer only.

## Direction (strict, enforced by `tests/test_architecture.py`)

```
interfaces/web  →  application  →  domain  +  infrastructure
```

- `domain/` — stdlib-only. No `flask`, `sqlalchemy`, `infrastructure`,
  `interfaces/web`, `application`. Pairing/tiebreak math lives in the external
  cores, not here (see `fide-compliance`).
- `application/` — **exclusive owner of transactions** (`commit`/`rollback`).
  No `interfaces/web` or `flask.request`. No pairing/tiebreak/rating logic.
- `infrastructure/` — models, repositories, external I/O. Repositories use
  `db.session.flush()` **only**. No business rules, no FIDE logic, no Flask
  `request`/`session`.
- `interfaces/web/` — HTTP only: parse request → capability check → call an
  `application.*` service → `flash()` + `redirect()` or `render_template()`.
  No business rules, no new `Model.query.*` (existing ones are grandfathered
  tech-debt, not a pattern), no transaction management.

## Facade rule

`application/*_service.py`, `infrastructure/db_models.py`, and `repositories.py`
are thin 1:1 delegation facades (tables: `docs/APPLICATION.md` §4). New code
imports the package (`from application.tournament import ...`). Never add logic
to a facade; no circular imports between `application` packages.

## Source of truth

`AGENTS.md` (§Architecture, §Where Should This Code Go),
`docs/AGENT_INSTRUCTIONS.txt`, `docs/APPLICATION.md` §8,
`docs/INFRASTRUCTURE.md` §3, `docs/DOMAIN.md` §2–3.

## Validation

- `pytest tests/test_architecture.py -q` plus the focused suite for the touched
  layer (see `testing-validation`).
- `domain/` unit tests must run without Flask context or DB.

## Do not assume

Verify imports exist — never infer direction from filenames. A facade is not
the implementation. Never fix a boundary with a reverse import.

## Escalation

Stop and mark `UNRESOLVED` when a task needs a cross-layer import, a new
`application` ↔ `application` dependency, or logic in a facade.
