# CHESS-MANAGER — UI/UX Redesign Specification

> Phase 0 deliverable. Source of truth: repository as inspected 2026-10-04.
> Stack stays: Flask + Jinja2 + vanilla CSS/JS, no framework, no build, no Node.

## 1. Product design vision

«A professional chess tournament control system that is powerful without being complicated.»
Calm, dense-where-needed operator tool + simple mobile-first public surface.
Clarity over decoration: every page answers where am I / which tournament / what state /
what needs attention / what can I do next / where is everything else.

## 2. User contexts

| Context | Priority | Needs |
|---|---|---|
| Player / public (often mobile) | standings, pairings, board, result, tournament info | fast scan, readable tables, LTR-safe numbers |
| Arbiter / organizer (desktop-first, mobile-usable) | round lifecycle, result entry, players, registrations, reports | density, keyboard flow, pending-work visibility |
| System admin | users, roles, FIDE data, health, notifications | tables + status queues |

## 3. Information architecture (14 blueprints)

- Global: `/` index+search, `/search`, auth (`/login /register /logout`),
  dashboard hub (`/dashboard`, profile, roles, verification, notification settings,
  staff invite/accept), notifications inbox, admin (`/admin*`, FIDE, verifications),
  public player profile (`/player/<id>`), print (`/print/*`), payment callback.
- Public tournament (keyed by 8-digit `public_id`, structurally identical for
  every visitor): Overview(view) · Players · Rounds · Round detail (read-only) ·
  Crosstable · Summary · Player detail · Rulebook PDF download.
- Tournament Management Workspace (`/<public_id>/manage*`, `manage_routes.py`,
  shell `templates/manage/`): Overview (operational command center) · Players ·
  Rounds · Round detail (result entry) · Standings · Crosstable · Tiebreaks ·
  Output (printing/exports) · Registrations · Announcements · Settings ·
  Rulebook · Staff & permissions · Pricing · Prizes. One workspace for all
  roles; manager-only entries render disabled for result-editors. The retired
  dashboard management hub redirects into the workspace (`manage.staff`).
- No invented routes. Sidebar links only to endpoints in `interfaces/web/`.

## 4. Navigation model

- Global header (all pages): brand → Home, Dashboard, Create (organizer), Admin
  (system admin), notification bell, auth links; mobile hamburger → drawer.
- Public tournament pages: tournament context header (name, status badge, round
  progress, city/time-control meta, Register action) + public sub-nav
  (Overview, Players, Rounds, Crosstable, Summary) — identical for everyone.
- Management workspace: compact tournament identity bar (name, status, city,
  time control, round x/y, start date, public-page return link) + grouped
  capability-aware sidebar (Tournament · Round operations · Tournament data ·
  Registration · Output · Configuration), collapsible to drawer <1024px with
  focus trap + ESC + overlay; unavailable entries render disabled with a
  reason tooltip instead of disappearing.
- Admin sidebar grouped: Overview (dashboard, system) · People (users, roles,
  verifications) · Tournaments (all) · Data (FIDE) · Messaging (notifications).
  Group labels, SVG icons, `aria-current="page"`, collapsible to drawer <1024px
  with focus trap + ESC + overlay.
- Breadcrumbs on workspace pages (overview → section → detail).

## 5. Color system

Brand foundation (restrained): Primary Blue `#1976D2`, Deep `#12529A`,
Accent Orange `#FF8A00`, Soft Orange `#FFF0DD`, Soft Blue `#EAF4FF`,
Off White `#FAFCFF`, Dark Text `#17212B`.
Neutrals carry 90% of UI. Blue = primary actions/active nav/links/selected.
Orange = meaningful emphasis only (pending attention, brand accents, special calls).
No gradients/glass/neon; flat surfaces, subtle borders, subtle elevation.

## 6. Typography

Vazirmatn kept (CDN). Scale: display 28/1.4 · page-title 22 · section 17 ·
subsection 15 · body 14/1.8 · small 12.5 · caption 12 · label 13/600 ·
table-header 12.5/700 uppercase-ish spacing · button 14/600 · nav 14.
Tabular numerals for ratings/ranks/scores/boards (`font-variant-numeric:
tabular-nums`), `.num` utility, LTR isolation for FIDE IDs/scores/dates/URLs.

