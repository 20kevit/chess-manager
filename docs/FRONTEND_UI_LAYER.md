# Frontend / Web UI Layer — Authoritative Architectural Map

> **Purpose.** This document is the single architectural map of the entire frontend and `interfaces/web/` layer. A developer or AI agent should be able to read *only* this file and know (a) how the web layer is structured, (b) which route group owns which templates, CSS and JS, (c) which files are global vs. feature-scoped, (d) how data flows Flask → Jinja → HTML/CSS/JS, and (e) *which files to open* before touching anything. It is **not** a line-by-line inventory — it documents *relationships, ownership, boundaries and blast radius*.

> **Invariant.** All paths below are verified against the current tree on `2026-08-30`. Template inheritance, `extra_css`/`extra_js` blocks and `url_for('static', ...)` references were grepped from the live `templates/` and `static/` directories. Do not document the pre-refactor inline-CSS/JS architecture as if it still exists.

---

## 1. Frontend Architecture Overview

### End-to-end flow

```
Browser ──HTTP──► Flask Blueprint (interfaces/web/) ──► Application Service (application/*)
                                              │
                                              ▼
                                    Jinja Template (templates/**/*.html)
                                              │
                                   ┌──────────┴──────────┐
                                   │                     │
                                  HTML               data-* attrs / JSON
                                   │                     │
                          ┌────────┴────────┐   ┌────────┴────────┐
                          │ CSS (static/css)│   │ JS (static/js)  │
                          └─────────────────┘   └─────────────────┘
                                              │
Browser ◄── rendered HTML + linked assets ────┘
```

* `interfaces/web/` **never** touches the DB directly. It validates auth/capability (`admin_auth.py`, `decorators.py`), parses `request.form` / `request.args`, delegates to an `application.*` service, then calls `render_template(...)` or `redirect(...)`. Direct `Model.query` from a view is an exception and should be treated as tech-debt to fix.
* `application/` owns all transactions (`commit`/`rollback`) and business rules. It calls `infrastructure/repositories/` and `domain/` — never the reverse.
* `infrastructure/` and `domain/` are invisible to the browser. Templates only see the DTOs / ORM objects that the service chose to pass.
* `templates/` consume what the route passes. `static/css` and `static/js` are vanilla — no React, Vue, jQuery, TypeScript, npm or bundler. RTL Persian, Vazirmatn.

### The five frontend-relevant trees

| Tree | Role | Imports from | Must NOT import |
|------|------|--------------|-----------------|
| `interfaces/web/` | Flask blueprints / route handlers | `application.*`, `infrastructure.*` (read-only ideally), `domain.*` (tiebreak constants) | `domain` business flow beyond constants; `templates` directly |
| `templates/` | Jinja2 HTML | Context vars from route; `url_for()`; CSS/JS via `static/` | `db`, `repositories`, `domain` |
| `static/css/` | Stylesheets, CSS variables | Nothing (pure) | JS |
| `static/js/` | Vanilla JS modules | DOM, `fetch`, `meta[name=csrf-token]`, `data-*` attrs | Jinja (except one tiny config shim — see §10) |
| `application/` | Services | `domain`, `infrastructure` | `interfaces/web` (strict), Flask `request` |

Blueprint registration lives in `app/__init__.py:87-113`. All 14 blueprints are registered with **no `url_prefix`** — each route string is its full URL (see §2). Error handlers (403/404/500/413), `toman_formatter` filter and the `unread_notifications_count` context processor are also registered there.

---

## 2. Web Layer (`interfaces/web/`) Map

All files under `interfaces/web/` (verified with `glob "interfaces/web/**/*.py"`):

| File / Blueprint | Blueprint var | Public / Auth scope | Responsibility — what kind of pages/endpoints it owns |
|------------------|---------------|---------------------|--------------------------------------------------------|
| `tournament/__init__.py` | `tournament_bp` | **Public** (`/`, `/<public_id>`, `/search`, `/uploads/rulebook/...`) + **Manager** (`/<public_id>/settings`, `/admin/announcements`, `/admin/notification-prefs`, `/admin/prizes`, `/settings/rulebook`) | The centre of the product. Public views: `index`, `view` (unified arbiter/public page — see §16), `player_detail`, `crosstable`, `summary`, `search`. Manager views: `settings`, `announcements`, `notification_prefs`, `prize_settings`, `rulebook_settings`, rulebook PDF upload/remove, rulebook public download. Owns ~15 `tournament/*.html` templates. |
| `round_routes.py` | `round_bp` | **Result-editor** (`/<public_id>/rounds`, `/<public_id>/rounds/<n>`, `/request-bye`, `/manual-pairing/*`) + **Manager** (`/rounds/new`, `/rounds/<n>/delete`) | Swiss lifecycle UI. `round_list`, `round_view` (result `<select>`s), `save_results`, `finish_round`, `delete_round`, bye/lock management (`request_bye`, `manual_pairing_add/remove`, `cancel_bye`) and post-pairing swaps (`manual_pairing`). Owns `tournament/rounds.html`, `round_view.html`, `request_bye.html`, `manual_pairing*.html`. |
| `player_routes.py` | `player_bp` | **Manager** (`/<public_id>/players*`) | Participant CRUD owned by `ParticipantManagement`. `players`, `player_add`, `player_edit`, `player_delete`, `player_withdraw`, `player_import` (CSV + template download). |
| `registration_routes.py` | `registration_bp` | **Public/auth** (`/<public_id>/register`, `/<public_id>/api/calculate_price`) + **Manager** (`/<public_id>/admin/pricing`, `/admin/registrations*`) | Pricing/eligibility surface. Public price-calc JSON API + self-registration form; manager pricing editor, promo-code CRUD, registration queue (`registrations`, `approve`, `reject`, `reject-receipt`). Uses `RegistrationCreator / EligibilityChecker / PricingCalculator`. |
| `payment_routes.py` | `payment_bp` | **Auth** (`/registration/<id>/pay`, `/payment/callback`) | Thin Zarinpal facade: `initiate_payment` (POST → redirect to gateway) and idempotent `callback` (GET). No template — redirects back to `tournament.view` / registration page. |
| `dashboard_routes.py` | `dashboard_bp` | **Auth** (`/dashboard`, `/dashboard/tournament/...`, `/dashboard/profile/...`, `/uploads/profile-photo/...`, `/dashboard/api/search-users`, `/dashboard/verification/request`) | Authenticated user hub. `index` (organiser/player cards, invitations, available tournaments — the P0-D filtered list), `manage_tournament` (staff hub), profile CRUD + private media upload/remove/serve, FIDE search proxy, invitation accept/reject, verification request, notification preferences (`/dashboard/notifications/settings`). Owns `dashboard/*.html`. |
| `admin_routes.py` | `admin_bp` | **System-admin** (`/admin`, `/admin/users*`, `/admin/tournaments`, `/admin/notifications`, `/admin/system`) | Platform super-admin. `dashboard` (stats), `manage_users` (search/filter/pagination), `user_detail` + role/admin toggles, `manage_tournaments`, notification status, system health. Owns `admin/*.html` *except* FIDE/verification. |
| `fide_routes.py` | `fide_bp` | **System-admin** (`/admin/fide`, `/admin/fide/import*`, `/admin/fide/verifications*`) | Monthly FIDE XML import UI + FIDE search + verification approval queue (`verifications`, `approve`, `reject`, `verify_fide_id/dob/photo`). Owns `admin/fide_dashboard.html`, `admin/verifications.html`. |
| `notification_routes.py` | `notification_bp` | **Auth** (`/notifications`, `/api/notifications*`) + **Webhook** (`/api/telegram/webhook`, `/api/bale/webhook`) + **Auth** (`/dashboard/notifications/telegram|bale/connect|disconnect`) | Dual purpose: user-facing inbox + provider webhooks. Renders `notifications/index.html` + `connect_provider.html`; JSON APIs for dropdown + mark-read; signed webhook entry points for Telegram/Bale. |
| `player_profile_routes.py` | `player_profile_bp` | **Public** (`/player/<identifier>`) | Single public profile page (`player/public_profile.html`) — `identifier` is FIDE ID if verified else internal ID. Privacy-filtered. |
| `print_routes.py` | `print_bp` | **Public** (`/<public_id>/print/*`, `/<public_id>/export/trf`) | Print-oriented renderings isolated from the screen UI: `print/standings.html`, `print/round.html`, `print/crosstable.html` (all extend `print/base.html`) + TRF export endpoint. No auth; shareable URLs. |
| `backup_routes.py` | `backup_bp` | **Manager** (`/<public_id>/admin/backup/*`, `/<public_id>/backup/*`) + **Auth** (`/create/from-backup/*`, `/create/execute/*`) | Coronate JSON import/export. `backup_options`, `backup_import`, `import_from_backup`, `export/<provider>`, `import/<provider>`, `from-backup` (preview JSON), `execute` (materialise). Uses `application.import_export` + `infrastructure/providers/coronate_*`. |
| `auth_routes.py` | `auth_bp` | **Public** (`/register`, `/login`, `/logout`) | Email+password auth. `register`, `login` (with safe `next` redirect), `logout`. Owns `auth/*.html`. Default role `player`. No email verification. |
| `decorators.py` / `admin_auth.py` / `helpers.py` | — | — | **Not blueprints.** `require_admin()` / `require_tournament_manager()` / `require_result_editor()` — the canonical capability checks used by *every* protected route. Order: system-admin → organiser → accepted `TournamentStaffModel` → legacy `session["admin_<public_id>"]`. `role_required(*roles)` / `admin_required` are the global Flask decorators. |

Empty package stubs exist but define no routes: `interfaces/web/admin/__init__.py`, `api/__init__.py`, `dashboard/__init__.py`, `registration/__init__.py`, `round/__init__.py`.

**Access tiers in one glance**

