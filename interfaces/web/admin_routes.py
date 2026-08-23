# interfaces/web/admin_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import current_user, login_required
from application.admin_service import AdminService
from interfaces.web.decorators import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
@login_required
@admin_required
def dashboard():
    """Admin dashboard overview."""
    stats = AdminService.get_dashboard_stats()
    return render_template("admin/dashboard.html", stats=stats, active_section="dashboard")

@admin_bp.route("/admin/users")
@login_required
@admin_required
def manage_users():
    """User management page with search and filter."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()
    
    result = AdminService.get_users_paginated(page, per_page, search, role_filter)
    
    return render_template(
        "admin/users.html",
        users=result['users'],
        pagination=result,
        search_query=search,
        role_filter=role_filter,
        active_section="users"
    )

@admin_bp.route("/admin/users/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    """User detail page."""
    user = AdminService.get_user_detail(user_id)
    if not user:
        abort(404)
    return render_template("admin/user_detail.html", user=user, active_section="users")

@admin_bp.route("/admin/users/<int:user_id>/add-role/<role_name>", methods=["POST"])
@login_required
@admin_required
def add_role(user_id, role_name):
    """Add a role to a user."""
    try:
        AdminService.add_role(user_id, role_name, current_user.id)
        flash(f"نقش '{role_name}' با موفقیت افزوده شد.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.user_detail", user_id=user_id))

@admin_bp.route("/admin/users/<int:user_id>/remove-role/<role_name>", methods=["POST"])
@login_required
@admin_required
def remove_role(user_id, role_name):
    """Remove a role from a user."""
    try:
        AdminService.remove_role(user_id, role_name, current_user.id)
        flash(f"نقش '{role_name}' با موفقیت حذف شد.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.user_detail", user_id=user_id))

@admin_bp.route("/admin/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle system admin status."""
    try:
        action = AdminService.toggle_admin(user_id, current_user.id)
        flash(f"دسترسی ادمین سیستم با موفقیت {('فعال شد' if action == 'added' else 'غیرفعال شد')}.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("admin.user_detail", user_id=user_id))

# Keep legacy route for backward compatibility
@admin_bp.route("/admin/users/<int:user_id>/toggle-role/<role_name>", methods=["POST"])
@login_required
@admin_required
def toggle_role_legacy(user_id, role_name):
    """Legacy toggle role endpoint - redirects to new add/remove logic."""
    try:
        action = AdminService.toggle_role(user_id, role_name)
        flash(f"نقش {role_name} با موفقیت {('افزوده شد' if action == 'added' else 'حذف شد')}.", "success")
    except ValueError as e:
        flash(str(e), "error")
    
    return redirect(url_for("admin.manage_users"))

@admin_bp.route("/admin/tournaments")
@login_required
@admin_required
def manage_tournaments():
    """Tournament management page."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    result = AdminService.get_tournaments_paginated(page, per_page, search, status_filter)
    
    return render_template(
        "admin/tournaments.html",
        tournaments=result['tournaments'],
        pagination=result,
        search_query=search,
        status_filter=status_filter,
        active_section="tournaments"
    )

@admin_bp.route("/admin/notifications")
@login_required
@admin_required
def notification_status():
    """Notification system status page."""
    stats = AdminService.get_notification_stats()
    return render_template("admin/notifications.html", stats=stats, active_section="notifications")

@admin_bp.route("/admin/system")
@login_required
@admin_required
def system_health():
    """System health check page."""
    health = AdminService.get_system_health()
    return render_template("admin/system.html", health=health, active_section="system")