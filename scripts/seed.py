"""
Seed script: Creates a demo tournament with players and rounds.
Usage: python scripts/seed.py
"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run import app
from app.extensions import db
from infrastructure.db_models import TournamentModel, PlayerModel
from infrastructure.repositories import TournamentRepository, PlayerRepository
from application.round_service import RoundService

# داده‌های نمونه
DEMO_PLAYERS = [
    {"first_name": "مگنوس", "last_name": "کارلسن", "rating": 2830, "fide_title": "GM", "gender": "M", "federation": "NOR"},
    {"first_name": "فابیانو", "last_name": "کاروانا", "rating": 2786, "fide_title": "GM", "gender": "M", "federation": "USA"},
    {"first_name": "دینگ", "last_name": "لیرن", "rating": 2780, "fide_title": "GM", "gender": "M", "federation": "CHN"},
    {"first_name": "یان", "last_name": "نپومنیاچی", "rating": 2769, "fide_title": "GM", "gender": "M", "federation": "RUS"},
    {"first_name": "آلیرضا", "last_name": "فیروزجا", "rating": 2760, "fide_title": "GM", "gender": "M", "federation": "FRA"},
    {"first_name": "آنیش", "last_name": "گیری", "rating": 2749, "fide_title": "GM", "gender": "M", "federation": "NED"},
    {"first_name": "لوران‌تیو", "last_name": "دیرین", "rating": 2740, "fide_title": "GM", "gender": "M", "federation": "USA"},
    {"first_name": "وسلی", "last_name": "سو", "rating": 2735, "fide_title": "GM", "gender": "M", "federation": "USA"},
    {"first_name": "شخریار", "last_name": "مامدیاروف", "rating": 2730, "fide_title": "GM", "gender": "M", "federation": "AZE"},
    {"first_name": "لونتین", "last_name": "آروند", "rating": 2725, "fide_title": "GM", "gender": "M", "federation": "IND"},
    {"first_name": "پرهام", "last_name": "مقصودلو", "rating": 2710, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "هوما", "last_name": "حقوقی", "rating": 2350, "fide_title": "WGM", "gender": "F", "federation": "IRI"},
    {"first_name": "سارا", "last_name": "خادم‌الشریعه", "rating": 2490, "fide_title": "GM", "gender": "F", "federation": "IRI"},
    {"first_name": "امین", "last_name": "طباطبایی", "rating": 2690, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "بردیا", "last_name": "دانشور", "rating": 2580, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "آرین", "last_name": "قائم‌مقامی", "rating": 2560, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "مبینا", "last_name": "علی‌نسب", "rating": 2250, "fide_title": "WIM", "gender": "F", "federation": "IRI", "age_category": "U18"},
    {"first_name": "ایلیا", "last_name": "رضایی", "rating": 1950, "fide_title": "FM", "gender": "M", "federation": "IRI", "age_category": "U16"},
    {"first_name": "نیکا", "last_name": "احمدی", "rating": 1800, "fide_title": "", "gender": "F", "federation": "IRI", "age_category": "U14"},
    {"first_name": "آرتین", "last_name": "محمدی", "rating": 1650, "fide_title": "", "gender": "M", "federation": "IRI", "age_category": "U12"},
]

DEMO_RESULTS = ["1-0", "0-1", "1/2"]


def create_seed_tournament():
    with app.app_context():
        print("🏆 ساخت تورنومنت نمونه...")

        tournament = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            admin_code=TournamentRepository.generate_admin_code(),
            name="مسابقات بین‌المللی شطرنج ایران ۱۴۰۴",
            city="تهران",
            federation="IRI",
            time_control_type="standard",
            time_control_description="۹۰ دقیقه + ۳۰ ثانیه",
            total_rounds=7,
            chief_arbiter="استاد علیرضا داوری",
            arbiter="فاطمه محمدی",
            tiebreak_rules='["buchholz_cut1","buchholz","sonneborn_berger","progressive"]',
            cumulative_age_category=True,
        )
        TournamentRepository.save(tournament)

        print(f"   شناسه: {tournament.public_id}")
        print(f"   کد ادمین: {tournament.admin_code}")

        # افزودن بازیکنان
        print(f"👥 افزودن {len(DEMO_PLAYERS)} بازیکن...")
        for i, p_data in enumerate(DEMO_PLAYERS, 1):
            player = PlayerModel(
                tournament_id=tournament.id,
                start_number=i,
                first_name=p_data["first_name"],
                last_name=p_data["last_name"],
                gender=p_data.get("gender", "M"),
                federation=p_data.get("federation", "IRI"),
                fide_title=p_data.get("fide_title", ""),
                rating_standard=p_data.get("rating", 0),
                k_factor=10 if p_data.get("rating", 0) > 2400 else 20,
                age_category=p_data.get("age_category", ""),
            )
            db.session.add(player)

        db.session.commit()

        # ایجاد و بازی ۴ دور
        for round_num in range(1, 5):
            print(f"🔄 دور {round_num}...")

            try:
                new_round = RoundService.create_next_round(tournament)

                # ثبت نتایج تصادفی
                from infrastructure.repositories import PairingRepository
                pairings = PairingRepository.get_all_for_round(new_round.id)

                for pairing in pairings:
                    if pairing.result in ("bye", "half-bye", "zero-bye"):
                        continue
                    if pairing.black_player_id:
                        pairing.result = random.choice(DEMO_RESULTS)

                db.session.commit()
                PlayerRepository.update_points(tournament.id)

                # پایان دور
                RoundService.finish_round(new_round, tournament)

            except Exception as e:
                print(f"   خطا: {e}")
                break

        print()
        print("=" * 50)
        print(f"✅ تورنومنت نمونه ساخته شد!")
        print(f"   لینک عمومی: https://swiss.20kevit.ir/{tournament.public_id}")
        print(f"   لینک ادمین: https://swiss.20kevit.ir/{tournament.public_id}/admin/{tournament.admin_code}")
        print(f"   ورود ادمین: https://swiss.20kevit.ir/{tournament.public_id}/admin/login")
        print("=" * 50)


if __name__ == "__main__":
    create_seed_tournament()