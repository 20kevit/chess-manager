# tests/test_tournament_service.py
"""
Regression test: TournamentService.create / POST /create must persist a
tournament end-to-end. Guards against undefined-name errors in the service
layer that only surface at runtime (e.g. missing 'db' import).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db

from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import (UserModel, UserRoleModel)
from infrastructure.repositories.tournament import TournamentRepository
VALID_FORM = {
    "name": "Service Created Tournament",
    "city": "Tehran",
    "federation": "IRI",
    "time_control_type": "standard",
    "time_control_description": "90+30",
    "total_rounds": "5",
    "base_price": "0",
    "max_players": "",
    "cumulative_age_category": "",
}

@pytest.fixture
def organizer(app):
    with app.app_context():
        user = UserModel(email="org_create@test.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="organizer"))
        db.session.add(user)
        db.session.commit()
        yield user

def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

def test_create_route_persists_tournament(app, organizer):
    """The exact arbiter flow: POST /create with valid form data."""
    client = app.test_client()
    _login(client, organizer)

    resp = client.post("/create", data=VALID_FORM, follow_redirects=True)

    assert resp.status_code == 200

    created = TournamentModel.query.filter_by(
        name="Service Created Tournament"
    ).first()
    assert created is not None, "tournament was not persisted"
    assert created.public_id and len(created.public_id) == 8
    assert created.organizer_id == organizer.id
    assert created.status == "setup"

def test_public_id_retry_on_collision(monkeypatch, app, organizer):
    """IntegrityError on the random public_id regenerates and retries."""
    from application.tournament_service import TournamentService

    calls = {"n": 0}

    class FakeRepoSave:
        def __init__(self):
            self.saved = []

        def __call__(self, tournament):
            calls["n"] += 1
            if calls["n"] == 1:
                from sqlalchemy.exc import IntegrityError
                raise IntegrityError("dup", "dup", Exception())
            self.saved.append(tournament)
            db.session.flush()
            return tournament

    with app.app_context(), app.test_request_context():
        # Simulate an authenticated organizer so create() attaches one.
        from flask_login import login_user
        login_user(organizer)

        fake = FakeRepoSave()
        monkeypatch.setattr(
            "application.tournament.tournament_config_service.TournamentRepository.save",
            fake,
        )
        monkeypatch.setattr(
            "application.tournament.tournament_config_service.TournamentRepository.generate_public_id",
            staticmethod(lambda: f"{calls['n']:08d}"),
        )

        t = TournamentService.create(dict(VALID_FORM))
        assert t is not None
        assert calls["n"] == 2  # first attempt collided, second succeeded