* **Public** — `tournament.index`, `tournament.view/crosstable/summary/player_detail/search`, `auth.register/login`, `player_profile`, `print/*`, `registration.register` (read), `tournament.download_rulebook_pdf`. No login required.
* **Authenticated** — `dashboard.index/manage_tournament`, `registration.register` (POST), `payment.*`, `notification.index`, `fide dashboard search` (scoped).
* **Tournament-manager** (organiser / chief arbiter / system-admin) — `tournament.settings/*`, `round.round_new/delete`, `player.*`, `registration.admin/*`, `backup.*`, `round.request_bye/manual*`.
* **Result-editor** (manager tier **plus** ordinary arbiter with accepted invite) — `round.round_list/view`, `round.save_results/finish_round`, `round.request_bye/manual*` (read + write of results/byes/locks). Deleting/generating rounds is intentionally *manager-only*.
* **System-admin** — `admin.*`, `fide.*` (import + verifications).
* **Webhook / API** — `/api/notifications`, `/dashboard/api/search-users`, `/dashboard/api/fide-search`, `registration.calculate_price`, `/api/telegram|bale/webhook` (HMAC-checked via `*_WEBHOOK_SECRET`).

---

## 3. Route → Template Relationships

> Read this when you change a route and need to know which templates will break, or when you change a template and need to know which routes feed it.

### `tournament` (`tournament/__init__.py`)

| Route handler | Method | Template rendered |
|---------------|--------|-------------------|
| `index()` | GET `/` | `index.html` |
| `create()` | GET/POST `/create` | `tournament/create.html` (form) → `tournament/created.html` (success + public/admin URLs) |
| `view()` | GET `/<public_id>` | `tournament/view.html` — the unified page (standings tabs + rounds + crosstable + summary + rulebook). Context: `tournament`, `is_admin/can_manage/can_edit_results`, `player_standings/tiebreak_rules`, `rating_changes`, `rulebook_sections`, `prize_summary`. The most coupled template in the project. |
| `player_detail()` | GET `/<public_id>/player/<int:participant_id>` | `tournament/player_detail.html` |
| `crosstable()` | GET `/<public_id>/crosstable` | `tournament/crosstable.html` |
| `summary()` | GET `/<public_id>/summary` | `tournament/summary.html` |
| `search()` | GET `/search?q=` | `search.html` |
| `settings()` | GET/POST `/<public_id>/settings` | `tournament/settings.html` (basic + dates + time control + tiebreak DnD) |
| `announcements()` | GET/POST `/<public_id>/admin/announcements` | `tournament/announcements.html` |
| `notification_prefs()` | GET/POST `/<public_id>/admin/notification-prefs` | `tournament/notification_prefs.html` |
| `prize_settings()` | GET/POST `/<public_id>/admin/prizes` | `tournament/prize_settings.html` |
| `prize_recompute` | POST `/<public_id>/admin/prizes/recompute` | redirect → `prize_settings` |
| `rulebook_settings()` | GET/POST `/<public_id>/settings/rulebook` | `tournament/rulebook_settings.html` |
| `upload_rulebook_pdf()` / `remove_rulebook_pdf()` | POST `/settings/rulebook/pdf*` | redirect → `rulebook_settings` |
| `download_rulebook_pdf()` | GET `/uploads/rulebook/<public_id>` | `send_file` (no template — PDF bytes) |

### `round` (`round_routes.py`)

| Handler | Template |
|---------|----------|
| `round_list()` | `tournament/rounds.html` |
| `round_view()` | `tournament/round_view.html` (board table + result `<select>`s + finish/delete) |
| `round_new()` / `delete_round()` | redirect → `tournament.view` / `round_list` (no template — flash + redirect) |
| `request_bye()` | `tournament/request_bye.html` (bye + manual lock queue for `next_round`) |
| `manual_pairing()` | `tournament/manual_pairing.html` (post-pairing color/swap) |

`save_results`, `finish_round`, `manual_pairing_add/remove`, `cancel_bye` are POST-only and redirect.

### `player` (`player_routes.py`)

| Handler | Template |
|---------|----------|
| `players()` | `tournament/players.html` |
| `player_add()` / `player_edit()` | `tournament/player_add.html`, `tournament/player_edit.html` |
| `player_import()` | `tournament/player_import.html` (CSV file + preview) ; `player_import/template` streams CSV |
| delete/withdraw | redirect → `players` |

### `registration` (`registration_routes.py`)

| Handler | Template |
|---------|----------|
| `register()` | `tournament/register.html` (public self-registration + price box) |
| `pricing()` | `tournament/pricing.html` |
| `registrations()` | `tournament/registrations.html` (manager queue) |
| `admin_pricing` / `promo_add/delete` | `tournament/pricing.html` (same template, different POST targets) |
| `calculate_price` | JSON (`/ <public_id>/api/calculate_price`) — consumed by `registration.js` |
| `upload_receipt` / `discard_receipt` / `reject_receipt` / `approve/reject` | redirect → `register` or `registrations` |
| `download_receipt` | `send_file` (private, `instance/uploads/receipts`) |

### `dashboard` (`dashboard_routes.py`)

| Handler | Template |
|---------|----------|
| `index()` | `dashboard/index.html` (hub: my_tournaments, invitations, assigned, registrations, participations, profile) |
| `manage_tournament()` | `dashboard/manage_tournament.html` (staff hub + user search) |
| `search_profile()` | re-renders `dashboard/index.html` with `search_results` |
| `create_profile()` | `dashboard/create_profile.html` |
| `request_verification()` | `dashboard/verification_request.html` |
| `notification_settings()` | `dashboard/notification_settings.html` |
| `update_profile` / `link_profile` / media upload/remove / `search_users` / staff add/remove / invitation accept/reject / `dashboard_fide_search` / `withdraw_from_participation` | redirect or JSON (`/dashboard/api/search-users`, `/dashboard/api/fide-search`) |

### `admin` + `fide`

| Handler | Template |
|---------|----------|
| `admin.dashboard` | `admin/dashboard.html` |
| `admin.manage_users` / `user_detail` | `admin/users.html`, `admin/user_detail.html` |
| `admin.manage_tournaments` | `admin/tournaments.html` |
| `admin.notification_status` | `admin/notifications.html` |
| `admin.system_health` | `admin/system.html` |
| `fide.fide_dashboard` / `fide.search` | `admin/fide_dashboard.html` (+ JSON `/admin/fide/search?q=`) |
| `fide.verifications*` | `admin/verifications.html` (+ POST approve/reject/verify_* → redirect) |
| `fide.import` / `fide.import_status` | JSON + redirect (async thread) |

### `auth` / `notification` / `player_profile` / `print` / `backup`

| Blueprint | Handlers → Templates |
|-----------|----------------------|
| `auth` | `register` → `auth/register.html`, `login` → `auth/login.html`, `logout` → redirect |
| `notification` | `index` → `notifications/index.html`, `connect_provider` → `notifications/connect_provider.html`; `/api/notifications*` → JSON; webhooks → 200/403; provider connect/disconnect → redirect |
| `player_profile` | `public_profile` → `player/public_profile.html` |
| `print` | `print_standings` → `print/standings.html`, `print_round` → `print/round.html`, `print_crosstable` → `print/crosstable.html`, `export_trf` → text response |
| `backup` | `backup_options` → `tournament/backup_options.html`, `backup_import` → `tournament/backup_import.html`, `import_from_backup` → `tournament/import_from_backup.html` ; `/create/from-backup/*` → JSON (consumed by `backup_import.js`); `/create/execute/*` → redirect |

Error handlers in `app/__init__.py:128-137` render `errors/404.html`, `errors/403.html`, `errors/500.html` for every blueprint.

---

## 4. Template Inheritance Architecture

```
base.html  ─────────────────────────── the only global layout
  │
  ├── index.html, search.html
  ├── auth/login.html, auth/register.html
  ├── errors/403.html, 404.html, 500.html
  ├── tournament/view.html, crosstable.html, summary.html, player_detail.html, …
  ├── tournament/register.html, registrations.html, pricing.html, …
  ├── tournament/rounds.html, round_view.html, request_bye.html, manual_pairing*.html
  ├── tournament/create.html, created.html, announcements.html, notification_prefs.html, …
  ├── dashboard/index.html, manage_tournament.html, create_profile.html, verification_request.html, notification_settings.html
  ├── notifications/index.html, notifications/connect_provider.html
  ├── player/public_profile.html
  │
  └── admin/base.html  ── extends base.html, adds sidebar chrome
        │
        ├── admin/dashboard.html
        ├── admin/users.html, admin/user_detail.html, admin/tournaments.html
        ├── admin/notifications.html, admin/system.html
        ├── admin/fide_dashboard.html
        └── admin/verifications.html

print/base.html  ── STANDALONE (does NOT extend base.html)
  │
  ├── print/standings.html
  ├── print/round.html
  └── print/crosstable.html
```

### Blocks

| Template | Blocks it defines | Blocks it consumes |
|----------|-------------------|--------------------|
| `base.html` | `title`, `og_title`, `extra_css`, `content`, `extra_js`; global `<head>` (meta, CSRF, Vazirmatn, 6 CSS links, `app.js` at bottom) | — |
| `admin/base.html` | `extra_css` (injects `admin.css`), re-defines `content` (wraps `admin_content` in `.admin-layout` + sidebar) | `extra_css`, `content`, `extra_js` from `base.html`; children use `admin_content` |
| `print/base.html` | `title`, `content` | — (standalone `<head>` with `print.css` + Vazirmatn) |
| All other templates | `title` + `content` (+ optionally `extra_css` / `extra_js`) | `base.html` / `admin/base.html` / `print/base.html` |

**Key decisions**

