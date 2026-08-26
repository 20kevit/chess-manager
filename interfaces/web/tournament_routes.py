"""
Tournament HTTP handlers.
No business logic here.
"""
from flask import (Blueprint, render_template, request, session, abort,
                   url_for, flash, redirect, current_app, send_file)
from flask_login import current_user
from infrastructure.repositories import TournamentRepository, ParticipantRepository, PairingRepository
from application.tournament_service import TournamentService
from app.extensions import db
from interfaces.web.helpers import build_cell as _build_cell
from interfaces.web.admin_auth import (
    require_admin, require_tournament_manager, require_result_editor,
)
from domain.tiebreak.calculators import ALL_TIEBREAKS_DISPLAY
from interfaces.web.decorators import role_required
import json
import os
from domain.rulebook import (
    parse_sections, serialize_sections, SECTION_VOCABULARY,
)
from infrastructure.file_storage import (
    FileStorageError, save_pdf, remove_pdf, resolve_private_file,
    PDF_MIMETYPE,
)

tournament_bp = Blueprint("tournament", __name__)

def is_current_admin(tournament):
    """
    Check if the current user may administer this specific tournament.
    Uses the account-based authorization model (system admin / organizer /
    accepted arbiter staff).
    """
    return require_admin(tournament.public_id) is not None

def _validate_public_id(public_id: str):
    if not public_id.isdigit() or len(public_id) != 8:
        abort(404)


@tournament_bp.route("/")
def index():
    from infrastructure.db_models import TournamentModel
    recent = TournamentModel.query.filter(
        TournamentModel.status != "setup"
    ).order_by(
        TournamentModel.updated_at.desc()
    ).limit(10).all()

    stats = TournamentRepository.get_global_stats()

    return render_template("index.html", recent_tournaments=recent, stats=stats)


@tournament_bp.route("/create", methods=["GET", "POST"])
@role_required('organizer')
def create():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            if not name:
                flash("نام تورنومنت الزامی است", "error")
                return render_template("tournament/create.html")

            total_rounds = request.form.get("total_rounds", 5, type=int)
            if not (1 <= total_rounds <= 30):
                flash("تعداد دورها باید بین ۱ تا ۳۰ باشد", "error")
                return render_template("tournament/create.html")

            tournament = TournamentService.create(request.form)

            public_url = url_for(
                "tournament.view",
                public_id=tournament.public_id,
                _external=True
            )
            return render_template(
                "tournament/created.html",
                tournament=tournament,
                public_url=public_url,
            )
        except Exception as e:
            # در صورت بروز خطا
            flash(f"خطا در ایجاد تورنمنت: {str(e)}", "error")
            return render_template("tournament/create.html")
            
    return render_template("tournament/create.html")


@tournament_bp.route("/<public_id>")
def view(public_id):
    """Unified view: automatically detects admin status from session."""
    if not public_id.isdigit(): abort(404)
    
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament: abort(404)

    # P1-B capability flags (server-computed; UI is cosmetic only).
    can_manage = False
    can_edit_results = False
    if current_user.is_authenticated:
        can_edit_results = require_result_editor(public_id) is not None
        can_manage = require_tournament_manager(public_id) is not None

    standings = TournamentService.get_standings(tournament)
    return render_template(
        "tournament/view.html",
        tournament=tournament,
        # Backward-compatible flag now means the manager tier.
        is_admin=can_manage,
        can_manage=can_manage,
        can_edit_results=can_edit_results,
        rulebook_sections=parse_sections(tournament.rulebook_sections),
        **standings
    )

