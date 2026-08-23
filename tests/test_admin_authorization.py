# tests/test_admin_authorization.py
"""
Security regression tests: tournament arbiter access must be granted ONLY by
ACCEPTED staff invitations (pending/rejected must not grant permissions).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db_models import (
    UserModel,
    UserRoleModel,
    TournamentModel,
    TournamentStaffModel,
)
from app.extensions import db


@pytest.fixture
def setup_access(app):
    """Owner (organizer), an invitee, a system admin, and one tournament."""
    with app.app_context():
        owner = UserModel(email="owner_authz@test.com")
        owner.set_password("password123")
        owner.roles.append(UserRoleModel(role="organizer"))
        db.session.add(owner)

        invitee = UserModel(email="invitee_authz@test.com")
        invitee.set_password("password123")
        invitee.roles.append(UserRoleModel(role="arbiter"))
        db.session.add(invitee)

        sysadmin = UserModel(email="sysadmin_authz@test.com", is_admin=True)
        sysadmin.set_password("password123")
        db.session.add(sysadmin)

        db.session.commit()

        tournament = TournamentModel(
            public_id="99999901",
            admin_code="authz_admin_code",
            name="AuthZ Test Tournament",
            total_rounds=3,
            status="setup",
            organizer_id=owner.id,
        )
        db.session.add(tournament)
        db.session.commit()

        yield {
            "tournament": tournament,
            "owner": owner,
            "invitee": invitee,
            "sysadmin": sysadmin,
        }


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _add_staff(tournament_id, user_id, status):
    staff = TournamentStaffModel(
        tournament_id=tournament_id,
        user_id=user_id,
        role="arbiter",
        status=status,
    )
    db.session.add(staff)
    db.session.commit()
    return staff


class TestStaffInvitationAuthorization:

    def test_accepted_invitation_grants_arbiter_access(self, app, setup_access):
        data = setup_access
        _add_staff(data["tournament"].id, data["invitee"].id, "accepted")

        client = app.test_client()
        _login(client, data["invitee"].id)
        resp = client.get(f"/{data['tournament'].public_id}/players")
        assert resp.status_code == 200

    def test_pending_invitation_does_not_grant_access(self, app, setup_access):
        data = setup_access
        _add_staff(data["tournament"].id, data["invitee"].id, "pending")

        client = app.test_client()
        _login(client, data["invitee"].id)
        resp = client.get(f"/{data['tournament'].public_id}/players")
        assert resp.status_code == 302  # redirected to admin login, not granted

    def test_rejected_invitation_does_not_grant_access(self, app, setup_access):
        data = setup_access
        _add_staff(data["tournament"].id, data["invitee"].id, "rejected")

        client = app.test_client()
        _login(client, data["invitee"].id)
        resp = client.get(f"/{data['tournament'].public_id}/players")
        assert resp.status_code == 302  # redirected to admin login, not granted

    def test_organizer_retains_access(self, app, setup_access):
        data = setup_access
        client = app.test_client()
        _login(client, data["owner"].id)
        resp = client.get(f"/{data['tournament'].public_id}/players")
        assert resp.status_code == 200

    def test_system_admin_retains_access(self, app, setup_access):
        data = setup_access
        client = app.test_client()
        _login(client, data["sysadmin"].id)
        resp = client.get(f"/{data['tournament'].public_id}/players")
        assert resp.status_code == 200