* **No layout for a single admin page** — every admin page inherits the sidebar via `admin/base.html`. Changing that file restyles the entire system-admin surface.
* **Print is intentionally isolated** — `print/base.html` does not extend `base.html` so print output never inherits header/footer, notification bell, or screen CSS. See §15.
* **`extra_css` / `extra_js` are additive** — `admin/base.html` injects `admin.css` via `extra_css`; feature pages then append their own file. Order: global CSS → feature CSS; `app.js` → feature JS. No asset is loaded twice.

---

## 5. Template → CSS Dependency Map

### Global vs. feature-scoped

| Scope | File | Loaded by | What belongs here / what must NOT go here |
|-------|------|-----------|--------------------------------------------|
| **Global** | `base.css` | `base.html` (every screen) | CSS variables (`--primary`, `--gray-*`, `--radius`, `--shadow`), reset, `body` (RTL, Vazirmatn, `line-height`), `a`, `h1..h3`. **Not** component-specific rules. Blast radius: *every page*. |
| **Global** | `layout.css` | `base.html` | Page chrome: `.container`, `.header`/`.logo`/`.nav`, `.main-content`, `.footer`, home page `.hero`/`.features`/`.search-section`, `.login-page`, `.error-page`, `.recent-*`. **Not** tournament or admin chrome. |
| **Global** | `components.css` | `base.html` | The component library consumed by *dozens* of templates (see §9). Buttons, badges, alerts, forms, link boxes, FIDE status, tiebreak lists, DnD, CSV import, notifications dropdown/page. **Not** admin-specific table/pagination or print rules. Largest shared file — changes ripple. |
| **Global** | `tables.css` | `base.html` | Screen tables: `.table-responsive`, `.data-table`, `.crosstable`, `.cross-cell`, `.cell-*` (win/draw/loss/bye), `.crosstable-legend`, `.rating-up/down`. **Not** admin tables (those live in `admin.css`). |
| **Global** | `tournament.css` | `base.html` (global on purpose) | Tournament chrome used on *many* tournament + player + summary pages: `.tournament-header`, `.tabs/.tab`, `.filter-bar/.filter-btn`, `.round-card`, `.pairings-table`, `.player-info-card`, `.stats-row/.stat-card`, summary/result-bars/podium/awards, arbiter toolbar/dock, admin trigger/sidebar, `.standings-table`, `.result-select*`, plus the **120-line utility-class tail** (`.flex`, `.text-center`, `.fw-bold`, colour `.text-primary`, spacing `.mb-16`, etc.) that replaced `style=""` in `tournament/view.html`. Keep tournament-specific here even though loaded globally — the alternative (a per-page tournament CSS) would fragment the cache. |
| **Global** | `responsive.css` | `base.html` | One media-query sheet: `<=600px`, `601-968px`, table scroll hint. **Only** overrides — never base rules. |
| **Feature** | `admin.css` | `admin/base.html` via `{% block extra_css %}` → every `admin/*.html` + `fide_dashboard`, `verifications` | System-admin chrome: `.admin-layout`, `.admin-sidebar*`, `.admin-nav*`, `.admin-main`, `.page-title`, `.admin-toolbar`, `.search-form`, `.admin-table`, `.table-container`, stats grids, dashboard sections, badges/status badges scoped to admin, `.pagination`, info grids. **Not** public tournament or print. |
| **Feature** | `dashboard.css` | `dashboard/index.html` + `dashboard/manage_tournament.html` via `extra_css` | User hub: `.dash-header` (gradient), `.dash-grid`, `.dash-card`/`.dash-card-title`, `.list-item*`, `.profile-row`, `.modal-overlay/.modal-box`, registration status colours (`.status-pending` etc.). **Not** admin chrome. |
| **Feature** | `print.css` | `print/base.html` (standalone) | Print-only: `@page A4 landscape`, `.print-header/.print-footer`, table borders, `.no-print`, `.btn-print/.btn-back`, `@media print` overrides. **Not** loaded on screen pages. |

### Per-template CSS wiring (verified by grepping `url_for('static', filename='css/…')`)

```
base.html
 ├── base.css, layout.css, components.css, tables.css, tournament.css, responsive.css
 └── (children inherit the 6 above)

admin/base.html  (extends base.html)
 └── + admin.css   → every admin/*.html, admin/fide_dashboard.html, admin/verifications.html

dashboard/index.html, dashboard/manage_tournament.html  (extend base.html)
 └── + dashboard.css

print/base.html  (standalone)
 └── print.css only   → print/standings.html, print/round.html, print/crosstable.html

Other feature pages (all extend base.html, no extra_css file of their own):
  tournament/view.html, crosstable.html, summary.html, player_detail.html,
  tournament/rounds.html, round_view.html, request_bye.html,
  tournament/players.html, player_add/edit.html, player_import.html,
  tournament/pricing.html, prize_settings.html, rulebook_settings.html,
  tournament/announcements.html, notification_prefs.html, backup_*.html, etc.
  → inherit the 6 global CSS files only. Their bespoke rules live inline
    (small <style> blocks in register.html, manual_pairing.html, etc.) or
    inline style="" where still justified — intentionally not extracted into
    per-page CSS files per §19.
```

Only four templates load a feature CSS via `extra_css`; the rest rely on the globals. That is intentional — see §19.

---

## 6. Template → JavaScript Dependency Map

| Scope | JS file | Loaded by (verified `url_for('static', filename='js/…')`) | Consumers / route |
|-------|---------|-------------------------------------------------------------|-------------------|
| **Global** | `app.js` (134 lines) | `base.html` — every page | `injectCSRFToken()`, notification dropdown (`/api/notifications`), generic `[data-target][data-action="toggle-class"]` handler (currently `admin/base.html` sidebar toggle). Exposes `window.AppUtils`. The only JS that runs unconditionally. |
| **Global (trivial)** | `main.js` (6 lines) | *never loaded* (exists but `base.html` loads `app.js`) | `console.log` placeholder — safe to delete but kept to avoid 404 on stale caches. Post-refactor it is dead code; do not add new code here. |
| **Feature** | `modal.js` (112 lines) | `dashboard/index.html` via `extra_js` | `Modal.open/close/closeAll`, focus trap, ESC + overlay close, auto-wires `[data-modal-trigger]` / `[data-modal-close]`. |
| **Feature** | `notifications.js` (105 lines) | `notifications/index.html` via `extra_js` | Inbox `markAsRead / markAllAsRead`, bell badge delta (`#notifCount`), click-outside guard. Fetches `POST /api/notifications/<id>/read` + `POST /api/notifications/read-all`. |
| **Feature** | `tournament-view.js` (99 lines) | `tournament/view.html` via `extra_js` | Tab switching (`[data-tab]` → `#tab-*`) + standings highlight/filter (`[data-filter]` vs `data-age`, cumulative `[data-cumulative-age-category]` flag, `ageOrder` map). The richest page JS. |
| **Feature** | `tiebreak-dnd.js` (68 lines) | `tournament/settings.html` via `extra_js` | HTML5 drag-and-drop reordering of `#tiebreak-list > .tiebreak-item`; DOM order *is* submission order (`getDragAfterElement` midpoint heuristic). |
| **Feature** | `manual-pairing.js` (35 lines) | `tournament/manual_pairing.html` via `extra_js` | Live validation that `#board1 ≠ #board2` for swaps; toggles `#swap-warning` + `#swap-submit-btn[disabled]`. |
| **Feature** | `registration.js` (105 lines) | `tournament/register.html` via `extra_js` | Debounced (300 ms) live price preview. Reads `form[data-api-url]` + `form[data-base-price]`, POSTs JSON `{first_name,last_name,fide_id,birth_date,gender,promo_code}` to `POST /<public_id>/api/calculate_price`, patches `#base-price`, `#final-price`, `#discount-list`. Uses `escapeHtml`. |
| **Feature** | `backup_import.js` (146 lines) | `tournament/import_from_backup.html` via `extra_js` | Coronate JSON flow: file validation (`.json`), `fetch POST /create/from-backup/coronate` with `FormData` + `X-CSRFToken`, renders per-tournament `<form>` targeting `/create/execute/coronate`, `showAlert/escapeHtml`. The only JS that was external *before* the refactor — kept as-is. |

Templates with **no extra JS** rely on `app.js` alone (CSRF + notification bell). Specifically: `tournament/crosstable.html`, `summary.html`, `player_detail.html`, `tournament/rounds.html`, `round_view.html`, `players.html`, `admin/*.html`, `dashboard/manage_tournament.html`, `auth/*.html`, `player/public_profile.html`, `print/*.html`, etc. — none load a page script.

---

## 7. JavaScript Architecture

### Conventions every file follows

* IIFE or module pattern with a single `DOMContentLoaded` entry point; idempotent if the expected DOM nodes are absent (`if (!el) return`).
* Vanilla `fetch` with `X-CSRFToken` from `meta[name=csrf-token]` (or `AppUtils.getCSRFToken()`).
* `data-*` attributes are the only server → JS channel (see §10). No raw `{{ }}` inside `.js` files — except one 3-line shim in `tournament/view.html` that sets `document.body.dataset.cumulativeAgeCategory` from Jinja before `tournament-view.js` runs.
* Defensive null checks everywhere; no unguarded `querySelector(...).addEventListener`.
* `escapeHtml` via a detached `<div>` — used in `app.js`, `backup_import.js`, `registration.js`.
* No globals except `window.AppUtils`, `window.Modal`, `window.Notifications`, `window.TournamentView`, `window.RegistrationCalculator`, etc. — each file namespaces itself.

### File-by-file

