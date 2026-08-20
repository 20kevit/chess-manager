# interfaces/web/player_profile_routes.py
from flask import Blueprint, render_template, abort, redirect, url_for
from application.player_profile_service import PlayerProfileService
from infrastructure.repositories import PlayerProfileRepository

player_profile_bp = Blueprint("player_profile", __name__)

@player_profile_bp.route("/player/<path:identifier>")
def public_profile(identifier):
    """
    Public profile page for a player.
    Uses fide_id for verified players, or numerical id for others.
    """
    profile = None
    
    # 1. اگر شناسه عددی باشد، بر اساس ID جستجو می‌کنیم
    if identifier.isdigit():
        profile = PlayerProfileRepository.get_by_id(int(identifier))
    else:
        # 2. اگر رشته‌ای باشد، بر اساس FIDE ID جستجو می‌کنیم
        profile = PlayerProfileRepository.get_by_fide_id(identifier)

    if not profile:
        abort(404)
        
    # اگر بازیکن FIDE ID دارد اما تأیید نشده است، اجازه نمایش عمومی با fide_id را نمی‌دهیم
    # برای امنیت بیشتر، فقط بازیکنان verified می‌توانند با fide_id پیدا شوند
    if not identifier.isdigit() and profile.fide_verification_status != "verified":
        abort(404)

    # جمع‌آوری داده‌های پروفایل
    profile_data = PlayerProfileService.get_profile_data(profile.id)
    if not profile_data:
        abort(404)

    # داده‌های تاریخچه و آمار (در فازهای 8C, 8D, 8F, 8E ساخته شدند)
    rating_history = PlayerProfileService.get_rating_history(profile.id)
    tournament_history = PlayerProfileService.get_tournament_history(profile.id)
    statistics = PlayerProfileService.get_statistics(profile.id)
    game_history = PlayerProfileService.get_game_history(profile.id)

    # حذف اطلاعات حساس قبل از ارسال به Template
    profile_data['profile'].national_id = None
    profile_data['profile'].bank_card_number = None
    profile_data['profile'].bank_account_name = None

    return render_template(
        "player/public_profile.html",
        profile_data=profile_data,
        rating_history=rating_history,
        tournament_history=tournament_history,
        statistics=statistics,
        game_history=game_history
    )