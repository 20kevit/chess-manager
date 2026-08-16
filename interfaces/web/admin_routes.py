# interfaces/web/admin_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from application.admin_service import AdminService

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/users")
@login_required
def manage_users():
    if not current_user.is_admin:
        flash("دسترسی به این بخش فقط برای ادمین سیستمی مجاز است.", "error")
        return redirect(url_for("tournament.index"))
    
    users = AdminService.get_all_users()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/admin/users/<int:user_id>/toggle-role/<role_name>", methods=["POST"])
@login_required
def toggle_role(user_id, role_name):
    if not current_user.is_admin:
        flash("دسترسی غیرمجاز.", "error")
        return redirect(url_for("tournament.index"))
    
    try:
        action = AdminService.toggle_role(user_id, role_name)
        flash(f"نقش {role_name} با موفقیت {('افزوده شد' if action == 'added' else 'حذف شد')}.", "success")
    except ValueError as e:
        flash(str(e), "error")
    
    return redirect(url_for("admin.manage_users"))