## 7. Spacing / layout / shape

Scale 4·8·12·16·24·32·48·64 (`--space-*`). Container 1200px desktop,
16px mobile gutters, 720px narrow (auth/public forms). Radii 6/8/12/16,
pill only for badges. Borders 1px neutral; elevation 3 subtle shadows.
Breakpoints: 390 · 600 · 768 · 1024 · 1200.

## 8. Responsive strategy

Mobile-first public pages; desktop-density management tables with horizontal
scroll + sticky header (+ sticky first column for standings/pairings).
Verify 360/390/768/1024/1200+/1440. Touch targets ~44px. Drawer nav <1024px.
Print pages isolated (`print/base.html` + `print.css`, A4 landscape).

## 9. Component inventory (canonical — `templates/components/ui.html` macros)

Button(5: primary/secondary/ghost/danger/icon) · IconButton · Badge/Status ·
Alert(4) · Card · Stat · PageHeader · SectionHeader · Breadcrumbs ·
TournamentHeader · Table shell · Empty/Loading/Error states · Modal/ConfirmDialog ·
Pagination · SearchField · FilterBar · FormField · Tabs · Toast (selective).

## 10. Table system (`tables.css` single source)

`.tbl-wrap` scroll container + `.tbl` base: sticky `thead`, zebra optional,
hover, selected, `.is-withdrawn` (opacity + strikethrough + label, never color
alone), numeric `.num` columns, action cell, compact/comfortable density,
`<caption>`, `th scope`, `aria-sort` where sortable, empty/loading/error rows.
Migrated first: players, rounds, round view, standings, crosstable, registrations.

## 11. Form system (`forms.css`)

`.field > label(+required) + control + hint + error`; `aria-invalid`,
`aria-describedby`, field errors + summary; native `<select>` kept for results;
Input/Select/Textarea/Checkbox/Radio/Search/File patterns; focus ring;
invalid ring; disabled; 44px targets on touch.

## 12. Status system

One badge set with label+icon+color: active/approved/completed/success ·
pending/ongoing · warning/half-bye · danger/withdrawn/error · info/draft ·
neutral/muted. Cross-table cells keep text symbols (1, ½, 0, +, −, *) plus
`aria-label`, not color alone.

## 13. Modal system (`modal.js` extended)

Single `Modal.open/close`, overlay click, ESC, focus trap + restore,
`role="dialog" aria-modal`, confirm variant (`data-confirm-*`) replacing all
native `confirm()` (~15 destructive actions: delete/withdraw/reset/remove).
Explains what happens + reversibility + destructive emphasis.

## 14. Iconography (`templates/components/icons.html`)

Inline SVG set, `currentColor`, 16/20px, stroke-consistent: home, dashboard,
plus, trophy, users, rounds(layers), pairing(vs), table, chart, settings,
bell, search, chevron, close, check, alert, clock, card, doc, download,
upload, print, link, shield, globe, logout, menu. `aria-hidden` decorative,
`aria-label` functional. No new dependency.

## 15. Accessibility rules

Semantic landmarks/headings order, skip link, visible `:focus-visible`,
labels `for/id`, `th scope`, caption, keyboard tabs/drawer/modal/DnD fallback
(up/down buttons for tiebreak order), `aria-live` for price preview + toasts,
`role="status"` flashes, reduced-motion respected, contrast AA (muted text
≥ `#5B6B7B` on light), no keyboard traps, color never sole carrier.

## 16. Dark mode

Same semantic tokens, `[data-theme="dark"]` override: tuned surfaces
(`#0F1722/#16202C/#1D2A38`), borders, text hierarchy, status-subtle fills,
table hover, form fills, modal/dropdown surfaces. Toggle in header persisted
in `localStorage`, default light, respects `prefers-color-scheme` on first run.

## 17. Mobile strategy

Public flows designed mobile-first. Management usable: drawer nav, stacked
headers/actions, scroll tables, full-width result selects, large result buttons.
`responsive.css` consolidated to the 5 breakpoints above.

## 18. Page migration plan