| File | What it owns | What it must NOT own |
|------|--------------|----------------------|
| **`app.js`** | CSRF injection into every `form[method=POST]` at `DOMContentLoaded`; dropdown fetch/render for `#notifBell → #notifDropdown` (lazy-loads `/api/notifications`, caches `isLoaded`, click-outside dismiss); `[data-target][data-action="toggle-class"]` dispatcher (admin sidebar toggle); `escapeHtml` + `getCSRFToken` helpers. Runs on *every* page — keep it small and failure-isolated (dropdown `catch` restores `isLoaded=false`). | Page-specific logic. Do not add tab/price/modal code here. |
| **`modal.js`** | Generic modal lifecycle for any `.modal-overlay`. `open(id)` adds `.active`, locks `body.overflow`, focuses first focusable child, wires `trapFocus` (Tab wrap). `close(id)` / `closeAll()` restore overflow. Auto-wired: `[data-modal-trigger] → Modal.open` and `[data-modal-close] → Modal.close`. Overlay-click and `Escape` close. Used by `dashboard/index.html` (`#editModal`, `#claimModal`). | Tournament or registration logic. Do not add domain-specific submit handlers. |
| **`notifications.js`** | Inbox page (`#notificationsList`, `.notif-row.unread[data-id]`, `#markAllReadBtn`). `fetch POST /api/notifications/<id>/read` per-row + `POST /api/notifications/read-all` for bulk; removes `.unread`, `.unread-dot`, updates `#notifCount` badge with delta math, removes `#markAllReadBtn` when empty. Guard: `e.target.closest('a,button')` prevents row click when a nested action is clicked. | Dropdown behaviour (that lives in `app.js`). Keep the two notification surfaces separate unless you intend to unify them. |
| **`tournament-view.js`** | Two independent features on the unified tournament page: (1) tab switching — `[.tab[data-tab]]` ⇄ `[.tab-content#tab-*]` (adds/removes `.active`), (2) standings highlight — `.filter-btn[data-filter]` vs `.player-row[data-age]` + `#standings-body.table-filtered / .player-row.row-highlighted`, reads `document.body.dataset.cumulativeAgeCategory` and `ageOrder` map to expand `U08 ⊆ U10 ⊆ … ⊆ U20` and `S65 ⊆ S50` in cumulative mode. | Price or pairing logic. |
| **`tiebreak-dnd.js`** | HTML5 DnD for `#tiebreak-list`. Marks each `.tiebreak-item[draggable=true]`, tracks `draggedItem`, inserts before midpoint `getDragAfterElement`. CSS class `tb-dragging` drives ghost styling. Submission order is DOM order — no hidden input sync needed (checkboxes ride with their `.tiebreak-item`). | Validation — server re-validates tiebreak keys. |
| **`manual-pairing.js`** | Live guard for swap form on `manual_pairing.html`: watches `#board1` / `#board2`, shows `#swap-warning` and disables `#swap-submit-btn` when `board1 === board2`. Pure validation — no fetch. | Pairing mutation (form POST to `round.manual_pairing`). |
| **`registration.js`** | Debounced preview. Reads `form#reg-form[data-api-url]` + `data-base-price`, watches six inputs (`first_name,last_name,fide_id,birth_date,gender,promo_code`) on `change`+`input`, 300 ms debounce, `fetch POST <data-api-url>` JSON, patches `#base-price`, `#final-price`, rebuilds `#discount-list` with `escapeHtml`. Gracefully handles `data.error` from the pricing service. | Submission — `form[method=POST]` goes to `registration.register` directly. Do not duplicate server pricing; this is preview-only. |
| **`backup_import.js`** | Pre-refactor Coronate import wizard (kept). `previewTournaments()` validates file present + `.json` extension, shows spinner, `fetch POST /create/from-backup/coronate` with `FormData(json_file)` + `X-CSRFToken`, then `renderTournamentList(tournaments, csrfToken)` injects per-tournament `<form method=POST action=/create/execute/coronate>` with hidden `csrf_token` + `target_tournament_id`. `showAlert` + `escapeHtml` for XSS-safe rendering. | Tournament creation — the `execute` POST is a full page submission, not AJAX. |

**Initialization pattern**

```js
// every file
document.addEventListener('DOMContentLoaded', initX);
window.X = { init: initX, ...helpers }; // namespace, never bare globals
```

**Fetch / CSRF pattern**

```js
fetch(url, {
  method: 'POST',
  headers: { 'X-CSRFToken': AppUtils.getCSRFToken(), 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});
```

**Server config pattern** — see §10.

---

## 8. CSS Architecture

### The decision not to over-split

Nine stylesheets is the post-refactor steady state. Four templates own a feature CSS (`admin.css`, `dashboard.css`, `print.css`, plus the inline `<style>` in `register.html`/`manual_pairing.html` already being the right size). A dozen tournament templates happily share `tournament.css`. Adding per-page CSS for each of the ~30 templates would have traded one duplication problem for a fragmentation problem (cache churn, import-order bugs, repeated variable re-declarations). New code should follow the same heuristic: **a feature CSS only when a coherent *section* of the site shares a distinct chrome** (admin, dashboard, print). Otherwise extend the appropriate global.

### Per-file ownership

| File | Lines (approx.) | What belongs here | What must NOT be placed here |
|------|------------------|-------------------|------------------------------|
| `base.css` | ~60 | Design tokens (`:root { --primary, --success, --warning, --error, --gray-50…900, --radius, --shadow }`), reset (`*{margin:0;padding:0;box-sizing:border-box}`), `body { Vazirmatn, rtl, line-height, font-size }`, `a`, `h1..h3`. | Anything component-specific. Changing this recolours the entire product. |
| `layout.css` | ~290 | Layout chrome shared by *every* `base.html` page: `.container`, `.header/.logo/.nav`, `.main-content`, `.footer`, home `.hero/.features/.search-section/.recent-*`, login/error pages. | Tournament tabs, admin sidebar, dashboard cards. |
| `components.css` | ~610 | The reusable component library — the highest-blast-radius file after `base.css`: `.btn*` (6 variants), `.badge*`, `.alert*`, `.form-container/.form-section/.form-group/.form-row/.radio-group/.checkbox-label`, link boxes, FIDE status, `.tiebreak-simple-list`, admin actions, `.bye-info`, `.file-input`/import, notification dropdown/page (`.notification-bell-container … .notification-item`). | Admin table chrome (lives in `admin.css`), print chrome (`print.css`), tournament podium/awards (`tournament.css`). |
| `tables.css` | ~185 | Screen tables: `.table-responsive`, `.data-table`, `.crosstable/.cross-cell/.cell-win/.cell-draw/.cell-loss/.cell-bye/.cell-pending`, `.crosstable-legend`, `.rating-up/down`. | Admin tables (those are `admin.css` `.admin-table`) and print tables (`print.css`). |
| `tournament.css` | ~835 (incl. utilities) | Tournament surface: `.tournament-header`, `.tabs/.tab/.tab-content`, `.filter-bar/.filter-btn`, `.rounds-list/.round-card`, `.pairings-table/.player-cell/.result-select`, player info card, stats, result bars, podium, awards, arbiter toolbar/dock, floating admin trigger, `.admin-sidebar` (tournament drawer variant), `.standings-table`, filter/highlight (`.row-highlighted/.table-filtered`). **Tail (last ~120 lines): utility classes** (`.flex/.justify-between/.gap-8/.mb-16/.p-16/.text-center/.fw-bold/.text-primary/.bg-white/.rounded/.shadow/.opacity-50` etc.) — a deliberate concession to eliminate 60+ `style=""` attributes from `tournament/view.html` without adding a utility framework. | Generic buttons/badges (those are `components.css`), admin layout (those are `admin.css`). Do not grow this file with dashboard or print rules. |
| `responsive.css` | ~205 | Overrides only: `max-width:600px` (mobile: body `13px`, header centred, hero, grid→1-2 col, forms, tournament header, tabs, tables, filter, rounds, admin actions, result-select), `601-968px` (tablet), `.table-responsive::after '← اسکرول کنید'` hint. Never base rules — always an override layered after the globals. | Any new component should land in its owner file; this file only *adapts* it. |
| `admin.css` | ~470 | System-admin section (loaded only under `admin/base.html`): `.admin-layout/.admin-sidebar*/.admin-nav*`, `.page-title`, `.admin-toolbar/.search-form/.search-input/.filter-select`, `.stats-grid/.stat-card`, `.dashboard-sections/.dashboard-section`, `.admin-table/.table-container`, scoped `.badge/status-badge` overrides (admin palette), `.pagination`, `.info-grid`, admin-scoped `.btn` overrides (`.btn-info/.btn-warning/.btn-danger/.btn-sm`). | Tournament or public pages — no `admin.css` outside `admin/*`. |
| `dashboard.css` | ~290 | Authenticated user hub (`dashboard/index.html`, `manage_tournament.html`): `.dash-header` (gradient), `.dash-grid`, `.dash-card/.dash-card-title`, `.list-item*`, `.profile-row`, `.modal-overlay/.modal-box`, `.status-pending/.status-payment_pending/…` (registration states), `.status-active`, file-button polish. Loaded only where needed via `extra_css`. | Admin tables (use `admin.css`) or tournament chrome (use `tournament.css`). |
| `print.css` | ~120 | Print + screen-preview for `print/base.html`: `@page { size: A4 landscape; margin 8mm }`, `body { padding 5mm / 10mm }`, `.print-header/.print-footer`, `table { border:1px solid #333 }`, `.cell-win/draw/loss`, `.no-print`, `.btn-print/.btn-back`, `@media print { body 5mm; .no-print display:none }`. Hard-coded `#000/#333/#e5e7eb` — CSS variables are avoided here because print media in Chromium/WeasyPrint renders them inconsistently. | Screen UI. Never import this file from `base.html`. |

**Choosing the right file for new code**

```
new global token / reset / body?            → base.css
new chrome that lives on every page?        → layout.css
new button/badge/alert/form/card/notice?    → components.css   (reusable)
new table on a normal screen page?          → tables.css
new responsive tweak to an existing thing?  → responsive.css   (override)
new rule that only matters on tournament pages? → tournament.css
new rule that only matters under /admin?    → admin.css
new rule that only matters on /dashboard?   → dashboard.css
print?                                      → print.css
```

