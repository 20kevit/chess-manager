# interfaces/web/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from application.auth_service import AuthService
from urllib.parse import urlparse

def _is_safe_redirect_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("tournament.index"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        role = "player"
        
        try:
            user = AuthService.register(email, password, password_confirm, default_role=role)
            login_user(user)
            flash("ثبت‌نام موفقیت‌آمیز بود و شما وارد شدید.", "success")
            return redirect(url_for("dashboard.index"))
        except ValueError as e:
            flash(str(e), "error")
            
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tournament.index"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        user = AuthService.authenticate(email, password)
        if user:
            login_user(user)
            flash("ورود موفقیت‌آمیز بود.", "success")
            
            # Redirect to dashboard by default, or to 'next' page if safe
            next_page = request.args.get("next")
            if next_page:
                parsed = urlparse(next_page)
                if parsed.netloc or not next_page.startswith('/'):
                    next_page = None
                    
            return redirect(next_page or url_for("dashboard.index"))
        else:
            flash("ایمیل یا رمز عبور اشتباه است.", "error")
    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("از حساب کاربری خود خارج شدید.", "success")
    return redirect(url_for("tournament.index"))