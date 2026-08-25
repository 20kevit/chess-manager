from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort, jsonify, current_app, send_file)
from flask_login import current_user, login_required
from application.auth_service import AuthService
from infrastructure.db_models import (
    PlayerProfileModel, TournamentModel, RegistrationModel,
    TournamentStaffModel, UserModel, TournamentParticipantModel
)
from datetime import datetime
import os
from app.extensions import db
from interfaces.web.admin_auth import require_admin
from application.verification_service import VerificationService
from application.fide_search_service import FideSearchService
from infrastructure.repositories import PlayerVerificationRepository
from infrastructure.file_storage import (
    FileStorageError, save_image, remove_image, resolve_private_file,
    IMAGE_MIMETYPES,
)
from application.registration_service import (
    BLOCKING_REGISTRATION_STATUSES, RegistrationService,
)
from domain.registration import (
    check_eligibility, parse_requirements, EligibilityProfile,
)

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
        
        # Phase 8 Fix: Fetch tournaments added directly by arbiter
        my_participations = TournamentParticipantModel.query.filter_by(
            player_profile_id=profile.id
        ).order_by(TournamentParticipantModel.id.desc()).all()
    else:
        my_participations = []

    # Fetch available tournaments for registration.
    # P0-D: hide tournaments where the player already holds an open/successful
    # registration or fails the configured entry requirements. This filter is
    # ONLY a UX optimization — RegistrationService re-enforces everything
    # server-side on direct POSTs.
    available_tournaments = []
    if is_player:
        blocked_tournament_ids = {
            reg.tournament_id
            for reg in RegistrationModel.query.filter(
                RegistrationModel.user_id == current_user.id,
                RegistrationModel.status.in_(BLOCKING_REGISTRATION_STATUSES),
            ).all()
        }

        eligibility_facts = (
            RegistrationService._map_profile_to_eligibility(profile)
            if profile is not None
            else EligibilityProfile()
        )

        candidates = TournamentModel.query.filter(
            TournamentModel.status != "finished",
            db.or_(
                TournamentModel.registration_deadline.is_(None),
                TournamentModel.registration_deadline >= datetime.utcnow()
            )
        ).order_by(TournamentModel.created_at.desc()).all()

        for tournament in candidates:
            if tournament.id in blocked_tournament_ids:
                continue
            requirements = parse_requirements(
                getattr(tournament, "registration_requirements", None)
            )
            if requirements.has_any:
                reference = (
                    tournament.start_date
                    if tournament.start_date else datetime.utcnow().date()
                )
                if check_eligibility(eligibility_facts, requirements, reference):
                    continue
            available_tournaments.append(tournament)
            if len(available_tournaments) >= 10:
                break

    return render_template(
        "dashboard/index.html", 
        profile=profile,
        user=current_user,
        is_organizer=is_organizer,
        is_player=is_player,
        my_tournaments=my_tournaments,
        pending_invitations=pending_invitations,
        assigned_tournaments=assigned_tournaments,
        my_registrations=my_registrations,
        available_tournaments=available_tournaments,
        search_results=None,
        my_participations=my_participations,
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
    
    # Fix: Fetch pending invitations and available tournaments to prevent template crash
    pending_invitations = TournamentStaffModel.query.filter_by(
        user_id=current_user.id, status="pending"
    ).all()
    
    available_tournaments = []
    if current_user.has_role('player'):
        available_tournaments = TournamentModel.query.filter(
            TournamentModel.status != "finished",
            db.or_(
                TournamentModel.registration_deadline.is_(None),
                TournamentModel.registration_deadline >= datetime.utcnow()
            )
        ).order_by(TournamentModel.created_at.desc()).limit(10).all()
    
    # Fix: Use player_profile_id for correct registration fetching
    profile_id = current_user.profile.id if current_user.profile else None
    my_registrations = []
    if profile_id:
        my_registrations = RegistrationModel.query.filter_by(
            player_profile_id=profile_id
        ).order_by(RegistrationModel.created_at.desc()).all()
    
    return render_template(
        "dashboard/index.html", 
        profile=current_user.profile, 
        user=current_user,
        search_results=search_results,
        is_organizer=current_user.has_role('organizer'),
        is_player=current_user.has_role('player'),
        my_tournaments=TournamentModel.query.filter_by(organizer_id=current_user.id).all(),
        pending_invitations=pending_invitations,
        assigned_tournaments=assigned_tournaments,
        my_registrations=my_registrations,
        available_tournaments=available_tournaments
    )

@dashboard_bp.route("/dashboard/profile/link/<int:profile_id>", methods=["POST"])
@login_required
def link_profile(profile_id):
    try:
        # Pass form data as verification dictionary
        verification_data = request.form.to_dict()
        AuthService.claim_profile(current_user.id, profile_id, verification_data)
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

    # Validate phone before mutating anything so an invalid value aborts
    # the whole update without partial changes.
    from domain.registration import normalize_phone, INVALID_PHONE_MESSAGE
    phone_raw = request.form.get("phone", "").strip()
    if phone_raw:
        normalized_phone = normalize_phone(phone_raw)
        if not normalized_phone:
            flash(INVALID_PHONE_MESSAGE, "error")
            return redirect(url_for("dashboard.index"))
        profile.phone = normalized_phone
    else:
        profile.phone = None

    profile.first_name = request.form.get("first_name", "").strip()
    profile.last_name = request.form.get("last_name", "").strip()
    profile.federation = request.form.get("federation", "IRI").strip() or "IRI"
    profile.fide_title = request.form.get("fide_title", "").strip()
    
    # New Fields: National ID and Bank Info
    profile.national_id = request.form.get("national_id", "").strip()
    profile.bank_card_number = request.form.get("bank_card_number", "").strip()
    profile.bank_account_name = request.form.get("bank_account_name", "").strip()
    
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


# --- Private Profile Media (P0-C) -------------------------------------
#
# Photos and ID documents are stored under instance-anchored private
# directories (never static/) and served exclusively through these
# authenticated endpoints. Stored values are bare filenames resolved with
# basename-only logic, so path traversal is impossible.

_MEDIA_ERROR_MESSAGES = {
    "empty": "فایلی انتخاب نشده است.",
    "size": "حجم فایل نباید بیشتر از ۵ مگابایت باشد.",
    "type": "فرمت تصویر مجاز نیست (فقط JPG و PNG).",
}


def _shared_tournaments(profile):
    """Tournaments where this player appears (registration or participation)."""
    tournament_ids = {r.tournament_id for r in profile.registrations}
    tournament_ids.update(
        p.tournament_id for p in TournamentParticipantModel.query.filter_by(
            player_profile_id=profile.id
        ).all()
    )
    if not tournament_ids:
        return []
    return TournamentModel.query.filter(
        TournamentModel.id.in_(tournament_ids)
    ).all()


def _may_view_photo(profile) -> bool:
    """Photo visibility: owner, system admin, or any tournament admin of a
    shared tournament (the current require_admin model; P1-B will introduce
    finer-grained arbiter roles)."""
    if current_user.is_admin:
        return True
    if profile.user_id == current_user.id:
        return True
    for tournament in _shared_tournaments(profile):
        if require_admin(tournament.public_id) is not None:
            return True
    return False


def _may_view_id_document(profile) -> bool:
    """ID-document visibility is stricter: owner, system admin, or the
    organizer of a shared tournament (identity-review need). Ordinary
    arbiters stay excluded until P1-B defines the chief-arbiter role and
    re-enables access explicitly."""
    if current_user.is_admin:
        return True
    if profile.user_id == current_user.id:
        return True
    for tournament in _shared_tournaments(profile):
        if tournament.organizer_id == current_user.id:
            return True
    return False


def _serve_profile_media(stored_value: str, config_key: str):
    absolute_path = resolve_private_file(
        current_app.config[config_key], stored_value
    )
    if not absolute_path:
        abort(404)
    ext = (absolute_path.rsplit(".", 1)[-1].lower()
           if "." in absolute_path else "")
    mimetype = IMAGE_MIMETYPES.get(ext, "application/octet-stream")
    return send_file(
        absolute_path,
        mimetype=mimetype,
        download_name=os.path.basename(absolute_path),
    )


@dashboard_bp.route("/dashboard/profile/photo/upload", methods=["POST"])
@login_required
def upload_profile_photo():
    profile = current_user.profile
    if not profile:
        flash("ابتدا باید پروفایل شطرنج خود را بسازید.", "error")
        return redirect(url_for("dashboard.index"))

    try:
        stored = save_image(
            request.files.get("photo"),
            current_app.config["PROFILE_PHOTO_UPLOAD_DIR"],
            f"profile_{profile.id}",
        )
    except FileStorageError as exc:
        flash(_MEDIA_ERROR_MESSAGES.get(exc.reason, "آپلود فایل ناموفق بود."), "error")
        return redirect(url_for("dashboard.index"))

    profile.photo_path = stored
    db.session.commit()
    flash("عکس پروفایل با موفقیت بروزرسانی شد.", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/dashboard/profile/photo/remove", methods=["POST"])
@login_required
def remove_profile_photo():
    profile = current_user.profile
    if not profile or not profile.photo_path:
        return redirect(url_for("dashboard.index"))

    remove_image(
        current_app.config["PROFILE_PHOTO_UPLOAD_DIR"],
        f"profile_{profile.id}",
    )
    profile.photo_path = None
    db.session.commit()
    flash("عکس پروفایل حذف شد.", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/uploads/profile-photo/<int:profile_id>")
@login_required
def serve_profile_photo(profile_id):
    profile = db.session.get(PlayerProfileModel, profile_id)
    if not profile or not profile.photo_path:
        abort(404)
    if not _may_view_photo(profile):
        abort(403)
    return _serve_profile_media(profile.photo_path, "PROFILE_PHOTO_UPLOAD_DIR")


@dashboard_bp.route("/dashboard/profile/id-document/upload", methods=["POST"])
@login_required
def upload_id_document():
    profile = current_user.profile
    if not profile:
        flash("ابتدا باید پروفایل شطرنج خود را بسازید.", "error")
        return redirect(url_for("dashboard.index"))

    try:
        stored = save_image(
            request.files.get("id_document"),
            current_app.config["ID_DOCUMENT_UPLOAD_DIR"],
            f"id_document_{profile.id}",
        )
    except FileStorageError as exc:
        flash(_MEDIA_ERROR_MESSAGES.get(exc.reason, "آپلود فایل ناموفق بود."), "error")
        return redirect(url_for("dashboard.index"))

    profile.id_document_path = stored
    db.session.commit()
    flash("تصویر مدرک هویتی با موفقیت بارگذاری شد.", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/dashboard/profile/id-document/remove", methods=["POST"])
@login_required
def remove_id_document():
    profile = current_user.profile
    if not profile or not profile.id_document_path:
        return redirect(url_for("dashboard.index"))

    remove_image(
        current_app.config["ID_DOCUMENT_UPLOAD_DIR"],
        f"id_document_{profile.id}",
    )
    profile.id_document_path = None
    db.session.commit()
    flash("تصویر مدرک هویتی حذف شد.", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/uploads/id-document/<int:profile_id>")
@login_required
def serve_id_document(profile_id):
    profile = db.session.get(PlayerProfileModel, profile_id)
    if not profile or not profile.id_document_path:
        abort(404)
    if not _may_view_id_document(profile):
        abort(403)
    return _serve_profile_media(profile.id_document_path, "ID_DOCUMENT_UPLOAD_DIR")

# ----------------------------------------------------------------------

# --- Live Search API for Arbiters ---
@dashboard_bp.route("/dashboard/api/search-users")
@login_required
def search_users():
    """AJAX endpoint for tournament admins to search users by name or email.

    Restricted to the tournament-management context: the caller must pass the
    tournament public_id and be authorized to administer it. Prevents
    platform-wide user/email enumeration by regular accounts.
    """
    public_id = request.args.get("public_id", "")
    if not public_id or require_admin(public_id) is None:
        return jsonify({"success": False, "error": "دسترسی غیرمجاز"}), 403

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
    
    # ── Phase 9C: Notify User about Arbiter Invitation ──
    try:
        from application.notification_service import NotificationService
        from application.notification_types import NotificationType
        NotificationService.create_notification(
            user_id=user.id,
            type=NotificationType.ARBITER_INVITATION,
            title="دعوت‌نامه داوری",
            message=f"شما برای داوری مسابقه '{tournament.name}' دعوت شده‌اید.",
            link_url=url_for("dashboard.index", _external=False)
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to send arbiter invitation notification: {str(e)}")
    # ──────────────────────────────────────────
    
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

# ── Player FIDE Verification ──

@dashboard_bp.route("/dashboard/verification/request", methods=["GET", "POST"])
@login_required
def request_verification():
    """Player requests FIDE verification."""
    profile = current_user.profile
    if not profile:
        flash("ابتدا پروفایل خود را تکمیل کنید.", "error")
        return redirect(url_for("dashboard.create_profile"))

    if request.method == "POST":
        fide_id = request.form.get("fide_id", "").strip()
        if not fide_id:
            flash("کد فیده الزامی است.", "error")
            return redirect(request.url)
            
        try:
            VerificationService.submit_request(profile.id, fide_id)
            flash("درخواست شما با موفقیت ثبت شد و در انتظار بررسی مدیر است.", "success")
            return redirect(url_for("dashboard.index"))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(request.url)

    # GET request: show form and current status
    # If they have a pending request, pass it to template
    pending_req = PlayerVerificationRepository.get_pending_for_profile(profile.id) if hasattr(PlayerVerificationRepository, 'get_pending_for_profile') else None
    
    return render_template(
        "dashboard/verification_request.html",
        profile=profile,
        pending_req=pending_req
    )

@dashboard_bp.route("/dashboard/api/fide-search")
@login_required
def dashboard_fide_search():
    """AJAX endpoint for players to search their FIDE ID."""
    query = request.args.get("q", "")
    if len(query) < 3:
        return jsonify([])
    
    # Players can only search within their own federation by default, 
    # but let's allow searching all for now, or restrict to IRI if needed.
    results = FideSearchService.search(query, federation=None, limit=10)
    return jsonify(results)

@dashboard_bp.route("/dashboard/participant/<int:participant_id>/withdraw", methods=["POST"])
@login_required
def withdraw_from_participation(participant_id):
    """Allows a player to withdraw from a tournament they were directly added to."""
    participant = TournamentParticipantModel.query.get_or_404(participant_id)
    
    # Security Check: Ensure this participant belongs to the current user
    if not current_user.profile or participant.player_profile_id != current_user.profile.id:
        abort(403)
        
    from application.player_service import PlayerService
    PlayerService.toggle_withdraw(participant, participant.tournament.current_round)
    
    flash("انصراف شما از مسابقه با موفقیت ثبت شد.", "info")
    return redirect(url_for("dashboard.index"))

# --- Notification Preferences ---
@dashboard_bp.route("/dashboard/notifications/settings", methods=["GET", "POST"])
@login_required
def notification_settings():
    from application.notification_service import NotificationService
    from application.notification_types import NotificationType
    import json

    if request.method == "POST":
        prefs = {}
        for n_type in NotificationType:
            prefs[n_type.value] = {
                "web": request.form.get(f"web_{n_type.value}") == "on",
                "telegram": request.form.get(f"telegram_{n_type.value}") == "on",
                "bale": request.form.get(f"bale_{n_type.value}") == "on",
            }

        NotificationService.update_preferences(current_user.id, prefs)
        flash("تنظیمات اعلان‌ها با موفقیت ذخیره شد.", "success")
        return redirect(url_for("dashboard.notification_settings"))

    pref_model = NotificationService.get_preferences(current_user.id)
    current_prefs = json.loads(pref_model.preferences_json or "{}")
    
    # Prepare data for template
    notif_types = []
    for n_type in NotificationType:
        settings = current_prefs.get(n_type.value, {})
        notif_types.append({
            "value": n_type.value,
            "name": n_type.value.replace("_", " ").title(),
            "web_enabled": settings.get("web", True),
            "telegram_enabled": settings.get("telegram", True), # Default to True
            "bale_enabled": settings.get("bale", True),
        })

    return render_template(
        "dashboard/notification_settings.html",
        notif_types=notif_types,
        telegram_connected=True if current_user.telegram_chat_id else False,
        bale_connected=True if current_user.bale_chat_id else False
    )