from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import current_user, login_required
from application.auth_service import AuthService
from infrastructure.db_models import (
    PlayerProfileModel, TournamentModel, RegistrationModel, 
    TournamentStaffModel, UserModel
)
from datetime import datetime
from app.extensions import db
from interfaces.web.admin_auth import require_admin

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def index():
    profile = current_user.profile
    is_organizer = current_user.has_role('organizer')
    is_player = current_user.has_role('player')
    
    my_tournaments = []
    my_registrations = []
    
    if is_organizer:
        my_tournaments = TournamentModel.query.filter_by(
            organizer_id=current_user.id
        ).order_by(TournamentModel.created_at.desc()).all()

    # Fetch pending invitations for this user
    pending_invitations = TournamentStaffModel.query.filter_by(
        user_id=current_user.id, status="pending"
    ).all()
    
    # Fetch accepted assignments
    accepted_assignments = TournamentStaffModel.query.filter_by(
        user_id=current_user.id, status="accepted"
    ).all()
    assigned_tournaments = [a.tournament for a in accepted_assignments]
        
    if is_player and profile:
        my_registrations = RegistrationModel.query.filter_by(
            player_profile_id=profile.id
        ).order_by(RegistrationModel.created_at.desc()).all()

    return render_template(
        "dashboard/index.html", 
        profile=profile,
        user=current_user,
        is_organizer=is_organizer,
        is_player=is_player,
        my_tournaments=my_tournaments,
        pending_invitations=pending_invitations,
        assigned_tournaments=assigned_tournaments,
        my_registrations=my_registrations
    )

@dashboard_bp.route("/dashboard/tournament/<public_id>/manage")
@login_required
def manage_tournament(public_id):
    """صفحه hub مدیریت تورنمنت در داشبورد"""
    tournament = require_admin(public_id)
    if not tournament:
        flash("دسترسی غیرمجاز است.", "error")
        return redirect(url_for("dashboard.index"))
    
    staff_members = TournamentStaffModel.query.filter_by(tournament_id=tournament.id).all()
    
    return render_template(
        "dashboard/manage_tournament.html", 
        tournament=tournament,
        staff_members=staff_members
    )

@dashboard_bp.route("/dashboard/profile/search", methods=["POST"])
@login_required
def search_profile():
    fide_id = request.form.get("fide_id", "").strip()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    
    query = PlayerProfileModel.query.filter_by(user_id=None)
    
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
    
    assignments = TournamentStaffModel.query.filter_by(user_id=current_user.id).all()
    assigned_tournaments = [a.tournament for a in assignments]
    
    return render_template(
        "dashboard/index.html", 
        profile=current_user.profile, 
        user=current_user,
        search_results=search_results,
        is_organizer=current_user.has_role('organizer'),
        is_player=current_user.has_role('player'),
        my_tournaments=TournamentModel.query.filter_by(organizer_id=current_user.id).all(),
        assigned_tournaments=assigned_tournaments,
        my_registrations=RegistrationModel.query.filter_by(user_id=current_user.id).all()
    )

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

@dashboard_bp.route("/dashboard/profile/update", methods=["POST"])
@login_required
def update_profile():
    if not current_user.profile:
        flash("شما پروفایلی برای ویرایش ندارید.", "error")
        return redirect(url_for("dashboard.index"))
        
    profile = current_user.profile
    profile.first_name = request.form.get("first_name", "").strip()
    profile.last_name = request.form.get("last_name", "").strip()
    profile.federation = request.form.get("federation", "IRI").strip() or "IRI"
    profile.fide_title = request.form.get("fide_title", "").strip()
    
    birth_str = request.form.get("birth_date", "").strip()
    if birth_str:
        try:
            profile.birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
        except ValueError:
            flash("فرمت تاریخ تولد اشتباه است.", "error")
    else:
        profile.birth_date = None
        
    db.session.commit()
    flash("پروفایل با موفقیت بروزرسانی شد.", "success")
    return redirect(url_for("dashboard.index"))

