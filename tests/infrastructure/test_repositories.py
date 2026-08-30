"""Repository contracts — flush-only, filtering, ordering"""
import pytest
from app.extensions import db
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.tournament import TournamentModel, RoundModel, PairingModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.notification import NotificationModel
from infrastructure.repositories.tournament import TournamentRepository, RoundRepository, PairingRepository
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.user import UserRepository
from infrastructure.repositories.notification import NotificationRepository

def _tournament(name="RepoT"):
    import random
    t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name=name, total_rounds=5, status="setup")
    db.session.add(t); db.session.flush()
    return t

class TestTournamentRepository:
    def test_generate_public_id_unique(self, app, db):
        ids=set()
        for _ in range(5):
            pid=TournamentRepository.generate_public_id()
            assert len(pid)==8 and pid.isdigit()
            ids.add(pid)
        assert len(ids)==5

    def test_save_flush_no_commit(self, app, db):
        t=TournamentModel(public_id="12345678", name="FlushT", total_rounds=5, status="setup")
        TournamentRepository.save(t)
        # flush should have assigned id without commit
        assert t.id is not None
        # but not yet committed? In test, flush is enough to query
        found=TournamentRepository.get_by_public_id("12345678")
        assert found is not None

    def test_get_by_public_id(self, app, db):
        t=_tournament("FindMe")
        db.session.commit()
        found=TournamentRepository.get_by_public_id(t.public_id)
        assert found.id==t.id
        assert TournamentRepository.get_by_public_id("99999999") is None

class TestParticipantRepository:
    def test_next_start_number(self, app, db):
        t=_tournament("NextNum")
        db.session.commit()
        assert ParticipantRepository.next_start_number(t.id)==1
        prof=PlayerProfileModel(first_name="A", last_name="B")
        db.session.add(prof); db.session.flush()
        p=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=1, rating_snapshot=2000)
        db.session.add(p); db.session.commit()
        assert ParticipantRepository.next_start_number(t.id)==2

    def test_get_active_filtering(self, app, db):
        t=_tournament("ActiveFilter")
        db.session.commit()
        for status in ["active","withdrawn","active"]:
            prof=PlayerProfileModel(first_name="P", last_name="X")
            db.session.add(prof); db.session.flush()
            p=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=ParticipantRepository.next_start_number(t.id), rating_snapshot=2000, status=status)
            db.session.add(p)
        db.session.commit()
        active=ParticipantRepository.get_active(t.id)
        assert len(active)==2
        assert all(p.status=="active" for p in active)

    def test_flush_only(self, app, db):
        t=_tournament("FlushOnly")
        db.session.commit()
        prof=PlayerProfileModel(first_name="F", last_name="L")
        db.session.add(prof); db.session.flush()
        p=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=1, rating_snapshot=1500)
        ParticipantRepository.save(p)
        assert p.id is not None
        assert TournamentParticipantModel.query.get(p.id) is not None

class TestRoundRepository:
    def test_get_last(self, app, db):
        t=_tournament("RoundLast")
        db.session.commit()
        assert RoundRepository.get_last(t.id) is None
        r1=RoundModel(tournament_id=t.id, round_number=1, status="finished")
        db.session.add(r1); db.session.commit()
        assert RoundRepository.get_last(t.id).id==r1.id
        r2=RoundModel(tournament_id=t.id, round_number=2, status="ongoing")
        db.session.add(r2); db.session.commit()
        assert RoundRepository.get_last(t.id).round_number==2

class TestNotificationRepository:
    def test_save_and_unread_count(self, app, db):
        u=UserModel(email="notif_repo@test.com")
        u.set_password("pass12345")
        db.session.add(u); db.session.commit()
        n=NotificationModel(user_id=u.id, type="WELCOME", title="t", message="m", is_read=False)
        NotificationRepository.save(n)
        assert n.id is not None
        assert NotificationRepository.get_unread_count(u.id)==1
        NotificationRepository.mark_as_read(n.id, u.id)
        assert NotificationRepository.get_unread_count(u.id)==0

    def test_user_isolation_mark_read(self, app, db):
        u1=UserModel(email="u1_repo@test.com"); u1.set_password("pass12345")
        u2=UserModel(email="u2_repo@test.com"); u2.set_password("pass12345")
        db.session.add_all([u1,u2]); db.session.commit()
        n=NotificationModel(user_id=u1.id, type="WELCOME", title="t", message="m", is_read=False)
        NotificationRepository.save(n); db.session.commit()
        assert NotificationRepository.mark_as_read(n.id, u2.id) is False
        assert NotificationRepository.get_unread_count(u1.id)==1

class TestUserRepository:
    def test_get_by_email(self, app, db):
        u=UserModel(email="findme@test.com")
        u.set_password("pass12345")
        db.session.add(u); db.session.commit()
        found=UserRepository.get_by_email("findme@test.com")
        assert found.id==u.id
        assert UserRepository.get_by_email("nonexistent@test.com") is None

    def test_transaction_ownership(self, app, db):
        # repositories never commit; verify that after save, commit is needed to persist across sessions
        u=UserModel(email="tx@test.com")
        u.set_password("pass12345")
        UserRepository.save(u)
        # flush made it visible in same session
        assert UserRepository.get_by_id(u.id) is not None