@tournament_bp.route("/<public_id>/player/<int:participant_id>")
def player_detail(public_id, participant_id):
    """نمایش جزئیات بازی‌های یک بازیکن"""
    _validate_public_id(public_id)

    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    # Use ParticipantRepository instead of PlayerRepository
    participant = ParticipantRepository.get_by_id(participant_id, tournament.id)
    if not participant:
        abort(404)

    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    all_participants = {p.id: p for p in ParticipantRepository.get_all(tournament.id)}
    
    from infrastructure.db_models import RoundModel
    rounds = {r.id: r for r in RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).all()}

    # ساخت لیست بازی‌ها
    games = []
    for pairing in all_pairings:
        round_obj = rounds.get(pairing.round_id)
        if not round_obj:
            continue

        # Check white_participant_id
        if pairing.white_participant_id == participant_id:
            opponent = all_participants.get(pairing.black_participant_id)
            games.append({
                "round": round_obj.round_number,
                "color": "سفید",
                "color_code": "white",
                "opponent": opponent,
                "opponent_rating": opponent.rating_snapshot if opponent else 0,
                "result": pairing.result,
                "score": _get_score(pairing.result, "white"),
                "board": pairing.board_number,
            })
        # Check black_participant_id
        elif pairing.black_participant_id == participant_id:
            opponent = all_participants.get(pairing.white_participant_id)
            games.append({
                "round": round_obj.round_number,
                "color": "سیاه",
                "color_code": "black",
                "opponent": opponent,
                "opponent_rating": opponent.rating_snapshot if opponent else 0,
                "result": pairing.result,
                "score": _get_score(pairing.result, "black"),
                "board": pairing.board_number,
            })

    games.sort(key=lambda g: g["round"])

    # محاسبه آمار
    total_score = sum(g["score"] for g in games if g["score"] is not None)

    # فقط بازی‌های واقعی
    played_games = [
        g for g in games
        if g["result"] in ["1-0", "0-1", "1/2", "+/-", "-/+", "+/+"]
    ]

    wins = len([g for g in played_games if g["score"] == 1.0])
    draws = len([g for g in played_games if g["result"] == "1/2"])
    losses = len([g for g in played_games if g["score"] == 0.0])

    # Bye ها جداگانه
    full_byes = len([g for g in games if g["result"] == "bye"])
    half_byes = len([g for g in games if g["result"] == "half-bye"])
    zero_byes = len([g for g in games if g["result"] == "zero-bye"])

    total_games = len(played_games)

    # محاسبه تغییر ریتینگ
    standings = TournamentService.get_standings(tournament)
    rc = standings["rating_changes"].get(participant_id, {})

    return render_template(
        "tournament/player_detail.html",
        tournament=tournament,
        player=participant,  # Pass participant as 'player' to template
        games=games,
        total_score=total_score,
        total_games=total_games,
        wins=wins,
        draws=draws,
        losses=losses,
        full_byes=full_byes,
        half_byes=half_byes,
        zero_byes=zero_byes,
        rating_change=rc,
    )


def _get_score(result, color):
    scores = {
        "1-0": {"white": 1.0, "black": 0.0},
        "0-1": {"white": 0.0, "black": 1.0},
        "1/2": {"white": 0.5, "black": 0.5},
        "+/-": {"white": 1.0, "black": 0.0},
        "-/+": {"white": 0.0, "black": 1.0},
        "+/+": {"white": 0.0, "black": 0.0},
        "bye": {"white": 1.0, "black": None},
        "half-bye": {"white": 0.5, "black": None},
        "zero-bye": {"white": 0.0, "black": None},
    }
    if result in scores:
        return scores[result].get(color)
    return None

@tournament_bp.route("/<public_id>/crosstable")
def crosstable(public_id):
    """Cross-Table view"""
    _validate_public_id(public_id)

    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    participants = ParticipantRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)

    from infrastructure.db_models import RoundModel
    rounds = RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).order_by(RoundModel.round_number).all()

    round_map = {r.id: r.round_number for r in rounds}
    participants_map = {p.id: p for p in participants}
    total_rounds = tournament.current_round or 0

    # ساخت cross-table data
    cross_data = {}
    for p in participants:
        cross_data[p.id] = {
            "player": p,
            "rounds": {},
        }

    for pairing in all_pairings:
        round_num = round_map.get(pairing.round_id)
        if not round_num:
            continue

        w_id = pairing.white_participant_id
        b_id = pairing.black_participant_id
        result = pairing.result

        if w_id and w_id in cross_data:
            cross_data[w_id]["rounds"][round_num] = _build_cell(
                result, "white", b_id, participants_map
            )

        if b_id and b_id in cross_data:
            cross_data[b_id]["rounds"][round_num] = _build_cell(
                result, "black", w_id, participants_map
            )

    sorted_players = sorted(
        cross_data.values(),
        key=lambda x: (-(x["player"].points or 0), -(x["player"].rating_snapshot or 0))
    )

    return render_template(
        "tournament/crosstable.html",
        tournament=tournament,
        sorted_players=sorted_players,
        total_rounds=total_rounds,
    )