# --- Live Search API for Arbiters ---
@dashboard_bp.route("/dashboard/api/search-users")
@login_required
def search_users():
    """AJAX endpoint to search for users by name or email"""
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify([])
        
    # Use outerjoin to include users who don't have a profile yet
    users = db.session.query(UserModel).outerjoin(
        PlayerProfileModel, UserModel.id == PlayerProfileModel.user_id
    ).filter(
        db.or_(
            UserModel.email.ilike(f"%{query}%"),
            PlayerProfileModel.first_name.ilike(f"%{query}%"),
            PlayerProfileModel.last_name.ilike(f"%{query}%")
        )
    ).limit(10).all()
    
    results = []
    for u in users:
        # Skip if user is the current user
        if u.id == current_user.id:
            continue
            
        full_name = f"{u.profile.first_name} {u.profile.last_name}" if u.profile else "بدون پروفایل (فقط ایمیل)"
        results.append({
            "id": u.id,
            "email": u.email,
            "name": full_name,
            "is_arbiter": u.has_role('arbiter')
        })
        
    return jsonify(results)


# --- Arbiter Invitation Management ---
@dashboard_bp.route("/dashboard/tournament/<public_id>/manage/staff/add", methods=["POST"])
@login_required
def add_staff(public_id):
    """Send invitation to a user to become tournament staff"""
    tournament = require_admin(public_id)
    if not tournament:
        abort(403)
        
    user_id = request.form.get("user_id", type=int)
    if not user_id:
        flash("کاربر نامعتبر است.", "error")
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))
        
    user = UserModel.query.get(user_id)
    if not user:
        flash("کاربر یافت نشد.", "error")
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))
        
    if tournament.organizer_id == user.id:
        flash("برگزارکننده نمی‌تواند به عنوان داور اضافه شود.", "error")
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))
        
    existing = TournamentStaffModel.query.filter_by(
        tournament_id=tournament.id, user_id=user.id
    ).first()
    
    if existing:
        if existing.status == "pending":
            flash("دعوت‌نامه قبلاً برای این کاربر ارسال شده است.", "info")
        elif existing.status == "accepted":
            flash("این کاربر قبلاً داور این تورنمنت است.", "info")
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))
        
    new_staff = TournamentStaffModel(
        tournament_id=tournament.id, 
        user_id=user.id, 
        role="arbiter",
        status="pending",
        invited_by=current_user.id
    )
    db.session.add(new_staff)
    db.session.commit()
    flash(f"دعوت‌نامه با موفقیت برای {user.email} ارسال شد.", "success")
    return redirect(url_for("dashboard.manage_tournament", public_id=public_id))

@dashboard_bp.route("/dashboard/tournament/<public_id>/manage/staff/remove/<int:user_id>", methods=["POST"])
@login_required
def remove_staff(public_id, user_id):
    tournament = require_admin(public_id)
    if not tournament:
        abort(403)
        
    staff = TournamentStaffModel.query.filter_by(
        tournament_id=tournament.id, user_id=user_id
    ).first()
    
    if staff:
        db.session.delete(staff)
        db.session.commit()
        flash("داور حذف شد.", "success")
    else:
        flash("داور یافت نشد.", "error")
        
    return redirect(url_for("dashboard.manage_tournament", public_id=public_id))

# --- Arbiter Accept/Reject Invitations ---
@dashboard_bp.route("/dashboard/invitation/<int:staff_id>/accept", methods=["POST"])
@login_required
def accept_invitation(staff_id):
    staff = TournamentStaffModel.query.get_or_404(staff_id)
    if staff.user_id != current_user.id:
        abort(403)
        
    staff.status = "accepted"
    db.session.commit()
    flash("دعوت‌نامه تایید شد. اکنون می‌توانید تورنمنت را مدیریت کنید.", "success")
    return redirect(url_for("dashboard.index"))

@dashboard_bp.route("/dashboard/invitation/<int:staff_id>/reject", methods=["POST"])
@login_required
def reject_invitation(staff_id):
    staff = TournamentStaffModel.query.get_or_404(staff_id)
    if staff.user_id != current_user.id:
        abort(403)
        
    staff.status = "rejected"
    db.session.commit()
    flash("دعوت‌نامه رد شد.", "info")
    return redirect(url_for("dashboard.index"))