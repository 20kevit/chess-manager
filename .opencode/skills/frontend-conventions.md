# Frontend Conventions — RTL, Tokens, Contracts

## Purpose

Keep UI changes consistent with the Persian/RTL design system and avoid the
high-blast-radius mistakes (global CSS/JS, CSRF, print bleed). The frontend is
vanilla: Jinja2 + HTML/CSS (variables) + vanilla JS. No Bootstrap, Tailwind,
jQuery, React, bundlers, or npm.

## When to use

Any change to `templates/`, `static/css/`, `static/js/`, or a route's rendered
context. Read `docs/FRONTEND_UI_LAYER.md` (authoritative map) for the exact
route→template→asset wiring of the touched page.

## Source of truth

- `docs/FRONTEND_UI_LAYER.md` (§5 CSS map, §6 JS map, §9 components, §10
  Jinja→JS contracts, §12 blast radius, §18 impact checklists)
- Tokens: `static/css/tokens.css`; contract test: `tests/test_frontend_tokens.py`
- Global behavior: `templates/base.html`, `static/js/app.js`, `static/js/ui.js`

## Operational rules

- **RTL/Persian default.** Every layout decision verified in `dir="rtl"`.
  Persian copy in templates/flash messages; code/comments/commit messages in
  English. Vazirmatn font; use `.num`/`.ltr` isolation for Latin/numbers.
- **Semantic tokens only.** New UI consumes `static/css/tokens.css` variables
  (`--surface`, `--text`, `--border`, `--primary`, …). No hardcoded light-theme
  hex in CSS (outside `tokens.css`/`print.css`/documented fixed bands) or
  templates. Enforced by `tests/test_frontend_tokens.py`. Dark mode retunes the
  same tokens (`[data-theme="dark"]`) — never fork component rules per theme.
- **File ownership heuristic** (not file-count matching): a feature CSS/JS only
  for a coherent *section* (admin, dashboard, print). Otherwise extend the
  owning global (`components.css` for buttons/badges/alerts/cards,
  `forms.css` for fields, `tables.css` for screen tables, `tournament.css` for
  tournament chrome, `responsive.css` for overrides — the ONLY file with
  `@media`). Small contextual `<style>` may stay inline only where extracting
  would create a one-off file (existing examples: register price-box, board
  rows). Never add per-component files.
- **Server→JS only via `data-*`.** `data-api-url`, `data-base-price`,
  `data-id`, `data-target/data-action/data-class`, `data-modal-trigger/close`.
  External `.js` must not contain `{{ }}` (one documented 3-line shim in
  `tournament/view.html` excepted). Destructive actions use `data-confirm` +
  `UI.openConfirm` — never native `confirm()` or inline `onclick`; wire with
  `addEventListener` / `data-*` dispatch.
- **CSRF via meta, not body.** `base.html` provides `<meta name="csrf-token">`;
  `app.js:injectCSRFToken()` appends inputs to every `form[method=POST]`;
  `fetch` uses `X-CSRFToken`. Keep `app.js` on every page — removing it breaks
  all POSTs and the notification bell.
- **Links/forms always `url_for`** (including `public_id=...`); never hardcoded
  URLs. Preserve `extra_css`/`extra_js` additive order (global → feature).
- **Public vs workspace.** Public tournament pages stay capability-free and
  identical for every visitor; staff UI lives in the management workspace
  (`templates/manage/`, shell `manage/shell.html`) with disabled-not-hidden
  entries. Never inject `{% if can_manage %}` controls into public templates
  (see `auth-rbac.md`).
- **Static versioning.** CSS/JS URLs carry a release `?v=…` query (long
  immutable cache); bump it per release touching frontend, otherwise visitors
  strand on stale assets.
- **Print isolation.** `print/base.html` is standalone (never extends
  `base.html`); `print.css` only. Print changes cannot affect screen UI and
  vice versa — verify via Print Preview, not screenshots.

## Validation (every UI change)

- [ ] Templates actually rendered (not guessed), CSS files actually opened,
      JS `fetch` actually triggered (`FRONTEND_UI_LAYER.md` §18G).
- [ ] 3 viewports (360/768/1200) + RTL + flash + CSRF submit.
- [ ] Blast-radius check per §12/§18 (`base.html`/`components.css`/`app.js`
      changes affect the whole site).
- [ ] `pytest tests/test_frontend_tokens.py tests/test_frontend_hardening.py -q`.

## Escalation

Escalate before: adding a CSS/JS file, a framework/bundler, a new global
behavior in `app.js`/`ui.js`, merging print into the screen layout, or changing
the modal/confirm/`data-*` contracts. Keep the contract stable.
