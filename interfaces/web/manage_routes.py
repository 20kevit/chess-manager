# interfaces/web/manage_routes.py
"""
Tournament Management Workspace.

A dedicated, authenticated product context for operating ONE tournament —
strictly separate from the public tournament pages (which stay structurally
identical for every visitor).

One workspace for every role: the visible/enabled functionality is driven
by the existing two-tier capability model in `admin_auth`:

- manager tier (system admin | organizer | accepted chief_arbiter)
- result-editor tier (manager tier + accepted arbiter)

Entries the current user may not use are rendered DISABLED in the sidebar
(structure stays visible); every mutation stays behind the server-side
`deny_or_login` gates. Disabled UI is cosmetic only — never authorization.
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort,
)

from app.extensions import db
from application.round.display_service import RoundDisplayService
from application.tournament.standings_service import StandingsService
from interfaces.web.admin_auth import (
    capabilities, deny_or_login, require_tournament_manager,
)

from infrastructure.models.staff import TournamentStaffModel
from infrastructure.models.tournament import ByeRequestModel, ManualPairingModel
from infrastructure.models.user import UserModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.registration import RegistrationRepository
from infrastructure.repositories.tournament import (
    PairingRepository, RoundRepository, TournamentRepository,
)

manage_bp = Blueprint("manage", __name__)

# Registrations that still need a staff decision.
ACTIONABLE_REGISTRATION_STATUSES = ("pending", "payment_pending", "receipt_submitted")

# Pairing results that count as "decided" on an operational board.
_DECIDED_RESULTS = ("1-0", "0-1", "1/2", "+/-", "-/+", "+/+")


def _workspace_context(public_id):
    """Shared (tournament, can_manage, can_edit_results) for workspace pages."""
    tournament, can_manage, can_edit_results = capabilities(public_id)
    if not tournament:
        abort(404)
    return tournament, can_manage, can_edit_results


def _require_workspace(public_id, tier="editor"):
    """Gate a workspace page: anonymous -> login, denied -> 403."""
    denied = deny_or_login(public_id, tier=tier)
    if denied:
        return None, denied
    tournament, can_manage, can_edit_results = _workspace_context(public_id)
    return {
        "tournament": tournament,
        "can_manage": can_manage,
        "can_edit_results": can_edit_results,
        "mn_can_manage": can_manage,
        "mn_can_edit_results": can_edit_results,
    }, None


def _round_stats(round_obj):
    """Operational counts for one round: boards, decided, pending."""
    pairings = PairingRepository.get_all_for_round(round_obj.id)
    boards = [p for p in pairings if p.black_participant_id]
    decided = [p for p in boards if (p.result or "") in _DECIDED_RESULTS]
    return {
        "total": len(boards),
        "decided": len(decided),
        "pending": len(boards) - len(decided),
        "byes": len(pairings) - len(boards),
    }


@manage_bp.route("/<public_id>/manage")
def overview(public_id):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    tournament = ctx["tournament"]

    rounds = RoundRepository.get_all(tournament.id)
    rounds_sorted = sorted(rounds, key=lambda r: r.round_number)
    ongoing = next((r for r in rounds_sorted if r.status == "ongoing"), None)
    last_finished = next(
        (r for r in reversed(rounds_sorted) if r.status == "finished"), None
    )
    ongoing_stats = _round_stats(ongoing) if ongoing else None

    players = ParticipantRepository.get_all(tournament.id)
    active_players = [p for p in players if p.status == "active"]

    pending_registrations = None
    if ctx["can_manage"]:
        regs = RegistrationRepository.get_for_tournament(tournament.id)
        pending_registrations = [
            r for r in regs if r.status in ACTIONABLE_REGISTRATION_STATUSES
        ]

    next_round_no = tournament.current_round + 1
    bye_requests = ByeRequestModel.query.filter_by(
        tournament_id=tournament.id, for_round=next_round_no
    ).all()
    manual_locks = ManualPairingModel.query.filter_by(
        tournament_id=tournament.id, round_number=next_round_no
    ).all()

    last_round = rounds_sorted[-1] if rounds_sorted else None
    can_create_next = (
        ctx["can_manage"]
        and (last_round is None or last_round.status == "finished")
        and tournament.current_round < tournament.total_rounds
    )
    create_blocked_reason = ""
    if not ctx["can_manage"]:
        create_blocked_reason = "ایجاد دور نیازمند دسترسی مدیریتی است."
    elif tournament.current_round >= tournament.total_rounds and rounds_sorted:
        create_blocked_reason = "همه دورها ایجاد شده‌اند."
    elif last_round is not None and last_round.status != "finished":
        create_blocked_reason = (
            f"ابتدا دور {last_round.round_number} را به پایان برسانید."
        )

    attention = []
    if ongoing_stats and ongoing_stats["pending"]:
        attention.append({
            "kind": "warning",
            "text": f"دور {ongoing.round_number} در جریان است و "
                    f"{ongoing_stats['pending']} نتیجه ثبت نشده دارد.",
            "url": url_for("manage.round_detail", public_id=public_id,
                            round_number=ongoing.round_number),
            "action": "ثبت نتایج",
        })
    if pending_registrations:
        attention.append({
            "kind": "warning",
            "text": f"{len(pending_registrations)} درخواست ثبت‌نام در انتظار بررسی است.",
            "url": url_for("registration.manage_registrations", public_id=public_id),
            "action": "بررسی درخواست‌ها",
        })
    if bye_requests and ctx["can_manage"]:
        attention.append({
            "kind": "info",
            "text": f"{len(bye_requests)} درخواست استراحت برای دور {next_round_no} ثبت شده است.",
            "url": url_for("round.request_bye", public_id=public_id),
            "action": "مدیریت استراحت‌ها",
        })
    if not players:
        attention.append({
            "kind": "info",
            "text": "هنوز بازیکنی به تورنومنت اضافه نشده است.",
            "url": url_for("manage.players", public_id=public_id),
            "action": "مدیریت بازیکنان",
        })
    elif not rounds_sorted:
        attention.append({
            "kind": "info",
            "text": "هنوز دوری ایجاد نشده است. برای شروع، دور ۱ را ایجاد کنید.",
            "url": url_for("manage.rounds", public_id=public_id),
            "action": "مدیریت دورها",
        })
    if tournament.status == "finished":
        attention.append({
            "kind": "success",
            "text": "تورنومنت به پایان رسیده است.",
            "url": None,
            "action": "",
        })

    return render_template(
        "manage/overview.html",
        rounds=rounds_sorted,
        ongoing_round=ongoing,
        ongoing_stats=ongoing_stats,
        last_finished=last_finished,
        total_players=len(players),
        active_players=len(active_players),
        pending_registrations=pending_registrations,
        bye_requests=bye_requests,
        manual_locks=manual_locks,
        next_round_no=next_round_no,
        can_create_next=can_create_next,
        create_blocked_reason=create_blocked_reason,
        attention=attention,
        mn_active="overview",
        **ctx,
    )


@manage_bp.route("/<public_id>/manage/players")
def players(public_id):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    return render_template(
        "manage/players.html",
        players=ParticipantRepository.get_all(ctx["tournament"].id),
        mn_active="players",
        **ctx,
    )


@manage_bp.route("/<public_id>/manage/rounds")
def rounds(public_id):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    tournament = ctx["tournament"]
    rounds = sorted(
        RoundRepository.get_all(tournament.id), key=lambda r: r.round_number
    )
    stats = {r.id: _round_stats(r) for r in rounds}
    last_round = rounds[-1] if rounds else None
    can_create_next = (
        ctx["can_manage"]
        and (last_round is None or last_round.status == "finished")
        and tournament.current_round < tournament.total_rounds
    )
    return render_template(
        "manage/rounds.html",
        rounds=rounds,
        round_stats=stats,
        can_create_next=can_create_next,
        mn_active="rounds",
        **ctx,
    )


@manage_bp.route("/<public_id>/manage/rounds/<int:round_number>")
def round_detail(public_id, round_number):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    tournament = ctx["tournament"]
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)
    pairings = PairingRepository.get_all_for_round(round_obj.id)
    participants = {
        p.id: p for p in ParticipantRepository.get_all(tournament.id)
    }
    stats = _round_stats(round_obj)
    return render_template(
        "manage/round_detail.html",
        round=round_obj,
        pairings=pairings,
        players=participants,
        round_stats=stats,
        mn_active="rounds",
        **ctx,
    )


@manage_bp.route("/<public_id>/manage/standings")
def standings(public_id):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    computed = StandingsService.get_standings(ctx["tournament"])
    return render_template(
        "manage/standings.html",
        mn_active="standings",
        **ctx,
        **computed,
    )


@manage_bp.route("/<public_id>/manage/crosstable")
def crosstable(public_id):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    tournament = ctx["tournament"]
    participants = ParticipantRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)

    from infrastructure.models.tournament import RoundModel
    rounds = RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).order_by(RoundModel.round_number).all()

    round_map = {r.id: r.round_number for r in rounds}
    participants_map = {p.id: p for p in participants}
    total_rounds = tournament.current_round or 0

    cross_data = {p.id: {"player": p, "rounds": {}} for p in participants}
    for pairing in all_pairings:
        round_num = round_map.get(pairing.round_id)
        if not round_num:
            continue
        w_id, b_id, result = (pairing.white_participant_id,
                              pairing.black_participant_id, pairing.result)
        if w_id and w_id in cross_data:
            cross_data[w_id]["rounds"][round_num] = \
                RoundDisplayService.build_crosstable_cell(
                    result, "white", b_id, participants_map)
        if b_id and b_id in cross_data:
            cross_data[b_id]["rounds"][round_num] = \
                RoundDisplayService.build_crosstable_cell(
                    result, "black", w_id, participants_map)

    sorted_players = sorted(
        cross_data.values(),
        key=lambda x: (-(x["player"].points or 0),
                       -(x["player"].rating_snapshot or 0)),
    )
    return render_template(
        "manage/crosstable.html",
        sorted_players=sorted_players,
        total_rounds=total_rounds,
        mn_active="crosstable",
        **ctx,
    )


@manage_bp.route("/<public_id>/manage/tiebreaks")
def tiebreaks(public_id):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    computed = StandingsService.get_standings(ctx["tournament"])
    return render_template(
        "manage/tiebreaks.html",
        mn_active="tiebreaks",
        **ctx,
        **computed,
    )


@manage_bp.route("/<public_id>/manage/output")
def output(public_id):
    ctx, denied = _require_workspace(public_id, tier="editor")
    if denied:
        return denied
    rounds = sorted(
        RoundRepository.get_all(ctx["tournament"].id),
        key=lambda r: r.round_number,
    )
    return render_template(
        "manage/output.html",
        rounds=rounds,
        mn_active="output",
        **ctx,
    )


@manage_bp.route("/<public_id>/manage/staff")
def staff(public_id):
    ctx, denied = _require_workspace(public_id, tier="manager")
    if denied:
        return denied
    tournament = ctx["tournament"]
    staff_members = TournamentStaffModel.query.filter_by(
        tournament_id=tournament.id).all()
    return render_template(
        "manage/staff.html",
        staff_members=staff_members,
        can_appoint_chief=_can_appoint_chief(tournament),
        mn_active="staff",
        **ctx,
    )


def _can_appoint_chief(tournament):
    """Only the organizer or a system admin may appoint a chief arbiter."""
    from flask_login import current_user
    if not current_user.is_authenticated:
        return False
    return bool(current_user.is_admin
                or tournament.organizer_id == current_user.id)


@manage_bp.route("/<public_id>/manage/staff/add", methods=["POST"])
def staff_add(public_id):
    denied = deny_or_login(public_id, tier="manager")
    if denied:
        return denied
    tournament = require_tournament_manager(public_id)
    if not tournament:
        abort(403)

    from flask_login import current_user
    user_id = request.form.get("user_id", type=int)
    user = db.session.get(UserModel, user_id) if user_id else None
    if not user:
        flash("کاربر یافت نشد.", "error")
        return redirect(url_for("manage.staff", public_id=public_id))
    if tournament.organizer_id == user.id:
        flash("برگزارکننده نمی‌تواند به عنوان داور اضافه شود.", "error")
        return redirect(url_for("manage.staff", public_id=public_id))

    from flask_login import current_user
    requested_role = request.form.get("staff_role", "arbiter")
    if requested_role == "chief_arbiter":
        if not _can_appoint_chief(tournament):
            flash("تنها برگزارکننده یا مدیر سیستم می‌تواند سرداور تعیین کند.",
                  "error")
            return redirect(url_for("manage.staff", public_id=public_id))
        existing_chief = TournamentStaffModel.query.filter_by(
            tournament_id=tournament.id, role="chief_arbiter",
            status="accepted").first()
        if existing_chief:
            flash("این تورنمنت قبلاً یک سرداور دارد. ابتدا سرداور فعلی را حذف کنید.",
                  "error")
            return redirect(url_for("manage.staff", public_id=public_id))
        role = "chief_arbiter"
    else:
        role = "arbiter"

    existing = TournamentStaffModel.query.filter_by(
        tournament_id=tournament.id, user_id=user.id).first()
    if existing:
        flash("این کاربر قبلاً در کادر این تورنومنت است.", "info")
        return redirect(url_for("manage.staff", public_id=public_id))

    db.session.add(TournamentStaffModel(
        tournament_id=tournament.id, user_id=user.id, role=role,
        status="pending", invited_by=current_user.id))
    db.session.commit()
    try:
        from application.notification_service import NotificationService
        from application.notification_types import NotificationType
        NotificationService.create_notification(
            user_id=user.id,
            type=NotificationType.ARBITER_INVITATION,
            title="دعوت‌نامه داوری",
            message=f"شما برای داوری مسابقه '{tournament.name}' دعوت شده‌اید.",
            link_url=url_for("dashboard.index", _external=False))
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Staff invitation notification failed")
    flash(f"دعوت‌نامه با موفقیت برای {user.email} ارسال شد.", "success")
    return redirect(url_for("manage.staff", public_id=public_id))


@manage_bp.route("/<public_id>/manage/staff/remove/<int:user_id>",
                 methods=["POST"])
def staff_remove(public_id, user_id):
    denied = deny_or_login(public_id, tier="manager")
    if denied:
        return denied
    tournament = require_tournament_manager(public_id)
    if not tournament:
        abort(403)

    staff = TournamentStaffModel.query.filter_by(
        tournament_id=tournament.id, user_id=user_id).first()
    if staff and staff.role == "chief_arbiter" \
            and not _can_appoint_chief(tournament):
        flash("حذف سرداور تنها توسط برگزارکننده یا مدیر سیستم ممکن است.",
              "error")
        return redirect(url_for("manage.staff", public_id=public_id))
    if staff:
        db.session.delete(staff)
        db.session.commit()
        flash("عضو کادر حذف شد.", "success")
    else:
        flash("عضو کادر یافت نشد.", "error")
    return redirect(url_for("manage.staff", public_id=public_id))


# Re-export for tests that probe the workspace gate surface.
__all__ = ["manage_bp", "ACTIONABLE_REGISTRATION_STATUSES"]