---

## 9. Shared UI Components

Canonically defined — reuse, do not duplicate.

| Component | Canonical file | Classes / markup | Notes |
|-----------|---------------|------------------|-------|
| **Buttons** | `components.css` + `admin.css` (admin overrides) | `.btn`, `.btn-primary/.btn-secondary/.btn-large/.btn-small/.btn-danger-outline`; admin adds `.btn-info/.btn-warning/.btn-danger/.btn-sm` | Admin buttons (`.btn-info` is `#17a2b8`) override the global `.btn-primary` palette intentionally. Elsewhere use the global set. |
| **Badges** | `components.css` (`admin.css` scopes its own) | `.badge`, `.badge-success/.badge-warning/.badge-error` (screen), `.badge-admin/.badge-player/.badge-organizer/.badge-arbiter` (admin-scoped `.badge` override in `admin.css`) | Admin `.badge` resets `background: var(--gray-200); color: var(--gray-700)` — do not reuse that palette outside admin. |
| **Status badges** | `admin.css` + `dashboard.css` | `.status-badge` + modifiers `.status-setup/.status-pending/.status-ongoing/.status-active/.status-finished/.status-success/.status-failed/.status-inactive/.status-rejected`; `dashboard.css` also defines `.status-pending/.status-payment_pending/…` for registrations | Tournament status and registration status use the same *concept* but different CSS. Check which file you're in. |
| **Alerts / Flash** | `components.css` + `base.html` | `.alert`, `.alert-error/.alert-success/.alert-close`; rendered from `get_flashed_messages(with_categories=true)` in `base.html` | Auto-dismiss button uses `onclick="this.parentElement.remove()"` — kept inline intentionally (trivial, no external dependency). |
| **Forms** | `components.css` | `.form-container`, `.form-section`, `.section-title`, `.form-group label/input/select/textarea`, `.form-row` (2-col grid), `.radio-group/.radio-label`, `.checkbox-label`, `.form-actions`, `.form-note` | Every create/edit page reuses this. `form-row` collapses to 1 col in `responsive.css`. |
| **Cards** | `components.css` (`link-box`), `tournament.css` (podium/award), `dashboard.css` (dash-card), `layout.css` (recent-card/feature-card) | `.link-box/.link-display`, `.podium-card/.award-card`, `.dash-card`, `.recent-card`, `.feature-card` | No single `.card` — each section scopes its own card. Reuse the nearest one; do not add a generic `.card` that collides. |
| **Tables** | `tables.css` (`data-table`, `crosstable`) + `admin.css` (`admin-table`) | `.table-responsive > .data-table`; `.crosstable .cross-cell`; print tables in `print.css` | Use `tables.css` for screen data, `admin.css` `.admin-table` under `/admin`. Print tables must not depend on either. |
| **Notifications** | `components.css` | `.notification-bell-container`, `.notif-badge`, `.notification-dropdown`, `.notif-dropdown-header/body/item(.unread)`, `.notification-item(.unread)`, `.notif-row/.unread-dot` | Dropdown (in `base.html` + `app.js`) and inbox (`notifications/index.html` + `notifications.js`) share these classes. Full-page inbox adds `.notif-row`. |
| **Modals** | `dashboard.css` (style) + `modal.js` (behaviour) | `.modal-overlay(.active)`, `.modal-box`; `[data-modal-trigger="id"]`, `[data-modal-close="id"]` | Focus trap + ESC + overlay click baked into `modal.js`. Any page can reuse by adding the two data attributes — no per-modal JS. |
| **Page header** | `components.css` | `.page-header > h1` | Thin wrapper; used on most CRUD pages. Do not add a per-page header CSS duplicate. |
| **Admin chrome** | `admin.css` | `.admin-layout/.admin-container`, `.admin-sidebar*`, `.admin-nav-item(.active)`, `.admin-main`, `.admin-toolbar`, `.search-form`, `.pagination` | Only rendered by `admin/base.html`. Every admin page inherits it — no per-page admin CSS. |
| **Utilities** | `tournament.css` tail | `.flex/.flex-wrap/.items-center/.justify-between/.gap-8/.mb-16/.mt-15/.p-16/.text-center/.fw-bold/.text-primary/.bg-white/.rounded/.shadow/.opacity-50/…` | Deliberately scoped to `tournament.css` (not a separate `utilities.css`) to avoid a third global that every page would load. Use these instead of new `style=""` in `tournament/view.html` descendants. |

---

## 10. Jinja → JavaScript Data Flow

**Rule.** External `.js` files must not contain raw `{{ }}`. The only sanctioned channels are:

### `data-*` attributes (preferred 90% of the time)

```html
<!-- registration.html — lets registration.js stay pure JS -->
<form id="reg-form"
      data-api-url="{{ url_for('registration.calculate_price_api', public_id=tournament.public_id) }}"
      data-base-price="{{ tournament.base_price or 0 }}">
  <input id="promo_code" …>
  <span id="final-price">{{ tournament.base_price }}</span>
</form>
```
```js
// registration.js
const apiUrl = document.getElementById('reg-form').dataset.apiUrl;
fetch(apiUrl, { method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken': getCSRFToken()}, body: JSON.stringify(data) })
```

```html
<!-- tournament/view.html — cumulative flag for the highlight filter -->
<tbody id="standings-body"
       data-cumulative-age-category="{{ 'true' if tournament.cumulative_age_category else 'false' }}">
```
```js
// tournament-view.js
const cumulativeMode = document.getElementById('standings-body').dataset.cumulativeAgeCategory === 'true';
```

```html
<!-- notifications/index.html — row identity for mark-read -->
<div class="notif-row unread" data-id="{{ n.id }}">
```

```html
<!-- admin/base.html + app.js — generic toggle without per-page JS -->
<button data-target=".admin-sidebar" data-action="toggle-class" data-class="open">☰</button>
```
```js
// app.js — initToggleHandlers
document.querySelectorAll('[data-target][data-action="toggle-class"]').forEach(el => … classList.toggle(className));
```

```html
<!-- dashboard/index.html — modal wiring without onclick -->
<button data-modal-trigger="editModal">ویرایش</button>
<div id="editModal" class="modal-overlay"> … <button data-modal-close="editModal">انصراف</button>
```

### Tiny config shim (the one exception)

`tournament/view.html` needs the *cumulative* flag before `tournament-view.js` runs. A single 3-line shim in `{% block extra_js %}` sets `document.body.dataset.cumulativeAgeCategory = "{{ 'true' … }}"` right before `<script src="tournament-view.js">`. No other Jinja leaks into JS. This is smaller and safer than inlining the whole filter engine.

### What is never exposed

* `SECRET_KEY`, `*_WEBHOOK_SECRET`, `user.password_hash` — no route ever passes these to a template.
* `DB_NAME` / `TELEGRAM_BOT_TOKEN` — config-only, never in context.
* Per-template CSRF: via `<meta name="csrf-token" content="{{ csrf_token() }}">` (in `base.html`) + `X-CSRFToken` header or auto-injected `<input name="csrf_token">` — no `{{ csrf_token() }}` in page body (see §3 Strict Rules).

### CSRF

* One meta tag in `base.html:13`.
* `app.js:injectCSRFToken()` appends a hidden input to every `form[method=POST]` missing one at `DOMContentLoaded`.
* `fetch` calls use `X-CSRFToken: AppUtils.getCSRFToken()`.
* Keep `app.js` loaded on every page — removing it silently breaks every POST form *and* the notification dropdown.

---

## 11. Frontend Dependency Boundaries

### Allowed

```
Route (interfaces/web/*.py)
  ├─► Application Service (application/*)      — the only business entry point
  ├─► Infrastructure Repository (read-only)    — ideally via the service; a few routes still query Model directly (tech-debt to move)
  ├─► domain.* (constants only: ALL_TIEBREAKS_DISPLAY, CATEGORY_TITLES_FA, SECTION_VOCABULARY)
  └─► render_template(template, **context)

Template (templates/**/*.html)
  ├─► CSS via url_for('static', filename='css/…') / {% block extra_css %}
  ├─► JS  via url_for('static', filename='js/…')  / {% block extra_js %}
  └─► url_for('blueprint.endpoint') for links/forms (never hardcoded URLs)

JS (static/js/*.js)
  ├─► DOM (querySelector, dataset, classList)
  ├─► fetch → Flask JSON / full-page POST endpoints
  └─► meta[name=csrf-token] + data-* attrs   — no Jinja
```

### Forbidden / Avoid

```
Template ──X──► db.session / Repository / Model query    (must go through the route → service)
Template ──X──► domain.pairing / tiebreak / rating logic (same)
JS      ──X──► Flask internals (request, session, g)    (JS only knows HTTP + DOM)
JS      ──X──► raw {{ csrf_token() }} outside the meta tag
Route   ──X──► infrastructure.db_models directly         (prefer repositories; existing direct queries are grandfathered but new code must use repositories/services)
Route   ──X──► static file-write outside instance_path  (receipts, profile photos, rulebook PDFs, FIDE downloads all live under instance_path — see app/__init__.py:33-54)
```

**Presentation vs. business logic.** Anything that decides *what to show* (status badge colours that are purely cosmetic, empty-state copy, client-side dim/highlight of rows) belongs in template/CSS/JS. Anything that decides *what is allowed / who wins / what the price is / who may write results* belongs in `application/` → `domain/`. The standings highlight filter is a good example of the boundary: `tournament-view.js` dims rows purely visually; the actual `player_standings` ordering is computed server-side by `StandingsService` and is authoritative.

---

## 12. Cross-Feature Dependencies — Blast Radius

