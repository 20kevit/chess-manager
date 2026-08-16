# interfaces/web/dashboard_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from application.auth_service import AuthService
from infrastructure.db_models import PlayerProfileModel

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def index():
    profile = current_user.profile
    return render_template("dashboard/index.html", profile=profile)

@dashboard_bp.route("/dashboard/profile/search", methods=["POST"])
@login_required
def search_profile():
    fide_id = request.form.get("fide_id", "").strip()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    
    query = PlayerProfileModel.query.filter_by(user_id=None) # فقط پروفایل‌های بدون مالک
    
    if fide_id:
        query = query.filter_by(fide_id=fide_id)
    elif first_name and last_name:
        query = query.filter(
            PlayerProfileModel.first_name.ilike(f"%{first_name}%"),
            PlayerProfileModel.last_name.ilike(f"%{last_name}%")
        )
    else:
        flash("لطفاً کد فیده یا نام و نام خانوادگی را وارد کنید.", "error")
        return redirect(url_for("dashboard.index"))
        
    search_results = query.all()
    return render_template("dashboard/index.html", profile=current_user.profile, search_results=search_results)

@dashboard_bp.route("/dashboard/profile/link/<int:profile_id>", methods=["POST"])
@login_required
def link_profile(profile_id):
    try:
        AuthService.claim_profile(current_user.id, profile_id)
        flash("پروفایل شطرنج با موفقیت به حساب شما متصل شد.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("dashboard.index"))

@dashboard_bp.route("/dashboard/profile/create", methods=["GET", "POST"])
@login_required
def create_profile():
    if current_user.profile:
        flash("شما قبلاً پروفایل دارید.", "info")
        return redirect(url_for("dashboard.index"))
        
    if request.method == "POST":
        try:
            AuthService.create_profile_for_user(current_user.id, request.form)
            flash("پروفایل شما با موفقیت ایجاد شد.", "success")
            return redirect(url_for("dashboard.index"))
        except ValueError as e:
            flash(str(e), "error")
            
    return render_template("dashboard/create_profile.html")