@tournament_bp.route("/<public_id>/summary")
def summary(public_id):
    """صفحه خلاصه و آمار تورنومنت"""
    _validate_public_id(public_id)

    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    participants = ParticipantRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    participants_map = {p.id: p for p in participants}

    standings = TournamentService.get_standings(tournament)

    # --- آمار کلی ---
    real_results = ["1-0", "0-1", "1/2", "+/-", "-/+", "+/+"]
    real_games = [p for p in all_pairings if p.result in real_results]

    white_wins = len([p for p in real_games if p.result == "1-0"])
    black_wins = len([p for p in real_games if p.result == "0-1"])
    draws = len([p for p in real_games if p.result == "1/2"])
    forfeits = len([p for p in real_games if p.result in ["+/-", "-/+", "+/+"]])

    total_real = len(real_games)
    white_pct = round(white_wins / total_real * 100, 1) if total_real else 0
    black_pct = round(black_wins / total_real * 100, 1) if total_real else 0
    draw_pct = round(draws / total_real * 100, 1) if total_real else 0

    top_players = standings["player_standings"][:3]

    # --- بهترین پرفورمنس ---
    rc = standings["rating_changes"]
    best_performance = None
    best_perf_value = 0
    for pid, data in rc.items():
        perf = data.get("performance")
        if perf and perf > best_perf_value:
            best_perf_value = perf
            best_performance = {
                "player": participants_map.get(pid),
                "performance": perf,
            }

    # --- بیشترین تغییر ریتینگ مثبت ---
    best_gain = None
    best_gain_value = -999
    for pid, data in rc.items():
        change = data.get("rating_change", 0)
        player = participants_map.get(pid)
        if player and (player.rating_snapshot or 0) > 0 and change > best_gain_value:
            best_gain_value = change
            best_gain = {
                "player": player,
                "change": change,
            }

    # --- بیشترین برد ---
    win_counts = {}
    for pairing in all_pairings:
        if pairing.result == "1-0" and pairing.white_participant_id:
            win_counts[pairing.white_participant_id] = win_counts.get(pairing.white_participant_id, 0) + 1
        elif pairing.result == "0-1" and pairing.black_participant_id:
            win_counts[pairing.black_participant_id] = win_counts.get(pairing.black_participant_id, 0) + 1

    most_wins = None
    if win_counts:
        max_pid = max(win_counts, key=win_counts.get)
        most_wins = {
            "player": participants_map.get(max_pid),
            "wins": win_counts[max_pid],
        }

    # --- آمار رده سنی ---
    age_stats = {}
    custom_stats = {}
    for ps in standings["player_standings"]:
        p = ps["player"]
        if p.age_category:
            age_stats.setdefault(p.age_category, [])
            age_stats[p.age_category].append(ps)
        if p.custom_category:
            custom_stats.setdefault(p.custom_category, [])
            custom_stats[p.custom_category].append(ps)

    age_winners = {}
    for cat, cat_players in age_stats.items():
        if cat_players:
            age_winners[cat] = cat_players[0]

    custom_winners = {}
    for cat, cat_players in custom_stats.items():
        if cat_players:
            custom_winners[cat] = cat_players[0]

    # --- میانگین ریتینگ ---
    rated_players = [p for p in participants if (p.rating_snapshot or 0) > 0]
    avg_rating = round(
        sum(p.rating_snapshot for p in rated_players) / len(rated_players)
    ) if rated_players else 0

    return render_template(
        "tournament/summary.html",
        tournament=tournament,
        total_players=len(participants),
        total_games=total_real,
        white_wins=white_wins,
        black_wins=black_wins,
        draws=draws,
        forfeits=forfeits,
        white_pct=white_pct,
        black_pct=black_pct,
        draw_pct=draw_pct,
        avg_rating=avg_rating,
        top_players=top_players,
        best_performance=best_performance,
        best_gain=best_gain,
        most_wins=most_wins,
        age_winners=age_winners,
        custom_winners=custom_winners,
    )

@tournament_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []

    if query:
        from infrastructure.db_models import TournamentModel
        results = TournamentModel.query.filter(
            TournamentModel.name.contains(query)
        ).order_by(
            TournamentModel.updated_at.desc()
        ).limit(20).all()

    return render_template("search.html", query=query, results=results)