| File | Scope | Blast radius if changed | How to check |
|------|-------|-------------------------|--------------|
| `templates/base.html` | Every `base.html` child (~45 templates) | **Maximum.** Header/nav, notification bell, flash alerts, CSRF meta, global CSS links, `app.js` live here. A broken `base.html` blanks the whole site. | Render `/`, `/dashboard`, `/<public_id>`, `/admin`, `/notifications`, a POST form (CSRF). |
| `static/css/base.css` | Every page | **Global tokens.** Changing a variable repaints the product. | Grep for `var(--changed)` — expect dozens of hits. Visually spot-check 3–4 different page types. |
| `static/css/components.css` | ~30 templates | **Very high.** Buttons/badges/alerts/forms/notifications are used almost everywhere. A `.btn` regression shows up on 20+ screens. | Open 3–4 templates that use the changed component (search for class name). |
| `static/css/tournament.css` | ~15 tournament/player/summary templates + is global import | **High** for tournament surface, none for admin/dashboard/print. | Open `tournament/view.html`, `players.html`, `summary.html`, `crosstable.html` on 3 viewports. |
| `static/css/responsive.css` | Every page (overrides) | **Global layout.** A bad breakpoint breaks mobile site-wide. | Resize to 360 / 768 / 1200 and check header, tables, cards, modals. |
| `static/js/app.js` | Every page | **Global behaviour.** Breaking CSRF injection silently breaks every POST; breaking the dropdown breaks the bell on every authenticated page. | Submit any POST form, open the bell dropdown, toggle the admin sidebar. |
| `templates/admin/base.html` | Every `admin/*.html` + `admin/fide_*` + `admin/verifications` | **Admin-section.** A sidebar/nav regression locks every system-admin page. | Open `/admin`, `/admin/users`, `/admin/fide`, `/admin/verifications` (desktop + mobile drawer). |
| `static/css/admin.css` | Admin section only | **Admin-section.** Restyling `.admin-table` or `.admin-sidebar` affects 8 pages. | Same 4 admin URLs above. |
| `templates/print/base.html` + `static/css/print.css` | `print/*.html` + `export/trf` only | **Isolated by design.** Changes never affect screen UI, but a bad `@page` or table border breaks every printed sheet. Use Print Preview, not screenshots. | Print Preview `print/standings`, `print/round`, `print/crosstable`. |
| `static/css/dashboard.css` | `dashboard/index.html`, `manage_tournament.html` only | **Dashboard-only.** Safe to edit without touching tournament or admin. | `/dashboard`, `/dashboard/tournament/<id>/manage`. |
| `.table-responsive` / `.data-table` (tables.css) vs `.admin-table` (admin.css) | Screen data vs admin data | **Two isolated table systems.** Do not “unify” them without touching both consumers — they have intentionally divergent spacing/palette/hover. | Any screen list + any admin list. |
| `{% block extra_css %}` / `{% block extra_js %}` ordering | Additive inheritance chain | **Ordering-sensitive.** A feature file loaded before the globals cannot override them. `base.html` → `admin/base.html` → page is correct; reversing breaks specificity. | View Source → confirm link order in `<head>` and script order before `</body>`. |
| `modal.js` generic `data-*` contract | Any future modal | **Wide if mis-used.** Changing `[data-modal-trigger]` semantics would break every modal opened that way. Keep the contract stable (open = add `.active`, focus first focusable, body lock, trap Tab, ESC/overlay close). | Any modal: dashboard edit/claim + any new modal. |

---

## 13. Data Flow Examples

### A. Someone opens a tournament page

```
GET /<public_id> (e.g. /58341297)
  │
  ▼
tournament.view()               interfaces/web/tournament/__init__.py:121
  ├─ validate public_id (8 digits)
  ├─ TournamentRepository.get_by_public_id()
  ├─ require_result_editor() / require_tournament_manager() → can_edit_results / can_manage
  ├─ StandingsService.get_standings(tournament)        application/tournament/standings_service.py
  │    └─ domain.tiebreak.calculators + domain.rating.calculator + infrastructure.repositories
  ├─ PrizeSummaryService.get_public_prize_summary()
  └─ render_template("tournament/view.html", tournament=…, is_admin=…, can_manage=…, **standings)
         │
         ▼
templates/tournament/view.html  (extends base.html)
  ├─ tournament-header (city, time control, round counter)
  ├─ tabs (.tabs → #tab-standings, #tab-round-N, #tab-crosstable, #tab-summary, #tab-rulebook)
  ├─ standings table (player_standings, tiebreak_rules, rating_changes) — data-age / row-highlighted classes
  ├─ round tables (tournament.rounds → pairings, result_display)
  └─ {% block extra_js %} → tournament-view.js (wire tabs + filter) + shim for cumulative flag
         │
         ▼
Browser: tournament.css (tabs/filter/podium) + tables.css (data-table) + tournament-view.js (Tabs + highlight)
         + base.html globals (header, bell, CSRF) — no extra round-trip.
```

### B. Live price preview while registering

```
GET /<public_id>/register  ──► registration.register() → render_template("tournament/register.html")
                                      │
                                      ▼
                          templates/tournament/register.html
                            <form id="reg-form"
                                  data-api-url="{{ url_for('registration.calculate_price_api', public_id=…) }}"
                                  data-base-price="{{ tournament.base_price }}">
                              <input id="promo_code"> … <span id="final-price">
                            </form>
                            + registration.js via extra_js

User types promo code (or changes gender / fide_id / birth_date)
  │
  ▼
registration.js:initRegistrationCalculator()
  ├─ listeners on 6 inputs (change + input), 300 ms debounce
  ├─ GET csrf from meta[name=csrf-token]
  ├─ POST <data-api-url>  Content-Type: application/json  X-CSRFToken: …
  │     { first_name, last_name, fide_id, birth_date, gender, promo_code }
  │
  ▼
POST /<public_id>/api/calculate_price   registration.calculate_price_api()
  ├─ PricingCalculator + EligibilityChecker (application/registration/pricing_calculator.py etc.)
  └─ JSON { base_price, final_price, discounts:[{reason, amount}] }

  │
  ▼
registration.js  patches #base-price, #final-price, rebuilds #discount-list
(never a full page reload; server pricing is still re-validated on final POST to /<public_id>/register)
```

### C. Creating and consuming a notification

```
Business event (e.g. dashboard.add_staff → invitation, round.round_new → next round)

  ▼  Business service calls
NotificationService.create_notification(user_id, type, title, message, link_url)   application/notification_service.py
  │
  ├─ NotificationDispatcher  →  NotificationPreference / tournament notification gate
  └─ fan-out to enabled Providers
       ├─ WebProvider    → INSERT NotificationModel (DB)
       ├─ TelegramProvider → POST Telegram Bot API (if user.telegram_chat_id + webhook)
       └─ BaleProvider     → POST Bale Bot API (if user.bale_chat_id)
     (a provider failure never crashes the dispatcher)

Two consumption surfaces:

1) Bell dropdown (every authenticated page)
   base.html  → #notifBell / #notifDropdown / #notifDropdownBody  +  app.js initNotificationDropdown()
                  └─ lazy fetch GET /api/notifications  (notification.api_list)
                     → { notifications:[{title,message,created_at,is_read,link_url}], unread_count }
                     → rendered into .notif-dropdown-item(.unread) in place

2) Inbox page
   GET /notifications  → notification.index() → render_template("notifications/index.html", notifications, unread_count)
                          └─ notifications.js  (markAsRead / markAllAsRead)
                               ├─ click .notif-row.unread[data-id] → POST /api/notifications/<id>/read
                               └─ click #markAllReadBtn               → POST /api/notifications/read-all
                                     → both are JSON {success}; updates #notifCount badge with delta math
```

---

## 14. Responsive Architecture

* Owner: `static/css/responsive.css` — **the only file** that contains `@media`. Do not add ad-hoc `@media` in `components.css` / `tournament.css` / `admin.css`; keep the breakpoints co-located and layered after the globals so specificity is predictable.

* Breakpoints (already shipped):

| Breakpoint | Rules |
|------------|-------|
| `max-width: 600px` (mobile) | `body 13px`; `.container 8px` gutters; header centred; `.hero 24px` + `1.2em`; `.features` 2-col; `.search-form` stacked; `.form-container 12px`; `.form-row 1 col`; `.radio-group` column; `.tournament-header 12px` + `1em`; `.tournament-meta` column; `.tabs 3px` gap / `.tab 6px 10px`; `.tab-content 10px`; `.data-table 0.72em` + `5px 4px` cells; `.filter-bar 6px 8px` / `.filter-btn 3px 8px`; `.round-card 10px`; `.admin-actions` stacked; `.result-select 100%`; `.form-actions` stacked. |
| `601-968px` (tablet) | `hero 1.4em`; `.features` 2-col; `.form-row` stays 2-col; `.data-table 0.78em`. |
| `<=968px` extra | `.table-responsive::after { '← اسکرول کنید' }` hint (hidden above). |

* Component-specific responsive notes agents must know:

| Component | Mobile behaviour | File that owns it |
|-----------|------------------|-------------------|
| Admin sidebar | `position: fixed; right:-250px` → `.open { right:0 }` drawer triggered by `.admin-sidebar-toggle` (visible only `<=768px`) | `admin.css` + `[data-target]` dispatcher in `app.js` |
| Tables (all) | Wrapped in `.table-responsive { overflow-x:auto; -webkit-overflow-scrolling:touch }` + `min-width:600px` on `.data-table` to force horizontal scroll instead of collapsing columns | `tables.css` + `responsive.css` hint |
| Tournament tabs | `overflow-x:auto` + `white-space:nowrap` on `.tabs`; tabs never wrap | `tournament.css` |
| Hero / feature cards / search | Stack to column; `letter-spacing` and padding tighten | `layout.css` + `responsive.css` |
| Modals | `@media` not in `responsive.css` — `dashboard.css` already makes `.modal-box { width:90%; max-width:450px }` and `app.js` locks body scroll | `dashboard.css` + `modal.js` |

