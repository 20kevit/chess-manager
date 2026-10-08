---
name: frontend-conventions
description: RTL and Persian UI conventions for chess-manager — design tokens, CSS ownership, Jinja-to-JS data contracts, CSRF, public-versus-workspace split, print isolation, and per-change QA. Load for any template, CSS, JS, or route-context change.
---

# Frontend Conventions — RTL, Tokens, Contracts

Vanilla stack only: Jinja2 + HTML/CSS variables + vanilla JS. No Bootstrap,
Tailwind, jQuery, React, bundlers, or npm.

## Rules

- **RTL/Persian default.** Verify every layout in `dir="rtl"`. Persian copy in
  templates/flash messages; code/comments/commits in English. Vazirmatn;
  `.num`/`.ltr` isolation for Latin/numbers.
- **Semantic tokens only** (`static/css/tokens.css`: `--surface`, `--text`,
  `--border`, `--primary`, …). No hardcoded light-theme hex outside
  `tokens.css`/`print.css`/documented fixed bands. Enforced by
  `tests/test_frontend_tokens.py`. Dark mode retunes the same tokens — never
  fork component rules per theme.
- **File heuristic** (not file-count matching): a feature CSS/JS only for a
  coherent *section* (admin, dashboard, print). Otherwise extend the owning
  global — `components.css` (buttons/badges/alerts/cards), `forms.css`
  (fields), `tables.css` (screen tables), `tournament.css` (tournament
  chrome), `responsive.css` (overrides — the ONLY file with `@media`). Never
  per-component files; tiny contextual `<style>` may stay inline only where
  extraction would create a one-off file.
- **Server→JS only via `data-*`** (`data-api-url`, `data-base-price`,
  `data-id`, `data-target/data-action/data-class`,
  `data-modal-trigger/close`). No `{{ }}` in `.js` (one documented shim in
  `tournament/view.html` excepted). Destructive actions: `data-confirm` +
  `UI.openConfirm` — never native `confirm()` or inline `onclick`.
- **CSRF via meta.** `base.html` provides `<meta name="csrf-token">`;
  `app.js` injects inputs into every `form[method=POST]`; `fetch` uses
  `X-CSRFToken`. Keep `app.js` on every page.
- **Links/forms always `url_for`** (with `public_id=...`), never hardcoded.
  Keep `extra_css`/`extra_js` additive order (global → feature).
- **Public vs workspace.** Public tournament pages stay capability-free and
  identical for every visitor; staff UI lives in `templates/manage/` with
  disabled-not-hidden entries. Never inject `{% if can_manage %}` controls
  into public templates (see `auth-rbac`).
- **Static versioning.** CSS/JS URLs carry a release `?v=…` query (long
  immutable cache); bump per frontend-touching release.
- **Print isolation.** `print/base.html` is standalone (never extends
  `base.html`); `print.css` only. Verify via Print Preview, not screenshots.

## Source of truth

`docs/FRONTEND_UI_LAYER.md` (§5/§6 wiring, §9 components, §10 contracts,
§12 blast radius, §18 checklists). It answers *which files to open* — open
them; this Skill does not replace them.

## Validation (every UI change)

Templates actually rendered, CSS actually opened, JS `fetch` actually
triggered; 3 viewports (360/768/1200) + RTL + flash + CSRF submit;
`pytest tests/test_frontend_tokens.py tests/test_frontend_hardening.py -q`.
`base.html` / `components.css` / `app.js` changes affect the whole site.

## Escalation

New CSS/JS file, framework/bundler, new global behavior in `app.js`/`ui.js`,
merging print into screen layout, or changing modal/confirm/`data-*`
contracts.