@tournament_bp.route("/<public_id>/settings", methods=["GET", "POST"])
def settings(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            TournamentService.update_basic_settings(tournament, request.form)
            flash("تنظیمات با موفقیت ذخیره شد.", "success")
            return redirect(url_for("tournament.view", public_id=public_id))
        except Exception as e:
            flash(f"خطا در ذخیره تنظیمات: {str(e)}", "error")

    current_tiebreaks = json.loads(tournament.tiebreak_rules or "[]")

    return render_template(
        "tournament/settings.html",
        tournament=tournament,
        current_tiebreaks=current_tiebreaks,
        all_tiebreaks=ALL_TIEBREAKS_DISPLAY,
        is_admin=True
    )


# ── P1-D: Rulebook system ─────────────────────────────────────────────

_RULEBOOK_ERROR_MESSAGES = {
    "empty": "فایلی انتخاب نشده است.",
    "size": "حجم فایل PDF نباید بیشتر از ۵ مگابایت باشد.",
    "type": "فایل ارسالی یک PDF معتبر نیست.",
}


@tournament_bp.route("/<public_id>/settings/rulebook", methods=["GET", "POST"])
def rulebook_settings(public_id):
    """Manager-tier editor for the three independent rulebook forms."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            TournamentService.update_rulebook_settings(tournament, request.form)
            flash("آیین‌نامه با موفقیت ذخیره شد.", "success")
        except Exception as e:
            flash(f"خطا در ذخیره آیین‌نامه: {str(e)}", "error")
        return redirect(url_for("tournament.rulebook_settings",
                                public_id=public_id))

    return render_template(
        "tournament/rulebook_settings.html",
        tournament=tournament,
        sections=parse_sections(tournament.rulebook_sections),
        vocabulary=SECTION_VOCABULARY,
        is_admin=True,
    )


@tournament_bp.route("/<public_id>/settings/rulebook/pdf", methods=["POST"])
def upload_rulebook_pdf(public_id):
    """Upload/replace the public rulebook PDF (manager tier only)."""
    tournament = require_admin(public_id)
    if not tournament:
        abort(403)

    try:
        stored = save_pdf(
            request.files.get("rulebook_pdf"),
            current_app.config["RULEBOOK_UPLOAD_DIR"],
            f"rulebook_{tournament.id}",
        )
    except FileStorageError as exc:
        flash(_RULEBOOK_ERROR_MESSAGES.get(
            exc.reason, "آپلود فایل ناموفق بود."), "error")
        return redirect(url_for("tournament.rulebook_settings",
                                public_id=public_id))

    tournament.rulebook_pdf_path = stored
    db.session.commit()
    flash("فایل PDF آیین‌نامه با موفقیت بارگذاری شد.", "success")
    return redirect(url_for("tournament.rulebook_settings",
                            public_id=public_id))


@tournament_bp.route("/<public_id>/settings/rulebook/pdf/remove", methods=["POST"])
def remove_rulebook_pdf(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        abort(403)

    if tournament.rulebook_pdf_path:
        remove_pdf(current_app.config["RULEBOOK_UPLOAD_DIR"],
                   f"rulebook_{tournament.id}")
        tournament.rulebook_pdf_path = None
        db.session.commit()
    flash("فایل PDF آیین‌نامه حذف شد.", "success")
    return redirect(url_for("tournament.rulebook_settings",
                            public_id=public_id))


@tournament_bp.route("/uploads/rulebook/<public_id>")
def download_rulebook_pdf(public_id):
    """PUBLIC access to the configured rulebook PDF.

    Rulebooks are public tournament content: no login required. Storage
    stays instance-anchored (never under static/) and resolution is
    basename-only, so traversal is impossible."""
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament or not tournament.rulebook_pdf_path:
        abort(404)

    absolute_path = resolve_private_file(
        current_app.config["RULEBOOK_UPLOAD_DIR"],
        tournament.rulebook_pdf_path,
    )
    if not absolute_path:
        abort(404)

    return send_file(
        absolute_path,
        mimetype=PDF_MIMETYPE,
        download_name=f"rulebook_{public_id}.pdf",
    )

# ─────────────────────────────────────────────────────────────────────