"""
Admin authentication via session.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from infrastructure.repositories import TournamentRepository
from domain.tiebreak.calculators import ALL_TIEBREAKS_DISPLAY

admin_auth_bp = Blueprint("admin_auth", __name__)


def get_admin_tournament(public_id):
    """
    Check if current session has admin access to this tournament.
    Returns tournament or None.
    """
    if not tournament:
        return None

    session_key = f"admin_{public_id}"
    if session.get(session_key) == tournament.admin_code:
        return tournament

    return None


def require_admin(public_id):
    """
    Helper for other routes to ensure admin access.
    Returns the tournament object or None.
    """
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament: return None
    
    session_key = f"admin_{public_id}"
    if session.get(session_key) == tournament.admin_code:
        return tournament
    return None


@admin_auth_bp.route("/<public_id>/admin/login", methods=["GET", "POST"])
def admin_login(public_id):
    """Arbiter login page."""
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament: abort(404)

    # Use a consistent session key: admin_<public_id>
    session_key = f"admin_{public_id}"
    
    if session.get(session_key) == tournament.admin_code:
        # Already logged in, go to the unified public URL
        return redirect(url_for("tournament.view", public_id=public_id))

    if request.method == "POST":
        code = request.form.get("admin_code", "").strip()
        if code == tournament.admin_code:
            session[session_key] = code
            flash("ورود موفقیت‌آمیز بود.", "success")
            # Redirect to the main UNIFIED URL (not /admin/)
            return redirect(url_for("tournament.view", public_id=public_id))
        else:
            flash("کد مدیریت اشتباه است.", "error")

    return render_template("tournament/admin_login.html", tournament=tournament)


@admin_auth_bp.route("/<public_id>/admin/logout")
def admin_logout(public_id):
    """Logout and clear session."""
    session.pop(f"admin_{public_id}", None)
    flash("خروج موفقیت‌آمیز بود.", "success")
    return redirect(url_for("tournament.view", public_id=public_id))

@admin_auth_bp.route("/<public_id>/admin/")
def admin_panel(public_id):
    """پنل مدیریت اصلی"""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    from application.tournament_service import TournamentService
    standings = TournamentService.get_standings(tournament)

    return render_template(
        "tournament/view.html",
        tournament=tournament,
        is_admin=True,
        **standings,
    )


@admin_auth_bp.route("/<public_id>/admin/link/<admin_code>")
def admin_link_login(public_id, admin_code):
    """
    ورود با لینک مستقیم.
    admin_code فقط یک بار در URL می‌آید، بعد در session ذخیره می‌شود.
    """
    tournament = TournamentRepository.get_by_admin(public_id, admin_code)
    if not tournament:
        abort(403)

    session[f"admin_{public_id}"] = admin_code
    return redirect(url_for("admin_auth.admin_panel", public_id=public_id))