---

## 15. Print Architecture

```
Normal screen UI            Print UI
base.html (+ 6 globals)     print/base.html (standalone, only print.css)
    │                           │
    ├── *.html                  ├── print/standings.html
    ├── tournament.css          ├── print/round.html
    └── app.js                  └── print/crosstable.html (+ /export/trf text)
```

* `print/base.html` intentionally **does not** `{% extends "base.html" %}` — it ships its own `<head>` (`Vazirmatn` + `print.css` only) so header/footer/bell/responsive CSS never bleed into print.
* `static/css/print.css` uses **hard-coded** `#000/#333/#e5e7eb` — CSS variables are avoided because Chromium/WeasyPrint print rendering does not resolve `var(--*)` reliably.
* Print tables have `border:1px solid #333` + `background:#e5e7eb` header, `.cell-win/draw/loss` tinted, `border-collapse:collapse`; `.no-print` (button bar) + `@media print { body 5mm; .no-print display:none; @page A4 landscape }`.
* Screen preview re-declares the same rules under `@media screen` with `10mm` padding and `.btn-print/.btn-back` so developers can eyeball print without hitting Preview.
* A change under `templates/print/` or `static/css/print.css` **cannot** affect screen UI and vice-versa — verify via Print Preview, not screenshots.

---

## 16. UI/UX Architectural Principles

These are project decisions, not generic advice. Violating them will be flagged in code review.

1. **Unified view, not split admin pages.** The tournament public page (`tournament/view.html`) *is* the arbiter console. Access is decided server-side (`is_admin / can_manage / can_edit_results` from `admin_auth.py`) and the *same* template conditionally renders management affordances (`{% if can_edit_results %}` toolbar + console link). Do not add `admin_view.html` or `admin_standings.html`.

2. **RTL + Persian is the default.** Every layout decision (flex order, `left` vs `right`, `float`, `margin-right` for tab admin slot, notification dropdown `left:0` in RTL) must be verified in `dir="rtl"`. Persian copy lives in templates/flash messages; code/comments/commit messages stay in English.

3. **In-place over navigation.** Where the UX philosophy applies: `round_view.html` exposes a `<select class="result-select">` *inside* the round tab so arbiters never leave the page to submit results; standings highlight reflows ranks client-side (`tournament-view.js`) instead of reloading. Keep this pattern for future arbiter tools.

4. **Reuse the library, do not re-declare it.** Buttons, badges, alerts, forms, table and notification chrome already exist in `components.css` / `tables.css` / `admin.css` / `dashboard.css` (see §9). Adding per-page CSS for a new button look is a review failure — use the modifiers (`.btn-primary`, `.filter-btn-custom`, etc.) or extend the library with a single variable-driven variant.

5. **Links/forms are always `url_for`, never hardcoded.** `url_for('tournament.view', public_id=tournament.public_id)` and `url_for('static', filename='…')` are the only acceptable forms. This preserves the `public_id`-in-URL contract (`data/ARCHITECTURE_REFACTOR.md`).

6. **CSRF via meta, not body.** Templates never call `{{ csrf_token() }}` directly; `base.html` provides `<meta name="csrf-token">` and `app.js:injectCSRFToken()` appends `<input name="csrf_token">` to every `form[method=POST]` at `DOMContentLoaded`. `fetch` uses `X-CSRFToken`.

7. **Vanilla JS, not a framework.** No jQuery, Bootstrap, React, Vue, TypeScript, npm, bundler. If you need a reusable behaviour, add a small vanilla module under `static/js/` and wire it via `data-*` + `extra_js` (see §7).

8. **Do not chase line-count.** The refactor deliberately left small inline `<style>` blocks in `tournament/register.html` (`.reg-container/.reg-card/.price-box`) and `tournament/manual_pairing.html` (`.board-row/.board-number/.players-display`) because extracting them into per-page CSS files would have added two one-off files with no reuse. The doc's §8 heuristic (feature CSS only for a *section*) is the canonical rule — not “every inline style must die”.

---

## 17. "If You Need to Change X, Start Here"

| Task | Start by reading — in order |
|------|-----------------------------|
| **Change global colours / fonts** | `static/css/base.css` → `base.html` (verify via Vazirmatn link, `:root` tokens) |
| **Change global layout (header/footer/container)** | `static/css/layout.css` → `templates/base.html` |
| **Change buttons / badges / alerts / forms** | `static/css/components.css` (library) → any 2–3 templates that use the class (grep the class name) |
| **Change tournament chrome (header, tabs, standings, rounds, podium, awards)** | `static/css/tournament.css` + `templates/tournament/view.html` → `round_view.html`, `crosstable.html`, `summary.html`, `players.html` |
| **Change tournament *logic* shown in the UI (tiebreak order, pricing)** | `interfaces/web/tournament/__init__.py` + `tournament/settings.html` (tiebreak) or `tournament/pricing.html` + `application.tournament.*` / `application.registration.*` |
| **Change registration UI / live price preview** | `templates/tournament/register.html` + `static/js/registration.js` + `interfaces/web/registration_routes.py` (`calculate_price` handler) |
| **Change dashboard UI (hub, staff, profile, media)** | `templates/dashboard/index.html` + `templates/dashboard/manage_tournament.html` + `static/css/dashboard.css` + `static/js/modal.js` → `interfaces/web/dashboard_routes.py` |
| **Change admin UI (sidebar, stats, tables, pagination)** | `templates/admin/base.html` + `static/css/admin.css` + any `admin/*.html` → `interfaces/web/admin_routes.py` / `fide_routes.py` |
| **Change notifications (dropdown vs inbox)** | `templates/base.html` (bell markup) + `static/js/app.js` (dropdown) vs `templates/notifications/index.html` + `static/js/notifications.js` (inbox) → `interfaces/web/notification_routes.py` (`/api/notifications*`) + `application/notification_service.py` |
| **Change modal behaviour / add a new modal** | `static/js/modal.js` + `static/css/dashboard.css` (`.modal-*`) → `dashboard/index.html` (example usage) |
| **Change responsive behaviour** | `static/css/responsive.css` → the component's owner file (e.g. `tournament.css`) → 3 viewports (360/768/1200) |
| **Change print output** | `templates/print/base.html` + `static/css/print.css` + any `print/*.html` → `interfaces/web/print_routes.py` — verify via Print Preview, not screenshots |
| **Change auth (login/register)** | `templates/auth/*.html` + `static/css/layout.css` (`.login-*`) → `interfaces/web/auth_routes.py` + `application.auth.*` |
| **Change any API consumed by JS** | `static/js/*.js` (the `fetch` call) → `interfaces/web/*routes.py` (the `@…route` handler) → `application/*` service that validates |
| **Change a Flask route used by the frontend** | The route file in `interfaces/web/` → its `render_template` templates (see §3) → their CSS/JS (see §5/§6) → the application service it delegates to |
| **Add a new tournament page** | `templates/tournament/view.html` (reference) → `static/css/tournament.css` → new template in `templates/tournament/` → wire via `interfaces/web/tournament/__init__.py` |
| **Add a new admin page** | `templates/admin/base.html` (reference) → `static/css/admin.css` → new `admin/*.html` → `interfaces/web/admin_routes.py` or `fide_routes.py` |

Goal: open 2–4 files, not the whole `interfaces/web/` + `templates/` + `static/` trees.

---

## 18. Change Impact Guide

### A. Touching a global CSS file

