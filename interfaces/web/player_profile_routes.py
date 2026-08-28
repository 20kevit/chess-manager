# interfaces/web/player_profile_routes.py
from flask import Blueprint, render_template, abort, redirect, url_for
from application.player_profile_service import PlayerProfileService

from infrastructure.repositories.profile import PlayerProfileRepository
player_profile_bp = Blueprint("player_profile", __name__)

@player_profile_bp.route("/player/<path:identifier>")
def public_profile(identifier):
    """
    Public profile page for a player.
    Uses fide_id for verified players, or numerical id for others.
    """
    profile = None
    
    # 1. اول بگردیم ببینیم آیا این شناسه، کد فیده یک بازیکن است یا خیر
    # (برای پشتیبانی از کدهای فیده که کاملا عددی هستند)
    profile = PlayerProfileRepository.get_by_fide_id(identifier)
    
    # 2. اگر پیدا نشد و شناسه عددی بود، بگردیم در آیدی‌های دیتابیس
    if not profile and identifier.isdigit():
        profile = PlayerProfileRepository.get_by_id(int(identifier))

    if not profile:
        abort(404)
        
    # اگر بازیکن FIDE ID دارد اما تأیید نشده است، اجازه نمایش عمومی با fide_id را نمی‌دهیم
    if not identifier.isdigit() and profile.fide_verification_status != "verified":
        abort(404)

    # جمع‌آوری داده‌های پروفایل
    profile_data = PlayerProfileService.get_profile_data(profile.id)
    if not profile_data:
        abort(404)

    # داده‌های تاریخچه و آمار
    rating_history = PlayerProfileService.get_rating_history(profile.id)
    tournament_history = PlayerProfileService.get_tournament_history(profile.id)
    statistics = PlayerProfileService.get_statistics(profile.id)
    game_history = PlayerProfileService.get_game_history(profile.id)

    # حذف اطلاعات حساس
    profile_data['profile'].national_id = None
    profile_data['profile'].bank_card_number = None
    profile_data['profile'].bank_account_name = None
    profile_data['profile'].phone = None

    return render_template(
        "player/public_profile.html",
        profile_data=profile_data,
        rating_history=rating_history,
        tournament_history=tournament_history,
        statistics=statistics,
        game_history=game_history
    )