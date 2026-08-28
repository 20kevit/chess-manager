# tests/test_payment_receipt_flow.py
"""
P0-E regression: payment/receipt workflow correctness.

- receipt_submitted lifecycle (submit -> review -> approve | reject-to-
  retryable-pending | player discard)
- server-side gateway-toggle enforcement and receipt lock on online pay
- consistent capacity accounting across create/approve/callback paths
- friendly duplicate-registration errors for every blocking status
- dashboard payment actions navigate to the payment section, never the
  gateway directly

Fixtures deliberately return PLAIN IDS: rows created inside a fixture's
nested app context detach when it exits, so every mutation re-fetches a
fresh, session-attached row first.
"""
import io
import os
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.payment_service import PaymentService
from application.registration_service import (
    RegistrationService, BLOCKING_REGISTRATION_STATUSES,
)

from app.extensions import db

from infrastructure.models.notification import NotificationModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.registration import (PaymentModel, RegistrationModel)
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import (UserModel, UserRoleModel)
PNG_RECEIPT = b"\x89PNG\r\n\x1a\nreceipt"

def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

def _reset_cached_login_user():
    from flask import g
    g.pop("_login_user", None)

def _get(client, url, **kw):
    _reset_cached_login_user()
    return client.get(url, **kw)

def _post(client, url, **kw):
    _reset_cached_login_user()
    return client.post(url, **kw)

def R(model, row_id):
    """Fresh, session-attached instance for the current app context."""
    return model.query.filter_by(id=row_id).first()

_counter = [0]

def make_registration(*, price=100000, enable_online=True, status="pending"):
    """Create user + organizer + tournament + priced registration.

    Returns plain ids (user_id, organizer_id, tournament_id, reg_id)."""
    _counter[0] += 1
    seq = _counter[0]

    user = UserModel(email=f"rcpt_u_{seq}@test.com")
    user.set_password("password123")
    user.roles.append(UserRoleModel(role="player"))
    organizer = UserModel(email=f"rcpt_o_{seq}@test.com")
    organizer.set_password("password123")
    profile = PlayerProfileModel(first_name="Re", last_name="Ceipt")
    db.session.add_all([user, organizer, profile])
    db.session.flush()
    profile.user_id = user.id
    db.session.flush()

    t = TournamentModel(
        public_id=f"77{seq:06d}",          # 8 digits, collision-free
        name=f"Receipt Open {seq}",
        total_rounds=3,
        status="setup",
        enable_online_payment=enable_online,
        base_price=price,
    )
    db.session.add(t)
    db.session.flush()
    t.organizer_id = organizer.id

    reg = RegistrationModel(
        tournament_id=t.id, player_profile_id=profile.id,
        user_id=user.id, status=status, final_price=price,
    )
    db.session.add(reg)
    db.session.commit()
    return {
        "user_id": user.id,
        "organizer_id": organizer.id,
        "tournament_id": t.id,
        "reg_id": reg.id,
    }

