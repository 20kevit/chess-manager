# Web Layer Context (Interfaces & Routing)

## 1. Responsibility
The `interfaces/web/` layer is the entry point for all HTTP requests. It acts as a controller that parses HTTP requests, extracts parameters, delegates execution strictly to the `application/` layer (Services), and returns HTML templates or JSON responses.

## 2. Dependency Direction
Dependencies must strictly point inward toward the Application and Infrastructure layers.

* `interfaces (Web)` ──> `application (Services)`
* `interfaces (Web)` ──> `infrastructure (Repositories)`
* `application` ──X──> `interfaces` (STRICTLY PROHIBITED)
* `domain` ──X──> `interfaces` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Implement any business logic, pairing logic, or data transformation here.
- Call `db.session.commit()`, `db.session.rollback()`, or `db.session.flush()`. Transaction management belongs to the Service layer.
- Query the database directly using `Model.query.filter()`. Always use `Repository` methods.
- Pass `admin_code` via URL parameters in any generated link or redirect (Rule 4 Enforcement).
- Create separate endpoints for admin views (e.g., `/admin/standings`). Use the Unified UI approach.

**MUST:**
- Use `require_admin(public_id)` from `admin_auth.py` at the top of any route that modifies data.
- Catch exceptions thrown by the Service layer and use Flask's `flash()` to display user-friendly error messages.
- Always redirect to the Unified Dashboard (`tournament.view`) after successful state-mutating operations.
- Extract all form data cleanly and pass it as dictionaries or specific arguments to the Service layer.

## 4. Module Specifications

### A. Authentication (`admin_auth.py`)
- **Session-Based Only:** Admin authorization is stored securely in the Flask session (`session[f"admin_{public_id}"]`).
- **Core Helper:** `require_admin(public_id)` must be used by other blueprints to verify access. It returns the `TournamentModel` if authorized, or `None` (requiring an abort or redirect by the caller).
- **No URL Leaks:** The `admin_code` is validated upon login and never appended to `url_for()` calls.

### B. Tournament Routes (`tournament_routes.py`)
- **Unified View:** The `view(public_id)` endpoint serves BOTH public users and arbiters. It dynamically sets `is_admin = is_current_admin(tournament)` and passes it to the template, allowing the UI to adapt without changing the URL.
- **Data Delegation:** Fetches standings directly via `TournamentService.get_standings()`.

### C. Round Routes (`round_routes.py`)
- **Actions:** Handles generating new rounds, saving results, finishing rounds, and manual adjustments (swaps/locks).
- **Post/Redirect/Get Pattern:** All POST routes must `flash()` the outcome and `redirect()` back to the unified view or a specific tab to prevent form resubmission.

### D. Player Routes (`player_routes.py`)
- **CRUD Operations:** Endpoints for adding, editing, withdrawing, and deleting players.
- **FIDE Integration:** Provides the `/api/fide/<fide_id>` endpoint (exempt from CSRF if needed) which acts as a proxy to `PlayerService.lookup_fide`.

### E. Backup & Import/Export (`backup_routes.py`)
- **Provider Architecture Endpoints:** Implements RESTful routes for exporting/importing via dynamic providers (`/export/<provider_name>`).
- **File Validation:** Validates file formats and sizes (e.g., 5MB limit) before passing the content to `ImportExportService`.
- **AJAX Support:** The `/create/from-backup` endpoint supports AJAX requests (returning JSON instead of HTML) for dynamic UI previews.

## 5. Error Handling & Middlewares
- **Decorator:** `handle_route_errors` (in `error_handlers.py`) should be used to catch `ValueError` or generic exceptions, flash them, and safely redirect the user.
- **HTTP Aborts:** Use `abort(404)` immediately if `public_id` format is invalid or the entity does not exist in the Repository.

## 6. Testing Requirements
- Use Flask's `test_client` to write integration tests for these routes.
- Tests must simulate active sessions to verify that unauthorized `POST` requests are rejected.