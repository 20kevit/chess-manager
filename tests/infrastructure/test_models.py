"""Model constraints — unique, FK, defaults, JSON"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.tournament import TournamentModel, RoundModel, PairingModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.fide import FidePlayerModel, FideImportModel
from infrastructure.models.notification import NotificationModel
from infrastructure.models.prize import TournamentPrizeModel

class TestUserModel:
    def test_email_unique(self, app, db):
        u1=UserModel(email="unique@test.com")
        u1.set_password("pass12345")
        db.session.add(u1); db.session.commit()
        u2=UserModel(email="unique@test.com")
        u2.set_password("pass12345")
        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_password_hash_not_plaintext(self, app, db):
        u=UserModel(email="hash@test.com")
        u.set_password("mypass123")
        assert u.password_hash != "mypass123"
        assert u.check_password("mypass123") is True
        assert u.check_password("wrong") is False

    def test_is_admin_default(self, app, db):
        u=UserModel(email="admin_default@test.com")
        u.set_password("pass12345")
        db.session.add(u); db.session.commit()
        assert u.is_admin in (False, None, 0)

class TestTournamentModel:
    def test_public_id_unique(self, app, db):
        t1=TournamentModel(public_id="11111111", name="T1", total_rounds=5, status="setup")
        db.session.add(t1); db.session.commit()
        t2=TournamentModel(public_id="11111111", name="T2", total_rounds=5, status="setup")
        db.session.add(t2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_status_defaults(self, app, db):
        import random
        t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name="StatusT", total_rounds=5)
        db.session.add(t); db.session.commit()
        assert t.status in ("setup", None)

    def test_json_fields(self, app, db):
        t=TournamentModel(public_id="22222222", name="JsonT", total_rounds=5, status="setup", tiebreak_rules='["buchholz"]', notification_prefs='{"ROUND_CREATED": true}')
        db.session.add(t); db.session.commit()
        fetched=TournamentModel.query.filter_by(public_id="22222222").first()
        assert 'buchholz' in fetched.tiebreak_rules
        assert 'ROUND_CREATED' in fetched.notification_prefs

class TestParticipantModel:
    def test_unique_start_number(self, app, db):
        import random
        t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name="UniqStart", total_rounds=5, status="setup")
        db.session.add(t); db.session.commit()
        prof1=PlayerProfileModel(first_name="A", last_name="B")
        prof2=PlayerProfileModel(first_name="C", last_name="D")
        db.session.add_all([prof1,prof2]); db.session.commit()
        p1=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof1.id, start_number=1, rating_snapshot=2000)
        db.session.add(p1); db.session.commit()
        p2=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof2.id, start_number=1, rating_snapshot=1800)
        db.session.add(p2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_rating_property(self, app, db):
        t=TournamentModel(public_id="33333333", name="RatingProp", total_rounds=5, status="setup")
        db.session.add(t); db.session.commit()
        prof=PlayerProfileModel(first_name="P", last_name="X")
        db.session.add(prof); db.session.commit()
        p=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=1, rating_snapshot=2200)
        db.session.add(p); db.session.commit()
        assert p.rating==2200
        assert p.ranking_label==p.start_number

class TestRoundModel:
    def test_round_unique_per_tournament(self, app, db):
        t=TournamentModel(public_id="44444444", name="RoundUniq", total_rounds=5, status="setup")
        db.session.add(t); db.session.commit()
        r1=RoundModel(tournament_id=t.id, round_number=1, status="ongoing")
        db.session.add(r1); db.session.commit()
        r2=RoundModel(tournament_id=t.id, round_number=1, status="ongoing")
        db.session.add(r2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

class TestFideImportModel:
    def test_fide_import_defaults(self, app, db):
        m=FideImportModel(period="2024-01", status="pending")
        db.session.add(m); db.session.commit()
        assert m.id is not None
        assert m.period=="2024-01"

class TestNotificationModel:
    def test_is_read_default(self, app, db):
        u=UserModel(email="notif_model@test.com")
        u.set_password("pass12345")
        db.session.add(u); db.session.commit()
        n=NotificationModel(user_id=u.id, type="WELCOME", title="t", message="m")
        db.session.add(n); db.session.commit()
        assert n.is_read==False
        assert n.created_at is not None

class TestPrizeModel:
    def test_prize_cascade(self, app, db):
        t=TournamentModel(public_id="55555555", name="PrizeT", total_rounds=5, status="setup")
        db.session.add(t); db.session.commit()
        prize=TournamentPrizeModel(tournament_id=t.id, category_type="overall", rank=1, amount=1000)
        db.session.add(prize); db.session.commit()
        assert prize.id is not None