def _upload(client, reg_id):
    return _post(
        client, f"/registration/{reg_id}/upload-receipt",
        data={"receipt": (io.BytesIO(PNG_RECEIPT), "r.png")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

class TestReceiptLifecycle:
    def test_upload_from_pending_enters_review_and_cancels_online_session(
        self, app
    ):
        with app.app_context():
            fx = make_registration()
            receipt_dir = app.config["RECEIPT_UPLOAD_DIR"]
            db.session.add(PaymentModel(
                registration_id=fx["reg_id"],
                amount=R(RegistrationModel, fx["reg_id"]).final_price,
                status="pending", gateway="zarinpal",
                authority="A0000000009",
            ))
            db.session.commit()

            client = app.test_client(); _login(client, R(UserModel, fx["user_id"]))
            resp = _upload(client, fx["reg_id"])

            assert "در انتظار تایید برگزارکننده" in resp.get_data(as_text=True)
            reg = R(RegistrationModel, fx["reg_id"])
            assert reg.status == "receipt_submitted"
            assert reg.payment_method == "transfer"
            assert reg.receipt_path is not None
            pmt = PaymentModel.query.one()
            assert pmt.status == "cancelled"
            assert "receipt_submitted" in (pmt.gateway_metadata or "")
            assert os.path.isfile(os.path.join(receipt_dir, reg.receipt_path))

    def test_upload_from_payment_pending_allowed(self, app):
        with app.app_context():
            fx = make_registration(status="payment_pending")
            client = app.test_client(); _login(client, R(UserModel, fx["user_id"]))
            _upload(client, fx["reg_id"])
            assert R(RegistrationModel, fx["reg_id"]).status \
                == "receipt_submitted"

    def test_double_upload_is_rejected_with_info_flash(self, app):
        with app.app_context():
            fx = make_registration()
            client = app.test_client(); _login(client, R(UserModel, fx["user_id"]))
            _upload(client, fx["reg_id"])
            first_name = R(RegistrationModel, fx["reg_id"]).receipt_path

            resp = _upload(client, fx["reg_id"])
            assert "قبلاً ثبت شده" in resp.get_data(as_text=True)
            assert R(RegistrationModel, fx["reg_id"]).receipt_path == first_name

    def test_upload_rejected_after_terminal_states(self, app):
        for status in ("paid", "approved", "rejected"):
            with app.app_context():
                fx = make_registration(status=status)
                client = app.test_client(); _login(client, R(UserModel, fx["user_id"]))
                resp = _upload(client, fx["reg_id"])
                assert "امکان بارگذاری رسید وجود ندارد" \
                    in resp.get_data(as_text=True)

    def test_discard_restores_retryable_online_state(self, app):
        class OkStub:
            base_pay_url = "https://pay.test/StartPay"
            def request_payment(self, amount, description, callback_url):
                from types import SimpleNamespace
                return SimpleNamespace(authority="A0000000042",
                                       payment_url="https://pay.test/A42")

        from application.payment_service import PaymentService as PS
        original_gateway = PS.gateway
        PS.gateway = OkStub()
        try:
            with app.app_context():
                fx = make_registration()
                receipt_dir = app.config["RECEIPT_UPLOAD_DIR"]
                client = app.test_client()
                _login(client, R(UserModel, fx["user_id"]))
                _upload(client, fx["reg_id"])

                resp = _post(
                    client,
                    f"/registration/{fx['reg_id']}/receipt/discard",
                    follow_redirects=True,
                )
                assert "حذف شد" in resp.get_data(as_text=True)

                reg = R(RegistrationModel, fx["reg_id"])
                assert reg.status == "pending"
                assert reg.payment_method == "online"
                assert reg.receipt_path is None
                assert os.listdir(receipt_dir) == []

                # Online payment must be retryable right after discarding.
                url = PaymentService.initiate_payment(
                    reg.id, fx["user_id"], "https://site/callback")
                assert url.endswith("/A42")
        finally:
            PS.gateway = original_gateway

    def test_reject_receipt_returns_to_pending_with_reason(self, app):
        with app.app_context():
            fx = make_registration()
            receipt_dir = app.config["RECEIPT_UPLOAD_DIR"]
            client = app.test_client(); _login(client, R(UserModel, fx["user_id"]))
            _upload(client, fx["reg_id"])
            stored_name = R(RegistrationModel, fx["reg_id"]).receipt_path

            admin = app.test_client()
            _login(admin, R(UserModel, fx["organizer_id"]))
            public_id = R(TournamentModel, fx["tournament_id"]).public_id
            resp = _post(
                admin,
                f"/{public_id}/admin/registrations/"
                f"{fx['reg_id']}/reject-receipt",
                data={"rejection_reason": "تصویر ناخوانا است"},
                follow_redirects=True,
            )
            assert "بازگشت" in resp.get_data(as_text=True)

            reg = R(RegistrationModel, fx["reg_id"])
            assert reg.status == "pending"      # retryable, NOT rejected
            assert reg.rejection_reason == "تصویر ناخوانا است"
            assert reg.receipt_path is None
            assert not os.path.exists(os.path.join(receipt_dir, stored_name))

            # Player may immediately resubmit a corrected receipt.
            _upload(client, fx["reg_id"])
            assert R(RegistrationModel, fx["reg_id"]).status \
                == "receipt_submitted"

class TestApprovalOfReceipts:
    def test_approving_receipt_creates_participant_and_notifies(self, app):
        with app.app_context():
            fx = make_registration()
            client = app.test_client(); _login(client, R(UserModel, fx["user_id"]))
            _upload(client, fx["reg_id"])

            admin = app.test_client()
            _login(admin, R(UserModel, fx["organizer_id"]))
            public_id = R(TournamentModel, fx["tournament_id"]).public_id
            resp = _post(
                admin,
                f"/{public_id}/admin/registrations/{fx['reg_id']}/approve",
                data={}, follow_redirects=True,
            )
            assert "تأیید شد" in resp.get_data(as_text=True)

            assert R(RegistrationModel, fx["reg_id"]).status == "approved"
            assert TournamentParticipantModel.query.filter_by(
                tournament_id=fx["tournament_id"]).count() == 1

            notification = NotificationModel.query.filter_by(
                type="PAYMENT_CONFIRMED").first()
            assert notification is not None
            assert notification.user_id == fx["user_id"]

class TestOnlinePaymentGates:
    def test_online_payment_blocked_while_receipt_under_review(self, app):
        with app.app_context():
            fx = make_registration()
            client = app.test_client(); _login(client, R(UserModel, fx["user_id"]))
            _upload(client, fx["reg_id"])

            with pytest.raises(ValueError, match="رسید پرداخت شما در حال بررسی"):
                PaymentService.initiate_payment(
                    fx["reg_id"], fx["user_id"], "https://site/cb")

    def test_disabled_gateway_enforced_server_side(self, app):
        with app.app_context():
            fx = make_registration(enable_online=False)
            with pytest.raises(ValueError,
                               match="پرداخت آنلاین برای این مسابقه غیرفعال"):
                PaymentService.initiate_payment(
                    fx["reg_id"], fx["user_id"], "https://site/cb")

            # UI hides the online method but shows transfer guidance instead.
            client = app.test_client()
            _login(client, R(UserModel, fx["user_id"]))
            public_id = R(TournamentModel, fx["tournament_id"]).public_id
            body = _get(client, f"/{public_id}/register").get_data(as_text=True)
            assert "پرداخت آنلاین برای این مسابقه غیرفعال است" in body
            assert "زرین‌پال" not in body

class TestDuplicateAndCapacityConsistency:
    def test_blocking_statuses_all_friendly_duplicates(self, app):
        for status in ("paid", "approved", "receipt_submitted",
                       "payment_pending", "pending"):
            with app.app_context():
                fx = make_registration(status=status)
                assert status in BLOCKING_REGISTRATION_STATUSES
                client = app.test_client()
                _login(client, R(UserModel, fx["user_id"]))
                public_id = R(TournamentModel, fx["tournament_id"]).public_id
                resp = _post(client, f"/{public_id}/register", data={},
                             follow_redirects=True)
                assert "قبلاً ثبت‌نام کرده‌اید" in resp.get_data(as_text=True)
                assert RegistrationModel.query.filter_by(
                    tournament_id=fx["tournament_id"]).count() == 1

    def test_capacity_counts_every_open_slot_status(self, app):
        """A single receipt_submitted registration occupies the whole
        capacity of a 1-player tournament."""
        with app.app_context():
            fx = make_registration(status="pending")
            t_row = R(TournamentModel, fx["tournament_id"])
            t_row.max_players = 1

            other_profile = PlayerProfileModel(first_name="Se",
                                               last_name="Cond")
            other_user = UserModel(email="second_cap@test.com")
            other_user.set_password("x")
            other_user.roles.append(UserRoleModel(role="player"))
            db.session.add_all([other_profile, other_user])
            db.session.flush()

            db.session.add(RegistrationModel(
                tournament_id=t_row.id, player_profile_id=other_profile.id,
                user_id=other_user.id, status="receipt_submitted",
                final_price=0,
            ))
            db.session.commit()

            with pytest.raises(ValueError, match="ظرفیت"):
                RegistrationService.create_registration(t_row,
                                                        R(UserModel, fx["user_id"]),
                                                        {})

    def test_approval_blocked_when_capacity_filled_elsewhere(self, app):
        with app.app_context():
            fx = make_registration()
            t_row = R(TournamentModel, fx["tournament_id"])
            t_row.max_players = 1

            filler_profile = PlayerProfileModel(first_name="Cap",
                                                last_name="Filler")
            db.session.add(filler_profile)
            db.session.flush()
            db.session.add(TournamentParticipantModel(
                tournament_id=t_row.id,
                player_profile_id=filler_profile.id,
                start_number=1,
            ))
            db.session.commit()

            client = app.test_client()
            _login(client, R(UserModel, fx["user_id"]))
            _upload(client, fx["reg_id"])   # enters receipt_submitted

            admin = app.test_client()
            _login(admin, R(UserModel, fx["organizer_id"]))
            resp = _post(
                admin,
                f"/{t_row.public_id}/admin/registrations/"
                f"{fx['reg_id']}/approve",
                data={}, follow_redirects=True,
            )
            assert "ظرفیت ثبت‌نام تکمیل شده است." in resp.get_data(as_text=True)
            assert R(RegistrationModel, fx["reg_id"]).status \
                == "receipt_submitted"
            assert TournamentParticipantModel.query.filter_by(
                tournament_id=t_row.id,
                player_profile_id=R(RegistrationModel,
                                    fx["reg_id"]).player_profile_id,
            ).count() == 0

class TestDashboardPaymentActions:
    def test_buttons_map_to_payment_section_never_gateway(self, app):
        """One player holds three registrations in the three payable
        states; each must surface its own action linking to the
        registration page's payment section."""
        with app.app_context():
            user = UserModel(email="dash_pay@test.com")
            user.set_password("x")
            user.roles.append(UserRoleModel(role="player"))
            profile = PlayerProfileModel(first_name="Da", last_name="Sh")
            profile.user_id = None  # linked right after ids exist
            db.session.add_all([user, profile])
            db.session.flush()
            profile.user_id = user.id
            db.session.flush()

            regs = {}
            for i, status in enumerate(("pending", "payment_pending",
                                        "receipt_submitted")):
                t = TournamentModel(public_id=f"88{i:06d}",
                                    name=f"Dash {status}", total_rounds=3)
                db.session.add(t)
                db.session.flush()
                regs[status] = (t, RegistrationModel(
                    tournament_id=t.id, player_profile_id=profile.id,
                    user_id=user.id, status=status, final_price=50000 + i,
                ))
                db.session.add(regs[status][1])
            db.session.commit()

            client = app.test_client(); _login(client, user)
            _reset_cached_login_user()
            body = client.get("/dashboard").get_data(as_text=True)

            for status, (tournament, reg) in regs.items():
                assert f"/{tournament.public_id}/register" in body
                assert f"/{reg.id}/pay" not in body   # never a gateway POST
            assert "ادامه پرداخت" in body
            assert "مشاهده رسید" in body
            # Strongest guarantee: no direct gateway trigger remains anywhere
            # on the dashboard (old behavior was a POST to /pay).
            assert "initiate_payment" not in body
            assert "/pay" not in body
