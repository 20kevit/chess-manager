# Web Routes — Agent Context

## Purpose
Flask Blueprint HTTP handlers. Auth, form handling, template rendering.

## Files
- admin_auth.py — Session auth + admin panel
- tournament_routes.py — Public views
- round_routes.py — Round management (session auth)
- player_routes.py — Player management (session auth)
- backup_routes.py — JSON backup/restore (session auth)
- print_routes.py — Print pages + TRF export (public)
- helpers.py — Shared utilities (build_cell)
- error_handlers.py — Centralized error decorator

## Auth Pattern
All admin routes use require_admin(public_id) from admin_auth.py.
Returns tournament object or None.
Pattern in each route:
```python
tournament, redir = _require_admin_or_redirect(public_id)
if redir:
    return redir
```

## Route Map
See docs/PROJECT.md for complete route table.