| File | Which pages may visually regress |
|------|----------------------------------|
| `base.css` | Everything. Variable edit is a full-product repaint. |
| `components.css` | Most of the ~30 screen templates — search for the altered class (`.btn`, `.badge`, `.form-`, `.alert`, `.notification-*`, `.tiebreak-*`). |
| `tables.css` | Any `tournament/players.html`, `tournament/rounds.html`, `round_view.html`, `tournament/crosstable.html`, `print/*`. |
| `tournament.css` | Any `tournament/*.html`, `tournament/players.html`, `summary.html`, `crosstable.html`, `player_detail.html`, `rounds.html`. No admin/dashboard/print impact (those don't load it as feature). |
| `responsive.css` | Every page on at least one breakpoint — always test 360/768/1200 after touching. |
| `admin.css` | All `admin/*` + `fide_dashboard` + `verifications`. No tournament/dashboard/print impact. |
| `dashboard.css` | `dashboard/index.html` + `manage_tournament.html` only. |
| `print.css` | `print/*` + `export/trf` only. |

### B. Touching `base.html` — blast radius: the entire site

* Header/nav changes: render `/`, `/<public_id>`, `/dashboard`, `/admin`, `/notifications`.
* `extra_css` / `extra_js` block move/rename: every child template that relies on them stops loading its assets (400+ silent failures).
* `<meta name=csrf-token>` rename/remove: every POST form + every `fetch` silently 403s.
* Flash message block (`get_flashed_messages`) removal: success/error feedback disappears site-wide.
* Notification bell markup change (`#notifBell/#notifDropdown/#notifDropdownBody` IDs): `app.js: initNotificationDropdown` crashes or silently does nothing.
* Unread count context processor (`unread_notifications_count`) rename: Jinja `Undefined` on every authenticated page.

**Always** View-Source and confirm 6 CSS links + `app.js` after touching this file.

### C. Touching `app.js` — blast radius: every page

* `injectCSRFToken` break → every `POST` form (login, create, settings, price, registrations, round mutations) silently loses CSRF protection and server-rejects.
* `initNotificationDropdown` break → bell dropdown on every authenticated page.
* `initToggleHandlers` break → admin sidebar drawer (mobile) stops opening.
* `escapeHtml` change → XSS surface in bell dropdown items, registration discount list, backup import preview.
* Anything that adds a global listener must be idempotent off the targeted page (the current file already is — `if (!el) return`).

Test: submit any POST form, open bell, toggle admin sidebar (mobile).

### D. Changing a feature template

Checklist:

1. Its owning route(s) (see §3) — what context vars does the template expect and which can be missing (`or ''`, `if profile`)?
2. Its CSS dependencies (see §5) — did you use a class that only exists in a *different* feature CSS not loaded here?
3. Its JS dependencies (see §6) — does the script expect `#id` / `[data-*]` that you renamed/removed?
4. The application service the route delegates to — does the template assume a shape the service no longer returns?
5. Mobile + RTL — resize and confirm `dir="rtl"` did not clip/overflow.

### E. Changing a route

Check:

* Templates it `render_template`s (see §3) — every conditional branch (`if request.method == "POST"` vs `GET`, `require_admin` redirect vs render).
* `url_for('*.endpoint')` callers (templates + JS) — renaming a route or its `public_id` param breaks every link/form/fetch that targets it.
* The application service it now calls — transaction ownership and `flash` category.
* Auth/capability check (`require_admin` / `require_tournament_manager` / `require_result_editor` / `@role_required`) — tightening or loosening has tournament-level consequences.

### F. Changing a shared component (button, badge, table, alert)

Checklist:

1. Grep the class name across `templates/` — open 3–4 hits from *different* sections (tournament vs admin vs dashboard vs notifications).
2. Those pages on 2–3 breakpoints (mobile is where shared component padding sync issues hide).
3. Print pages only if the class is also used there (it shouldn't be — see §15).

### G. Checklist for *any* frontend change

* [ ] Which templates did I *actually* verify (not guess)?
* [ ] Which CSS files did I *actually* open (not grep)?
* [ ] Which JS `fetch` did I *actually* trigger (not static-read)?
* [ ] Mobile (≤600), tablet (601-968), desktop (≥969)
* [ ] RTL — no LTR-only `right/left` regression
* [ ] If API JSON changed — does every `js/*.js` consumer still parse it?

---

## 19. Architectural Decisions / Why Things Are This Way

Only decisions supported by the current tree and the refactor diff (`git log --stat` on `dev` since the audit) are recorded here.

| Decision | Why | Alternative rejected |
|----------|-----|----------------------|
| **Extract significant inline JS to `static/js/` (app.js, tournament-view.js, notifications.js, …)** | Inline `<script>` blocks in 7 templates duplicated fetch/CSRF/escape logic and made history-blame noisy; extraction gives a single testable module per surface and lets the browser cache it. Kept the 1-tile shim in `tournament/view.html` because passing `cumulativeAgeCategory` via `data-*` would have required restructuring that template's Jinja loops. | Embedding all JS in `base.html` (worse cache granularity) or inlining forever (worse reuse). |
| **Extract significant inline CSS to feature files (`admin.css`, `dashboard.css`, `print.css`)** | `admin/base.html` shipped 84 lines + `admin/dashboard.html` 106 + `admin/users.html` 95 of `<style>` that duplicated `.badge/.admin-table` and conflicted with the token palette; `print/base.html` shipped 127 lines of print-only rules that polluted screen pages if merged. Feature files give a single source of truth per *section*. | A per-template CSS file for each of the 50 templates — cache fragmentation and repeated variable re-declarations. |
| **Keep `tournament.css` globally loaded even though tournament-specific** | ~15 templates share it; splitting it per-tournament-page would have meant 10 tiny files where any “which file did my tab padding come from?” question becomes a hunt. A single global tournament file keeps cache hit rate high and ordering trivial. | 10 one-off `tournament-view.css`, `tournament-crosstable.css`, … files — rejected for fragmentation. |
| **`data-*` attributes for Jinja → JS** (e.g. `data-api-url`, `data-base-price`, `data-cumulative-age-category`, `data-id`, `data-target/data-action/data-class`, `data-modal-trigger/close`) | Keeps `.js` files Jinja-free and lintable, makes the contract visible in View Source, and isolately testable from the template. `registration.js` reading `dataset.apiUrl` is a concrete example. | Embedding `{{ url_for(...) }}` / `{{ tournament.base_price }}` inside `.js` files — breaks if the file is ever cached/CDN-served and makes JS unlintable. |
| **No Jinja macros / `templates/components/` yet** | The refactor found repeated `.page-header`, `.admin-actions`, `.empty-state`, `.card` *markup* but extracted them into CSS utility classes + single-line `include`-like reuse was not worth the abstraction cost yet: a macro that merely wraps a `<div>` trades one line for indirection with no consistent prop set. The design instead added a small utility-class tail to `tournament.css` (see §9) and kept `dashboard/index.html` card variance as scoped classes. Macros can be added later when a second real consumer demands them. | Blindly wrapping every repeated wrapper in a macro “to reduce line count” — rejected (audit constraint: *do not create abstractions merely to reduce line count*). |
| **No frontend framework / bundler / npm** | Product constraint from `docs/FRONTEND_UI_LAYER.md` §3 and `AGENTS.md`: Vanilla JS + Custom CSS + Vazirmatn + RTL is the stack. A framework would triple the onboarding cost for a team that ships a Flask monolith on cPanel shared hosting (`passenger_wsgi.py`). The delivered JS (≈500 lines total across 9 files) does not justify a toolchain. | React / Vue / Tailwind / Bootstrap / Webpack — rejected without an explicit architectural decision record. |
| **Generic `modal.js` contract via `data-modal-trigger/close`** | First real modal consumer was `dashboard/index.html` (edit + claim). A generic contract lets any future page add a modal with *zero* new JS — just the two data attributes + `Modal.open/close` if needed programmatically. Focus trap + ESC + overlay close were baked in once. | Per-page `onclick="element.classList.add('active')"` handlers — duplicated, not trap-safe, not keyboard-accessible. |
| **Generic `[data-target][data-action="toggle-class"]` dispatcher in `app.js`** | First consumer was the admin sidebar drawer (`data-target=".admin-sidebar" data-action="toggle-class" data-class="open"`). A one-line dispatcher lets future toggles reuse it instead of adding per-page handlers. | Inline `onclick="document.querySelector('.admin-sidebar').classList.toggle('open')"` in every page needing a drawer. |
| **Print stays standalone** | `print/base.html` not extending `base.html` and `print.css` not loaded on screen were kept because unifying them once bled header/footer/responsive rules into the `@page { A4 landscape }` sheet and made Print Preview unreliable. | Merging print into the screen layout with `@media print` overrides everywhere — rejected (harder to reason about, fragile ordering). |
| **Utility-class tail in `tournament.css` (not a separate `utilities.css`)** | `tournament/view.html` alone needed 60+ `style=""` replacements after extraction. A standalone utilities sheet would be loaded even on admin/print (waste), and a Tailwind-like split would violate the “no dozens of tiny files” constraint. Inlining the ~120-line tail at the end of the already-global `tournament.css` kept the change local to the page that needed it. | A separate `utilities.css` or utility framework — rejected. |
| **One source of truth for admin vs. dashboard vs. screen tables** | `tables.css` owns `data-table/crosstable`; `admin.css` owns `admin-table`; `print.css` owns print tables. Merging them into one “unified table” would have forced admin/print to carry screen-specific sticky header + zebra + responsive hint code. | Single `.table` for everything — rejected for cross-section coupling. |

---

## 20. Maintenance / Onboarding Instructions

### Workflow for every frontend task

```
1. Read this document (docs/FRONTEND_UI_LAYER.md) — 10 minutes.
2. Identify the affected feature in §2 and its routes in §3.
3. Follow the dependency maps in §5 (CSS) and §6 (JS) to list the exact
   templates / stylesheets / scripts you must open.
4. Inspect only those files. Do not grep the whole codebase as a first step.
5. Make the smallest change that satisfies the requirement — prefer reusing
   an existing class / data-* contract (see §9 / §10) over adding a new one.
6. Check the blast radius in §12 and run the impact checklist in §18.
7. Manually verify: 3 viewports (360/768/1200) + RTL + flash + CSRF.
8. Update this document ONLY if the architecture (a blueprint, a template
   relationship, a CSS/JS ownership decision, a contract) materially changed.
   Typo or comment fixes do not require a doc update.
```

### Rules for keeping this doc truthful

* Verify every `Blueprint`, `render_template`, `url_for('static', …)` and `{% extends %}` claim against the current tree before committing a doc edit. The verification commands are:

  ```powershell
  # Blueprints + routes → templates
  Get-ChildItem -Path interfaces/web -Filter *.py -Recurse |
    ForEach-Object { Select-String -Path $_.FullName -Pattern "render_template|Blueprint|@.*\.route" }

  # Template inheritance + blocks
  Get-ChildItem -Path templates -Filter *.html -Recurse |
    ForEach-Object { Select-String -Path $_.FullName -Pattern 'extends|extra_css|extra_js' }

  # Actual CSS/JS wiring
  Get-ChildItem -Path templates -Filter *.html -Recurse |
    ForEach-Object { [regex]::Matches((Get-Content $_.FullName -Raw), "url_for\('static', filename='(css|js)/[^']+'") }
  ```

* Do not document the old inline-CSS/JS architecture as if it still exists.
* Do not invent relationships. If a template does not load `admin.css`, do not say it does.
* Do not add a new CSS/JS file without adding it to §5/§6 and §8/§7.
* Do not add a new blueprint route without adding it to §2/§3 and, if it touches the UI, to §17/§18.

> **This document is the architectural map of the frontend. It is not a replacement for inspecting the actual source files when implementing a change; it is intended to tell the developer/agent *which* source files need to be inspected.**

---

*Last verified: 2026-08-30. Post-refactor tree — 9 CSS files, 9 JS files, 55 templates (3 standalone print). Global entry: `base.html` → `static/css/{base,layout,components,tables,tournament,responsive}.css` + `static/js/app.js`.*
