# Frontend UI/UX Context (Templates & Styles)

## 1. Responsibility
The `templates/` and `static/` directories handle the presentation layer. The UI is built using Jinja2 templates, standard HTML5, CSS3 (with CSS Variables), and vanilla JavaScript.
The core philosophy is a **Unified UI / Single Source of Truth**: Users and Arbiters see the exact same pages, but Arbiters have extra controls injected dynamically based on their session status.

## 2. Dependency Direction
The Frontend strictly consumes data passed by the `interfaces (Web)` layer.
- Frontend ──X──> Database (PROHIBITED)
- Frontend ──X──> Domain Logic (PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Add frameworks like Bootstrap, Tailwind, React, or jQuery. The project strictly uses Custom CSS (`var(--primary)`, etc.) and Vanilla JS.
- Create separate HTML files for "Admin" views (e.g., `admin_standings.html`). Use the Unified UI approach (`{% if is_admin %}`).
- Expose the CSRF token directly on the page `{{ csrf_token() }}`. Use the meta tag `<meta name="csrf-token" content="{{ csrf_token() }}">` which is auto-injected by `base.html` JS.
- Put inline styles unless absolutely necessary for dynamic layout calculations. Use `tournament.css` or `components.css`.

**MUST:**
- Maintain RTL (Right-to-Left) orientation and Persian language support natively.
- Use `url_for('blueprint.route', public_id=tournament.public_id)` for all links. Never hardcode URLs.
- Always include `data-*` attributes for dynamic filtering (e.g., `data-age="{{ player.age_category }}"`) rather than requiring a server reload.

## 4. UI Architecture & Core Files

### A. Base Layout (`base.html` & CSS)
- **CSS Variables:** Colors are defined in `base.css` (`--primary`, `--success`, `--gray-900`, etc.).
- **Typography:** Uses `Vazirmatn` font for Persian text.
- **CSRF Auto-injector:** The base template contains a script that automatically appends a hidden `csrf_token` input to all `POST` forms on the page.

### B. The Unified Dashboard (`view.html`)
This is the heart of the application. It contains multiple hidden/visible sections controlled by JS:
- **Arbiter Toolbar (`.arbiter-toolbar`):** A sticky dark bar at the top, visible only to admins, containing quick actions (Next Round, Add Player, etc.).
- **Admin Sidebar Drawer (`#admin-sidebar`):** A hidden drawer for heavy maintenance tasks (Backup, Settings, Delete Round).
- **Tab Navigation (`.tabs`):** Switches between Standings, Rounds, Crosstable, and Settings using vanilla JS (`showTab(tabName)`).

### C. In-Place Editing (UX Philosophy)
Instead of navigating away to edit things:
- **Results:** In `view.html`, ongoing round pairings show a `<select>` dropdown for admins to input results directly inside the round tab.
- **Filtering/Highlighting:** The Standings table uses client-side JS (`highlightTable()`) to dim irrelevant rows and highlight specific age categories (e.g., U16) dynamically, recalculating visible ranks on the fly.

### D. Component Library (`components.css` & `tables.css`)
- **Buttons:** `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-small`.
- **Badges:** `.badge`, `.badge-success`, `.badge-warning`.
- **Tables:** `.data-table` wrapped in `.table-responsive` for horizontal scrolling on mobile.
- **Forms:** `.form-group`, `.form-row`, `.radio-group`.

## 5. JavaScript Guidelines
- Keep scripts embedded in the HTML using `{% block extra_js %}` if they depend on Jinja2 variables (e.g., `{{ tournament.public_id }}`).
- Use ES6 standard features (const, let, arrow functions) but avoid complex build tools (Webpack/Babel).