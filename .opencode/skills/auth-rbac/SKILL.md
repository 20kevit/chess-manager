---
name: auth-rbac
description: Authorization model for chess-manager — authentication state, global roles, per-tournament manager versus result-editor capabilities, system-admin authority, workspace rules, and denial semantics. Load for any route, template, workspace, or mutation change.
---

# Authorization — Orthogonal Model, Not Tiers

This is **not** "5-tier RBAC": authentication state, global roles,
per-tournament capabilities, and system-admin authority are orthogonal axes.
Conflating them over- or under-grants access.

## The model (exact names from `interfaces/web/admin_auth.py`)

- **Authentication state.** Public tournament pages (`tournament.view`,
  `crosstable`, `summary`, public round/player reads, print pages) render the
  SAME experience for every visitor and carry no management controls.
- **Global roles** (`UserRoleModel`: `player` | `organizer` | `arbiter`; default
  `player`). Tournament creation requires the `organizer` role; backup
  create-from-backup endpoints require `@role_required("organizer")`.
  `role_required` denial = flash + dashboard redirect (**not** 403).
  `has_role`/`has_any_role` return True for system admins automatically.
- **Manager capability** (`require_tournament_manager()`; the historical name
  `require_admin()` is an alias for this tier — NOT system admin). Granted to:
  system admin, OR `tournament.organizer_id == user.id`, OR **accepted**
  `chief_arbiter` staff row. Owns settings, pricing, prizes, rulebook,
  announcements, player CRUD/import, registration decisions, round
  generation/deletion, backups, staff.
- **Result-editor capability** (`require_result_editor()` = manager tier PLUS
  any **accepted** `arbiter` staff row). Owns the result console: round views,
  result entry, finish round, byes, manual locks/swaps. Generation/deletion
  stays manager-only by design.
- **System-admin authority** (`UserModel.is_admin`, `@admin_required`:
  anonymous → login redirect, non-admin → 403). Owns `/admin/*` and
  `/admin/fide/*`.

A global `arbiter` **role** grants nothing tournament-scoped; an accepted
tournament `arbiter` **staff row** grants editor only; an accepted
`chief_arbiter` row grants manager. Only `status="accepted"` counts —
`pending`/`rejected` grant nothing. One accepted `chief_arbiter` per tournament
is enforced in `dashboard_routes.add_staff` (application level; DB enforcement
is only a commented proposal in `staff.py` — do not assume it).

## Backend-authoritative rules

- `capabilities()` → `(tournament, can_manage, can_edit_results)` is
  **render-only** (never redirects/aborts). Public pages ignore the flags.
- Workspace entries render **disabled, not hidden** (`is-disabled`,
  `aria-disabled`, reason tooltip). Disabled UI is cosmetic, never authorization.
- Every mutation sits behind `deny_or_login(tier=...)`: anonymous → login
  redirect; denied → 403.
- Contract: authenticated non-admin hitting `/admin/fide/import/status` gets
  **403**, not 302 — do not "fix" routes toward the old expectation.

## Source of truth

`interfaces/web/admin_auth.py`, `interfaces/web/decorators.py`,
`interfaces/web/manage_routes.py:1-70`, `infrastructure/models/user.py`,
`infrastructure/models/staff.py`, `docs/WEB_ROUTES_LAYER.md` §4,
`docs/FRONTEND_UI_LAYER.md` §16.

## Validation

`pytest tests/test_manage_workspace.py tests/test_staff_permission_matrix.py
tests/test_admin_authorization.py tests/web -q`, exercising the matrix
(anonymous / player / arbiter-staff / chief / organizer / system-admin) × (GET
render vs POST mutation).

## Escalation

Escalate hidden-instead-of-disabled UI, per-role public pages, parallel auth
mechanisms, or any capability name not evidenced in `admin_auth.py`.
