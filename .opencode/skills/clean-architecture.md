# Clean Architecture — Layer Boundaries

## Purpose

Prevent layer violations in `chess-manager`. Every code change must respect the
dependency direction below. Most "quick fixes" that break this app break it here.

## When to use

Any task that adds, moves, or edits Python code outside `tests/`. Read this first,
then the deep doc for the layer being changed.

## Source of truth

- `AGENTS.md` → §Architecture & Dependency Rules, §Where Should This Code Go
- `docs/AGENT_INSTRUCTIONS.txt` (strict MUST/MUST NOT checklist)
- `docs/APPLICATION.md` §8 (application rules), `docs/INFRASTRUCTURE.md` §3,
  `docs/DOMAIN.md` §2-3, `docs/WEB_ROUTES_LAYER.md` §3
- Enforcement: `tests/test_architecture.py` (import-direction regression tests)

## Repository-specific rules

Dependency direction (strict, verified in code):

```
interfaces/web  →  application  →  domain  +  infrastructure
```

- `domain/` — pure Python (stdlib only). MUST NOT import `flask`, `sqlalchemy`,
  `infrastructure`, `interfaces/web`, or `application`. Pairing/tiebreak math lives
  in the external `pairing-core` / `tiebreak-core` packages, not here
  (see `fide-compliance.md`; ownership: `docs/ARCHITECTURE.md`).
- `application/` — use-case orchestration. **Exclusive owner of transactions**
  (`db.session.commit()` / `rollback()`). MUST NOT import `interfaces/web` or
  `flask.request`. Must not reimplement pairing/tiebreak/rating logic.
- `infrastructure/` — models, repositories, external I/O. Repositories use
  `db.session.flush()` **only** — never `commit`/`rollback`. No business rules,
  no FIDE logic, no Flask `request`/`session`.
- `interfaces/web/` — HTTP only: parse request → capability check → call an
  `application.*` service → `flash()` + `redirect()` or `render_template()`.
  No business rules, no `Model.query.*` in new code (existing direct queries are
  grandfathered tech-debt, not a pattern), no transaction management.

**Facade rule.** `application/*_service.py` and `infrastructure/db_models.py` /
`repositories.py` are thin backward-compatibility facades delegating 1:1 to the
new packages (delegation tables: `docs/APPLICATION.md` §4). New code imports from
the package (`from application.tournament import TournamentConfigService`).
Never add logic to a facade. Circular imports between `application` packages are
forbidden.

## Workflow

1. Classify the change using the "Where Should This Code Go?" table in `AGENTS.md`.
2. Open only the owning layer's files plus its immediate neighbor (caller or callee).
3. If the change needs data across layers, pass plain data at the boundary
   (e.g. `PlayerData` in → `RoundResult` out); do not leak ORM objects into
   `domain/` or Flask objects into `application/`.

## Validation

- `beta/.venv/bin/python -m pytest tests/test_architecture.py -q` (import-direction gates)
- Focused suite for the touched layer (`testing-validation.md`).
- New unit tests for `domain/` changes must run without Flask app context or DB.

## Do not assume

- Do not assume Clean Architecture from doc titles — verify the import exists.
- Do not assume a facade is the implementation — read the delegating package.
- Do not "fix" a boundary by adding a reverse import; restructure instead.

## Escalation

Stop and escalate when a task genuinely requires a cross-layer import, a new
`application` ↔ `application` dependency, or logic in a facade. Mark the tension
`UNRESOLVED`; do not silently violate the direction.

## Maintenance / update triggers

Update this Skill when `tests/test_architecture.py` gains/removes a rule, when a
facade is finally deleted, or when a layer's ownership changes in `AGENTS.md`.
