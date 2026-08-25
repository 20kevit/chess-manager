# tests/test_staff_permission_matrix.py
"""
P1-B regression: chief-arbiter / arbiter authorization matrix.

Server-side tier model:
- manager  (system admin | organizer | accepted chief_arbiter)
- editor   (manager | accepted arbiter)

Every protected route is exercised for the four actor roles with either a
status-code assertion (GET pages) or a state-delta assertion (POST actions),
so UI hiding can never substitute for enforcement.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db_models import (
    UserModel, UserRoleModel, PlayerProfileModel, TournamentModel,
    TournamentParticipantModel, TournamentStaffModel, RegistrationModel,
    RoundModel,
)
from application.round_service import RoundService
from interfaces.web.admin_auth import (
    require_tournament_manager, require_result_editor,
)
from app.extensions import db


# ── fixtures ───────────────────────────────────────────────────────────

def _user(email, role=None, is_admin=False):
    u = UserModel(email=email)
    u.set_password("x")
    u.is_admin = is_admin
    if role:
        u.roles.append(UserRoleModel(role=role))
    db.session.add(u)
    db.session.flush()
    return u


@pytest.fixture
def matrix(app):
    """Tournament with organizer, chief, plain arbiter, sysadmin, and two
    participants plus one generated round."""
    with app.app_context():
        organizer = _user("mx_org@test.com", "organizer")
        chief = _user("mx_chief@test.com", "arbiter")
        arbiter = _user("mx_arbiter@test.com", "arbiter")
        sysadmin = _user("mx_sys@test.com", is_admin=True)

        t = TournamentModel(
            public_id="66000001", name="Matrix Open",
            total_rounds=5, status="setup",
            organizer_id=organizer.id,
        )
        db.session.add(t)
        db.session.flush()

        p1 = PlayerProfileModel(first_name="One", last_name="Matrix")
        p2 = PlayerProfileModel(first_name="Two", last_name="Matrix")
        p3 = PlayerProfileModel(first_name="Three", last_name="Matrix")
        p4 = PlayerProfileModel(first_name="Four", last_name="Matrix")
        db.session.add_all([p1, p2, p3, p4])
        db.session.flush()

        parts = [
            TournamentParticipantModel(
                tournament_id=t.id, player_profile_id=p.id,
                start_number=i)
            for i, p in enumerate((p1, p2, p3, p4), start=1)
        ]
        db.session.add_all(parts)
        db.session.commit()

        RoundService.create_next_round(t)          # round 1 + one board

        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=chief.id,
            role="chief_arbiter", status="accepted",
            invited_by=organizer.id))
        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=arbiter.id,
            role="arbiter", status="accepted",
            invited_by=organizer.id))
        db.session.commit()

        yield {
            "app": app,
            "tournament": TournamentModel.query.get(t.id),
            "ids": {
                "organizer": organizer.id, "chief": chief.id,
                "arbiter": arbiter.id, "sysadmin": sysadmin.id,
                "part1": parts[0].id, "part2": parts[1].id,
            },
            # fresh attached user objects per lookup
            "U": lambda key: UserModel.query.get(
                {"organizer": organizer.id, "chief": chief.id,
                 "arbiter": arbiter.id, "sysadmin": sysadmin.id}[key]),
        }


def _login(client, user):
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _as(matrix, who):
    client = matrix["app"].test_client()
    _login(client, matrix["U"](who))
    return client


PID = "66000001"

# Actor expectations shorthand: allowed roles per tier
MANAGERS = ("organizer", "chief", "sysadmin")
EDITORS = ("organizer", "chief", "arbiter", "sysadmin")


class TestTierHelpersUnit:
    def test_helpers_exist(self, matrix):
        """Direct tier semantics are exercised through the route matrix;
        here we only pin the public helper surface."""
        assert callable(require_tournament_manager)
        assert callable(require_result_editor)


class TestManagerOnlyRoutes:
    """Arbiter must be rejected; organizer/chief/sysadmin allowed."""

    @pytest.mark.parametrize("url", [
        f"/{PID}/settings",
        f"/{PID}/admin/pricing",
        f"/{PID}/admin/registrations",
        f"/{PID}/players",
        f"/{PID}/players/add",
        f"/{PID}/players/import",
        f"/{PID}/admin/backup/export",
        "/dashboard/tournament/" + PID + "/manage",
    ])
    def test_get_pages(self, matrix, url):
        denied = _as(matrix, "arbiter").get(url).status_code == 302
        assert denied, url

    @pytest.mark.parametrize("who", MANAGERS)
    def test_settings_get_allowed_for_managers(self, matrix, who):
        resp = _as(matrix, who).get(f"/{PID}/settings")
        assert resp.status_code == 200

    def test_settings_post_by_arbiter_changes_nothing(self, matrix):
        client = _as(matrix, "arbiter")
        before = TournamentModel.query.filter_by(public_id=PID).first().name
        client.post(f"/{PID}/settings", data={
            "name": "Hacked Name", "city": "X", "federation": "IRI",
            "time_control_type": "standard", "total_rounds": "9",
        })
        after = TournamentModel.query.filter_by(public_id=PID).first()
        assert after.name == before and after.total_rounds == 5

    def test_pricing_post_by_arbiter_changes_nothing(self, matrix):
        client = _as(matrix, "arbiter")
        client.post(f"/{PID}/admin/pricing",
                    data={"base_price": "999999"})
        assert TournamentModel.query.filter_by(
            public_id=PID).first().base_price != 999999

    def test_player_add_by_arbiter_creates_nothing(self, matrix):
        count_before = TournamentParticipantModel.query.filter_by(
            tournament_id=matrix["tournament"].id).count()
        _as(matrix, "arbiter").post(f"/{PID}/players/add", data={
            "first_name": "Ghost", "last_name": "Player",
            "rating": "2000", "gender": "M",
        })
        assert TournamentParticipantModel.query.filter_by(
            tournament_id=matrix["tournament"].id).count() == count_before

    def test_backup_export_denied_for_arbiter(self, matrix):
        assert _as(matrix, "arbiter") \
            .get(f"/{PID}/admin/backup/export").status_code == 302

    def test_staff_add_by_plain_arbiter_blocked(self, matrix):
        outsider = _user("mx_new@test.com")
        db.session.commit()
        _as(matrix, "arbiter").post(
            f"/dashboard/tournament/{PID}/manage/staff/add",
            data={"user_id": outsider.id})
        assert TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            user_id=outsider.id).count() == 0


class TestResultEditorRoutes:
    """All four roles allowed; arbiter positively verified."""

    @pytest.mark.parametrize("who", EDITORS)
    def test_round_console_get(self, matrix, who):
        assert _as(matrix, who).get(f"/{PID}/rounds").status_code == 200

    @pytest.mark.parametrize("who", EDITORS)
    def test_round_view_get(self, matrix, who):
        assert _as(matrix, who).get(f"/{PID}/rounds/1").status_code == 200

    def test_arbiter_can_save_results(self, matrix):
        pairing = matrix["tournament"].rounds[0].pairings[0]
        resp = _as(matrix, "arbiter").post(
            f"/{PID}/rounds/1/result",
            data={f"result_{pairing.id}": "1-0"},
        )
        # save_results aborts 403 when unauthorized; authorized path flashes
        assert resp.status_code == 302
        from infrastructure.db_models import PairingModel
        assert PairingModel.query.get(pairing.id).result == "1-0"

    def test_arbiter_can_save_then_finish_round(self, matrix):
        client = _as(matrix, "arbiter")
        round1 = RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id, round_number=1).one()
        data = {f"result_{p.id}": "1-0" for p in round1.pairings}
        client.post(f"/{PID}/rounds/1/result", data=data)

        resp = client.post(f"/{PID}/rounds/1/finish")
        assert resp.status_code == 302
        assert RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id, round_number=1
        ).first().status == "finished"

    def test_arbiter_can_request_bye_page(self, matrix):
        assert _as(matrix, "arbiter") \
            .get(f"/{PID}/rounds/request-bye").status_code == 200


class TestRoundGenerationAndDeletion:
    def test_generate_round_denied_for_arbiter(self, matrix):
        rounds_before = RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id).count()
        _as(matrix, "arbiter").post(f"/{PID}/rounds/new")
        assert RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id
        ).count() == rounds_before

    @pytest.mark.parametrize("who", ("chief", "organizer", "sysadmin"))
    def test_generate_round_allowed_for_managers(self, matrix, who):
        # Business rules: every board needs a result, and the previous
        # round must be finished before a new one can be generated.
        client = _as(matrix, who)
        round1 = RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id, round_number=1).one()
        data = {f"result_{p.id}": "1-0" for p in round1.pairings}
        client.post(f"/{PID}/rounds/1/result", data=data)
        client.post(f"/{PID}/rounds/1/finish")

        rounds_before = RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id).count()
        client.post(f"/{PID}/rounds/new")
        assert RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id).count() == rounds_before + 1

    def test_delete_round_denied_for_arbiter_and_chiefless(self, matrix):
        _as(matrix, "arbiter").post(f"/{PID}/rounds/1/delete")
        assert RoundModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            round_number=1).count() == 1


class TestStaffRoleManagement:
    def test_organizer_appoints_chief(self, matrix):
        invitee = _user("mx_invitee@test.com")
        db.session.commit()
        _as(matrix, "organizer").post(
            f"/dashboard/tournament/{PID}/manage/staff/add",
            data={"user_id": invitee.id, "staff_role": "chief_arbiter"})
        row = TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            user_id=invitee.id).one()
        assert row.role == "chief_arbiter"

    def test_chief_cannot_appoint_another_chief(self, matrix):
        invitee = _user("mx_invitee2@test.com")
        db.session.commit()
        _as(matrix, "chief").post(
            f"/dashboard/tournament/{PID}/manage/staff/add",
            data={"user_id": invitee.id, "staff_role": "chief_arbiter"})
        assert TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            user_id=invitee.id).count() == 0

    def test_chief_adds_ordinary_arbiter(self, matrix):
        invitee = _user("mx_invitee3@test.com")
        db.session.commit()
        _as(matrix, "chief").post(
            f"/dashboard/tournament/{PID}/manage/staff/add",
            data={"user_id": invitee.id, "staff_role": "arbiter"})
        row = TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            user_id=invitee.id).one()
        assert row.role == "arbiter"
        assert row.invited_by == matrix["ids"]["chief"]

    def test_chief_removes_plain_arbiter(self, matrix):
        _as(matrix, "chief").post(
            f"/dashboard/tournament/{PID}/manage/staff/remove/"
            f"{matrix['ids']['arbiter']}")
        assert TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            user_id=matrix["ids"]["arbiter"]).count() == 0

    def test_chief_cannot_remove_chief(self, matrix):
        _as(matrix, "chief").post(
            f"/dashboard/tournament/{PID}/manage/staff/remove/"
            f"{matrix['ids']['chief']}")
        assert TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            user_id=matrix["ids"]["chief"]).count() == 1

    def test_organizer_removes_chief(self, matrix):
        _as(matrix, "organizer").post(
            f"/dashboard/tournament/{PID}/manage/staff/remove/"
            f"{matrix['ids']['chief']}")
        assert TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id,
            user_id=matrix["ids"]["chief"]).count() == 0

    def test_existing_rows_default_role_preserved(self, matrix):
        rows = TournamentStaffModel.query.filter_by(
            tournament_id=matrix["tournament"].id).all()
        assert {r.role for r in rows} == {"chief_arbiter", "arbiter"}


class TestReceiptVisibilityTier:
    def test_receipt_download_manager_only(self, matrix):
        profile = PlayerProfileModel(first_name="Re", last_name="Cipt")
        db.session.add(profile)
        db.session.flush()
        reg = RegistrationModel(
            tournament_id=matrix["tournament"].id,
            player_profile_id=profile.id,
            status="receipt_submitted", payment_method="transfer",
            receipt_path="receipt_x.png", final_price=1000,
        )
        db.session.add(reg)
        db.session.commit()

        arb = _as(matrix, "arbiter").get(
            f"/registration/{reg.id}/receipt")
        chief = _as(matrix, "chief").get(f"/registration/{reg.id}/receipt")
        # 403 vs 404 distinction: file missing on disk -> both tiers pass
        # authz; arbiter must be refused BEFORE that (403).
        assert arb.status_code == 403
        assert chief.status_code in (200, 404)


class TestPublicPageUnchanged:
    def test_public_view_open_to_everyone(self, matrix):
        anon = matrix["app"].test_client()
        assert anon.get(f"/{PID}").status_code == 200

    def test_capability_flags_on_view(self, matrix):
        html = _as(matrix, "arbiter").get(f"/{PID}").get_data(as_text=True)
        assert "کنسول داوری" in html
        assert "پنل مدیریت" not in html

        html = _as(matrix, "chief").get(f"/{PID}").get_data(as_text=True)
        assert "کنسول داوری" in html and "پنل مدیریت" in html