P1 shell: tokens→base→components→forms→tables→navigation→base.html/admin base/UI JS.
P2 tournament workspace: view (header+tabs+standings+pairings), rounds,
round_view, players, crosstable, summary. P3 dashboard hub, auth, index/search,
registrations, settings/pricing/prizes/rulebook, notifications, player profile,
admin pages, errors. P4 print CSS token-align (structure kept).

## 19. CSS architecture (final)

```text
static/css/
  tokens.css      # palette, semantic, type, space, radii, shadow, motion, themes
  base.css        # reset, body, typography, utilities (ltr/num/visually-hidden)
  components.css  # buttons, badges, alerts, cards, stats, page headers,
                  #   empty/loading/error, modal, pagination, breadcrumbs, toast
  forms.css       # field system + controls + validation states        (NEW)
  tables.css      # unified table + crosstable cells + legend          (converged)
  navigation.css  # header, drawer, sidebar, tabs, tournament nav      (NEW)
  layout.css      # container, hero, footer, public sections           (trimmed)
  tournament.css  # tournament header, pairings extras, summary        (trimmed)
  admin.css       # admin tables/stats reuse tokens                    (trimmed)
  dashboard.css   # dashboard layout reusing components               (trimmed)
  responsive.css  # breakpoint consolidation only                     (trimmed)
  print.css       # print preserved, token-aligned
```

Rules: no framework, no per-component files, no large inline blocks, tokens over
hex, logical props over physical, `extra_css/js` additive per page.

## 20. Jinja component strategy

`templates/components/ui.html` (macros: page_header, badge, alert, empty_state,
stat, search_field, pagination), `templates/components/icons.html` (svg icon
macro), `templates/components/tournament_header.html`. Gradual adoption: new and
high-traffic pages use macros; legacy markup kept working via CSS class aliases.
No over-abstracted component framework.

## 21. Visual QA rules

Per phase: render-check 360/390/768/1024/1200/1440 (dev server + screenshots
where possible), RTL reading, sticky/scroll tables, drawer/modal/focus,
touch targets, wrapping numerals, dark theme, print preview for print pages.
Functionality preserved: forms/filters/search/pagination/modals/result selects/
CSRF (`meta` + `app.js`) / `url_for(public_id=...)`.

## 22. Explicit anti-patterns (forbidden)

Gradients/glass/blur/neon/animated backgrounds/bouncing · giant floating cards ·
15 button variants · every-heading-blue · orange-everywhere · color-only status ·
`confirm()` · `onclick` soup · inline `{{ }}` in JS · physical left/right ·
table font-shrink instead of scroll · hiding actions instead of explaining
disabled state · toasts as primary errors · decorative illustrations per page.

## Appendix A — Design audit (evidence, 2026-10-04)

- Duplication: buttons in 4 files (components/admin/dashboard/tournament/print);
  badges in 3 (components/dashboard/admin); tables in 3 (tables/admin/tournament:914);
  alerts only error/success globally + one-off warning; form styles duplicated in
  dashboard modal scope; 17 inline `<style>` blocks, 13 inline `<script>` blocks,
  ~30 `onclick`/`confirm()` usages, dead `main.js` (5-line console.log).
- Hardcoded hex outside tokens: tables yellows/greens, dashboard status hexes,
  components `#1f2937/#4b5563/#9ca3af`, tournament/admin assorted.
- 48 physical `left/right/border-right/margin-left` hits → logical props.
- Overlapping breakpoints 390/600/768/968/1024 incl. scattered dashboard/admin queries.
- A11y: 0× `th scope`, mostly unassociated `<label>`, icon buttons unnamed,
  color-only cells/status, thin ARIA (no tablist, live regions, sort), mouse-only
  tiebreak DnD, 32px small buttons.
- Good bones to keep: skip link, modal focus trap, CSRF meta flow, `data-*`
  Jinja→JS channel, `extra_css/extra_js` additive loading, sticky `th`, print isolation.

## Appendix B — Decisions

- Keep Vazirmatn CDN + `dir=rtl`; self-hosting deferred.
- Keep native result `<select>`s; add keyboard DnD fallback instead of custom widget.
- Keep `print/base.html` isolated; token-align only.
- `pairing-core` / `tiebreak-core` untouched; no backend/domain/schema changes.
- Test runner unavailable in this env (no Flask installed) — changes are
  frontend-only; verify via template render grep + CSS checks; run `pytest`
  where env exists.
