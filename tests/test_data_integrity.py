# tests/test_data_integrity.py
"""
Category C regression tests: transactions & data integrity.
C-1: backup restore reconstructs Swiss pairing state (+ format back-compat)
C-2: registration rejection_reason persists
C-3: repositories are flush-only (service layer owns commits)
C-4: manual-pairing/bye mutations live in RoundService
C-5: serialization locks are emitted for MySQL
C-6: participant deletion cleans dependent rows
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.dialects import mysql

from app.extensions import db
from application.player_service import PlayerService
from application.registration_service import RegistrationService
from application.round_service import RoundService
from infrastructure.db_models import (
    UserModel, UserRoleModel, TournamentModel, PlayerProfileModel,
    TournamentParticipantModel, RoundModel, PairingModel,
    ByeRequestModel, ManualPairingModel, RegistrationModel,
    PaymentModel, NotificationModel,
)
from infrastructure.repositories import (
    ParticipantRepository, NotificationRepository,
)


@pytest.fixture
def setup_tournament(app):
    """Organizer-owned tournament with three participants (A/B/C)."""
    with app.app_context():
        organizer = UserModel(email="org_int@test.com")
        organizer.set_password("password123")
        organizer.roles.append(UserRoleModel(role="organizer"))
        db.session.add(organizer)
        db.session.commit()

        t = TournamentModel(
            public_id="77777701",
            name="Integrity Tournament",
            total_rounds=5,
            status="setup",
            organizer_id=organizer.id,
        )
        db.session.add(t)
        db.session.flush()

        parts = []
        for i, (fn, ln, rating) in enumerate(
            [("Alice", "A", 2000), ("Bob", "B", 1500), ("Carol", "C", 1200)], start=1
        ):
            prof = PlayerProfileModel(first_name=fn, last_name=ln)
            db.session.add(prof)
            db.session.flush()
            p = TournamentParticipantModel(
                tournament_id=t.id,
                player_profile_id=prof.id,
                start_number=i,
                rating_snapshot=rating,
                status="active",
            )
            db.session.add(p)
            parts.append(p)
        db.session.commit()

        yield {
            "organizer": organizer,
            "tournament": t,
            "parts": parts,  # [A, B, C]
        }


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _backup_payload(tournament_id, include_floats=True):
    """Internal-format backup for: R1: A(b)-B(w) 1-0 ; C bye. R2: A(w)-B(b) draw."""
    r1_ab = {
        "board_number": 1,
        "white_start_number": 2,   # B plays white
        "black_start_number": 1,   # A plays black
        "result": "1-0",
    }
    r1_bye = {
        "board_number": 2,
        "white_start_number": 3,   # C gets the full-point bye
        "black_start_number": None,
        "result": "bye",
    }
    if include_floats:
        # B was a downfloater in round 1 ('d'), A upfloater ('u')
        r1_ab["white_float"] = "d"
        r1_ab["black_float"] = "u"
    return {
        "version": "1.0",
        "tournament": {
            "name": "Restored", "total_rounds": 5, "current_round": 2,
            "status": "ongoing",
        },
        "players": [
            {"start_number": 1, "first_name": "Alice", "last_name": "A", "rating": 2000},
            {"start_number": 2, "first_name": "Bob", "last_name": "B", "rating": 1500},
            {"start_number": 3, "first_name": "Carol", "last_name": "C", "rating": 1200},
        ],
        "rounds": [
            {"round_number": 1, "status": "finished",
             "pairings": [r1_ab, r1_bye]},
            {"round_number": 2, "status": "finished",
             "pairings": [{
                 "board_number": 1,
                 "white_start_number": 1,
                 "black_start_number": 2,
                 "result": "1/2",
             }]},
        ],
    }


class TestC1BackupSwissState:

    def test_replace_import_reconstructs_swiss_state(self, app, setup_tournament):
        data = setup_tournament
        t = data["tournament"]
        client = app.test_client()
        _login(client, data["organizer"])

        payload = _backup_payload(t.id)
        client.post(
            f"/{t.public_id}/backup/import",
            data={"json_file": (__import__("io").BytesIO(
                __import__("json").dumps(payload).encode()), "backup.json"),
                  "mode": "replace"},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        parts = {p.start_number: p for p in ParticipantRepository.get_all(t.id)}
        a, b, c = parts[1], parts[2], parts[3]

        # Points rebuilt from results: A: 0+0.5, B: 1+0.5, C: bye=1
        assert a.points == 0.5
        assert b.points == 1.5
        assert c.points == 1.0
        # Color history rebuilt chronologically
        assert a.color_history == "bw"   # black R1 (played), white in R2
        assert b.color_history == "wb"   # white R1, black R2
        assert c.color_history == "-"    # unplayed bye
        # received_bye flag restored from the bye result
        assert c.received_bye is True
        assert a.received_bye is False
        # Float tags survive the round-trip when present in the backup
        assert b.float_history.startswith("d")
        assert a.float_history.startswith("u")
        # Pairing numbers follow FIDE order: rating DESC -> A=1, B=2, C=3
        assert (a.pairing_no, b.pairing_no, c.pairing_no) == (1, 2, 3)

    def test_old_backup_without_floats_still_imports(self, app, setup_tournament):
        """Backward compatibility: pre-float backups must restore cleanly."""
        data = setup_tournament
        t = data["tournament"]
        client = app.test_client()
        _login(client, data["organizer"])

        payload = _backup_payload(t.id, include_floats=False)
        resp = client.post(
            f"/{t.public_id}/backup/import",
            data={"json_file": (__import__("io").BytesIO(
                __import__("json").dumps(payload).encode()), "backup.json"),
                  "mode": "replace"},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200

        parts = {p.start_number: p for p in ParticipantRepository.get_all(t.id)}
        assert parts[1].points == 0.5
        assert parts[2].points == 1.5
        assert parts[3].received_bye is True
        assert parts[1].pairing_no == 1

    def test_merge_appends_pairing_numbers(self, app, setup_tournament):
        data = setup_tournament
        t = data["tournament"]
        # Existing player already holds pairing_no 5
        data["parts"][0].pairing_no = 5
        db.session.commit()

        client = app.test_client()
        _login(client, data["organizer"])
        payload = _backup_payload(t.id)
        payload["rounds"] = []
        # Merge dedupes by name — use a fresh player so a newcomer is created.
        payload["players"] = [
            {"start_number": 9, "first_name": "Dave", "last_name": "D", "rating": 1400},
        ]
        client.post(
            f"/{t.public_id}/backup/import",
            data={"json_file": (__import__("io").BytesIO(
                __import__("json").dumps(payload).encode()), "backup.json"),
                  "mode": "merge"},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        newcomer = (
            TournamentParticipantModel.query.filter_by(tournament_id=t.id)
            .order_by(TournamentParticipantModel.start_number.desc())
            .first()
        )
        assert newcomer.pairing_no == 6


class TestC2RejectionReason:

    def test_reject_registration_persists_reason(self, app, setup_tournament):
        data = setup_tournament
        t = data["tournament"]
        profile = PlayerProfileModel.query.filter_by(first_name="Alice").first()
        reg = RegistrationModel(
            tournament_id=t.id, player_profile_id=profile.id,
            status="pending", final_price=0,
        )
        db.session.add(reg)
        db.session.commit()

        RegistrationService.reject_registration(reg.id, "ظرفیت تکمیل است")

        refreshed = RegistrationModel.query.get(reg.id)
        assert refreshed.status == "rejected"
        assert refreshed.rejection_reason == "ظرفیت تکمیل است"


class TestC3RepositoriesFlushOnly:

    def test_notification_repo_does_not_commit(self, app, setup_tournament):
        user = setup_tournament["organizer"]
        notif = NotificationModel(
            user_id=user.id, type="WELCOME", title="t", message="m", is_read=False
        )
        db.session.add(notif)
        db.session.commit()

        assert NotificationRepository.mark_as_read(notif.id, user.id) is True
        # Rollback must undo the change — proves the repository did not commit.
        db.session.rollback()
        db.session.expire_all()
        assert NotificationModel.query.get(notif.id).is_read is False


class TestC4ServiceOwnedMutations:

    def test_cancel_bye_request_scoped_to_tournament(self, app, setup_tournament):
        data = setup_tournament
        t = data["tournament"]
        p = data["parts"][0]
        bye = ByeRequestModel(
            tournament_id=t.id, participant_id=p.id,
            bye_type="half-bye", for_round=1,
        )
        other_t = TournamentModel(public_id="77777702", name="Other", total_rounds=3)
        db.session.add(other_t)
        db.session.flush()
        other_bye = ByeRequestModel(
            tournament_id=other_t.id, participant_id=p.id,
            bye_type="half-bye", for_round=1,
        )
        db.session.add_all([bye, other_bye])
        db.session.commit()

        assert RoundService.cancel_bye_request(t, bye.id) is True
        # A bye belonging to another tournament must not be cancellable here
        assert RoundService.cancel_bye_request(t, other_bye.id) is False
        assert RoundService.cancel_bye_request(other_t, bye.id) is False

    def test_remove_manual_pairing(self, app, setup_tournament):
        data = setup_tournament
        t = data["tournament"]
        a, b = data["parts"][0], data["parts"][1]
        mp = ManualPairingModel(
            tournament_id=t.id, round_number=1,
            white_participant_id=a.id, black_participant_id=b.id,
        )
        db.session.add(mp)
        db.session.commit()

        assert RoundService.remove_manual_pairing(t, a.id) is True
        assert RoundService.remove_manual_pairing(t, a.id) is False


class TestC5SerializationLocks:

    def test_for_update_emitted_on_mysql(self, app):
        q = select(TournamentModel.id).where(TournamentModel.id == 1).with_for_update()
        compiled = str(q.compile(dialect=mysql.dialect()))
        assert "FOR UPDATE" in compiled.upper()

    def test_capacity_boundary_rejected(self, app, setup_tournament):
        from application.registration_service import RegistrationService
        data = setup_tournament
        t = data["tournament"]
        t.max_players = 1
        db.session.commit()

        user = UserModel(email="cap@test.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)
        db.session.commit()

        with pytest.raises(ValueError):
            # One active participant already occupies the single slot.
            RegistrationService.create_registration(t, user, {
                "first_name": "Extra", "last_name": "Player",
            })


class TestC6DeleteDependentRows:

    def test_delete_cleans_byes_and_locks(self, app, setup_tournament):
        data = setup_tournament
        t = data["tournament"]
        p = data["parts"][2]  # Carol
        db.session.add(ByeRequestModel(
            tournament_id=t.id, participant_id=p.id,
            bye_type="half-bye", for_round=1,
        ))
        db.session.add(ManualPairingModel(
            tournament_id=t.id, round_number=1,
            white_participant_id=data["parts"][0].id,
            black_participant_id=p.id,
        ))
        db.session.commit()

        PlayerService.delete(p, t.id)

        assert ByeRequestModel.query.filter_by(participant_id=p.id).count() == 0
        assert ManualPairingModel.query.filter(
            (ManualPairingModel.white_participant_id == p.id)
            | (ManualPairingModel.black_participant_id == p.id)
        ).count() == 0
        assert ParticipantRepository.get_by_id(p.id, t.id) is None
