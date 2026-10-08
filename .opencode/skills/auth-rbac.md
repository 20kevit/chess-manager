# Authorization — Orthogonal Model, Not Tiers

## Purpose

Apply the actual authorization model. It is **not** "5-tier RBAC": authentication
state, global roles, per-tournament capabilities, and system-admin authority are
orthogonal axes. Conflating them causes both over-granting and under-granting.

## When to use

Any route, template, workspace page, or mutation touching tournaments, rounds,
players, registrations, payments, backups, staff, FIDE admin, or the management
workspace. Also any change to `admin_auth.py`, `decorators.py`, or staff logic.

## Source of truth

- Implementation: `interfaces/web/admin_auth.py` (the whole file, ~118 lines),
  `interfaces/web/decorators.py`, `interfaces/web/manage_routes.py:1-70`
- Models: `infrastructure/models/user.py` (`is_admin`, `has_role/has_any_role`),
  `infrastructure/models/staff.py` (`role`, `status`)
- Single-chief enforcement: `interfaces/web/dashboard_routes.py` (`add_staff`)
- Route matrix: `docs/WEB_ROUTES_LAYER.md` §4; workspace rules:
  `docs/FRONTEND_UI_LAYER.md` §16; invariant map: `AGENTS.md` §Critical Invariants
- Regression cover: `tests/test_manage_workspace.py`,
  `tests/test_staff_permission_matrix.py`, `tests/test_admin_authorization.py`

## The model (five concepts, three axes — use these exact names)

- **Authentication state.** Anonymous vs authenticated (`flask_login`). Public
  tournament pages (`tournament.view`, `crosstable`, `summary`, player/round
  public reads, print pages) render the SAME experience for every visitor and
  carry no management controls.
- **Global roles** (`UserRoleModel`: `player` | `organizer` | `arbiter`; default
  `player`). Gate creation-level actions: tournament creation requires the
  `organizer` role (`tournament/__init__.py:create`); backup create-from-backup
  endpoints require `@role_required("organizer")` (`backup_routes.py`).
  `role_required` denial = flash + redirect to dashboard (NOT 403).
  `UserModel.has_role/has_any_role` return True for system admins automatically.
- **Per-tournament manager capability** (`require_tournament_manager()`; the
  historical name `require_admin()` is an alias for this tier — NOT system
  admin). Granted to: system admin, OR `tournament.organizer_id == user.id`, OR
  **accepted** `chief_arbiter` staff row. Owns: settings, pricing, prizes,
  rulebook, announcements, player CRUD/import, registration decisions, round
  generation/deletion, backups, staff.
- **Per-tournament result-editor capability** (`require_result_editor()` =
  manager tier PLUS any **accepted** `arbiter` staff row). Owns the operational
  console: round views, result entry, finish round, bye requests, manual
  locks/swaps. Round generation/deletion stays manager-only by design.
- **System-admin authority** (`UserModel.is_admin`, `@admin_required`:
  anonymous → login redirect, non-admin → 403). Owns `/admin/*` and
  `/admin/fide/*` (users, all tournaments, FIDE import, verifications, health).
Distinguish precisely: a global `arbiter` **role** grants nothing
tournament-scoped; an accepted tournament `arbiter` **staff row** grants the
editor tier only; an accepted `chief_arbiter` staff row grants the manager tier;
the tournament **organizer** (creator) is manager of their tournaments; the
**system administrator** (`is_admin`) is manager/editor everywhere plus the
system console. `pending`/`rejected` staff rows grant nothing — only
`status="accepted"` counts. Exactly one accepted `chief_arbiter` per tournament
is enforced at application level in `dashboard_routes.add_staff` (DB-level
enforcement is only a commented proposal in `staff.py` — do not assume it).

## Backend-authoritative rules

- `capabilities(public_id)` → `(tournament, can_manage, can_edit_results)` is
  **render-only**: it never redirects or aborts. Public pages ignore the flags.
- Workspace navigation renders unavailable entries **disabled, not hidden**
  (`is-disabled`, `aria-disabled`, reason tooltip). Disabled UI is cosmetic.
- Every mutation sits behind `deny_or_login(public_id, tier=...)`:
  anonymous → login redirect; authenticated-but-denied → 403.
- Known contract: `GET /admin/fide/import/status` as an authenticated non-admin
  returns **403**, not 302 (pinned by a baseline test — see
  `testing-validation.md`). Do not "fix" routes to match the old 302 expectation.

## Validation

- `beta/.venv/bin/python -m pytest tests/test_manage_workspace.py tests/test_staff_permission_matrix.py tests/test_admin_authorization.py tests/web -q`
- For any auth change: exercise the matrix (anonymous / player / arbiter-staff /
  chief / organizer / system-admin) × (GET render vs POST mutation).

## Escalation

Escalate when a requirement asks for hidden-instead-of-disabled UI, per-role
public pages, secret-code/parallel auth mechanisms, or any new capability name
not evidenced in `admin_auth.py`. Never invent tiers.
