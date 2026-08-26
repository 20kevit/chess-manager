# tests/test_rulebook_system.py
"""
P1-D regression: rulebook system (raw text + ordered structured sections
+ public PDF).

Covers: vocabulary completeness, parse/serialize ordering, manager-tier
CRUD with replace-all section semantics, strict settings isolation,
arbiter denial / sysadmin access, secure PDF validation (magic bytes,
size cap), anonymous public PDF access, PDF removal, legacy
rulebook_text backward compatibility, and the pricing-save no-clobber pin.
"""
import io
import gc
import json
import os
import shutil

import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.rulebook import (
    SECTION_VOCABULARY, VOCABULARY_KEYS, parse_sections, serialize_sections,
    Section, default_title,
)
from infrastructure.db_models import (
    UserModel, UserRoleModel, TournamentModel,
)
from app.extensions import db


PDF_BYTES = b"%PDF-1.7\nfake-but-magic-correct"
SECTIONS_JSON = json.dumps([
    {"key": "registration", "title": "ثبت‌نام", "body": "مهلت تا ..."},
    {"key": "tie_breaks", "title": "تای‌بریک‌ها", "body": "بوخهولز ..."},
    {"key": "other", "title": "سهمیه", "body": "متن سفارشی"},
], ensure_ascii=False)


def _login(client, user):
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _get(client, url, **kw):
    from flask import g
    g.pop("_login_user", None)
    return client.get(url, **kw)


def _post(client, url, **kw):
    from flask import g
    g.pop("_login_user", None)
    return client.post(url, **kw)


@pytest.fixture
def setup(app):
    with app.app_context():
        organizer = UserModel(email="rb_org@test.com")
        organizer.set_password("x")
        organizer.roles.append(UserRoleModel(role="organizer"))
        arbiter = UserModel(email="rb_arb@test.com")
        arbiter.set_password("x")
        arbiter.roles.append(UserRoleModel(role="arbiter"))
        sysadmin = UserModel(email="rb_sys@test.com")
        sysadmin.set_password("x")
        sysadmin.is_admin = True

        t = TournamentModel(
            public_id="33000001", name="Rulebook Open",
            total_rounds=3, status="setup",
            base_price=100000,
            registration_requirements='{"phone_required": true}',
        )
        db.session.add_all([organizer, arbiter, sysadmin, t])
        db.session.flush()
        t.organizer_id = organizer.id

        # Staff rows for tier checks (accepted chief + plain arbiter).
        chief_user = UserModel(email="rb_chief@test.com")
        chief_user.set_password("x")
        chief_user.roles.append(UserRoleModel(role="arbiter"))
        db.session.add(chief_user)
        db.session.flush()
        from infrastructure.db_models import TournamentStaffModel
        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=chief_user.id,
            role="chief_arbiter", status="accepted",
            invited_by=organizer.id))
        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=arbiter.id,
            role="arbiter", status="accepted",
            invited_by=organizer.id))

        # Neighbor-section sentinel values for isolation assertions.
        t.start_date = __import__("datetime").date(2026, 10, 1)
        db.session.commit()

        yield {
            "app": app,
            "organizer": organizer.id, "chief": chief_user.id,
            "arbiter": arbiter.id, "sysadmin": sysadmin.id,
            "tournament_id": t.id,
            "public_id": "33000001",
            "dir": app.config["RULEBOOK_UPLOAD_DIR"],
        }


def T(setup):
    return TournamentModel.query.get(setup["tournament_id"])


@pytest.fixture(autouse=True)
def clean_rulebook_dir(app):
    """Keep instance/uploads/rulebooks clean between tests.

    Every test's tournament gets id=1 on a fresh DB, so without cleanup
    files would leak across tests. GC first: streamed responses hold
    Windows file handles open."""
    yield
    gc.collect()
    shutil.rmtree(app.config["RULEBOOK_UPLOAD_DIR"], ignore_errors=True)


# ── Domain unit tests ──────────────────────────────────────────────────

class TestVocabularyAndParsing:
    REQUIRED_KEYS = {
        "registration", "tournament_system", "schedule", "time_control",
        "pairing", "tie_breaks", "player_obligations", "withdrawal",
        "appeals", "prizes", "other",
    }

    def test_vocabulary_covers_required_sections(self):
        assert self.REQUIRED_KEYS <= VOCABULARY_KEYS
        for key in self.REQUIRED_KEYS:
            fa_title = default_title(key)
            assert fa_title and not fa_title.isascii(), key  # Persian label

    def test_roundtrip_preserves_order(self):
        sections = [
            Section("pairing", "جفت‌گذاری", "بخش اول"),
            Section("registration", "ثبت‌نام", "بخش دوم"),
        ]
        parsed = parse_sections(serialize_sections(sections))
        assert [(s.key, s.title) for s in parsed] == \
            [("pairing", "جفت‌گذاری"), ("registration", "ثبت‌نام")]

    def test_junk_payloads_parse_empty(self):
        for raw in (None, "", "not-json", '{"a":1}', '[1,2]', '"text"'):
            assert parse_sections(raw) == []

    def test_bad_entries_dropped_titles_defaulted(self):
        raw = json.dumps([
            "junk-string",
            {"title": "بدون کلید", "body": "متن"},
            {"key": "prizes", "body": "جوایز نقدی"},     # title defaults
            {"key": "", "title": "", "body": ""},         # dropped
        ], ensure_ascii=False)
        parsed = parse_sections(raw)
        assert len(parsed) == 2
        assert parsed[0].key == "other" and parsed[0].title == "بدون کلید"
        assert parsed[1].key == "prizes" and parsed[1].title == "جوایز"


# ── Manager CRUD + isolation ───────────────────────────────────────────

class TestRulebookCrudAndIsolation:
    def test_organizer_saves_all_three_representations(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["organizer"]))

        resp = _post(client, f"/{setup['public_id']}/settings/rulebook", data={
            "rulebook_text": "متن آزاد کامل آیین‌نامه",
            "sections_json": SECTIONS_JSON,
        }, follow_redirects=True)

        assert resp.status_code == 200
        t = T(setup)
        assert t.rulebook_text == "متن آزاد کامل آیین‌نامه"
        keys = [s.key for s in parse_sections(t.rulebook_sections)]
        assert keys == ["registration", "tie_breaks", "other"]

    def test_settings_isolation_rulebook_save_touches_nothing_else(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["organizer"]))
        t0 = T(setup)
        sentinels_before = (
            t0.base_price, t0.start_date,
            t0.registration_requirements, t0.city or "",
            t0.bank_transfer_notes or "",
        )

        _post(client, f"/{setup['public_id']}/settings/rulebook", data={
            "rulebook_text": "متن جدید",
            "sections_json": SECTIONS_JSON,
        })

        t = T(setup)
        assert (
            t.base_price, t.start_date, t.registration_requirements,
            t.city or "", t.bank_transfer_notes or "",
        ) == sentinels_before

    def test_pricing_save_never_wipes_rulebook(self, setup):
        """Backward-compat + isolation regression: pricing page no longer
        owns any rulebook field."""
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["organizer"]))
        _post(client, f"/{setup['public_id']}/settings/rulebook", data={
            "rulebook_text": "متن حفظ‌شدنی",
            "sections_json": SECTIONS_JSON,
        })

        _post(client, f"/{setup['public_id']}/admin/pricing", data={
            "base_price": "120000",
        })

        t = T(setup)
        assert t.rulebook_text == "متن حفظ‌شدنی"
        assert len(parse_sections(t.rulebook_sections)) == 3
        assert t.base_price == 120000          # pricing still works

    def test_section_ordering_and_replace_all_semantics(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["organizer"]))
        url = f"/{setup['public_id']}/settings/rulebook"

        first = json.dumps([
            {"key": "schedule", "title": "برنامه", "body": "A"},
            {"key": "prizes", "title": "جوایز", "body": "B"},
        ], ensure_ascii=False)
        _post(client, url, data={"rulebook_text": "", "sections_json": first})
        assert [s.key for s in parse_sections(T(setup).rulebook_sections)] \
            == ["schedule", "prizes"]

        # Reorder + edit one title + delete another -> single replace POST.
        second = json.dumps([
            {"key": "prizes", "title": "جوایز نقدی", "body": "B"},
            {"key": "schedule", "title": "برنامه زمانی", "body": "A"},
        ], ensure_ascii=False)
        _post(client, url, data={"rulebook_text": "", "sections_json": second})
        sections = parse_sections(T(setup).rulebook_sections)
        assert [s.key for s in sections] == ["prizes", "schedule"]
        assert sections[0].title == "جوایز نقدی"

    def test_legacy_rulebook_text_still_renders_publicly(self, setup):
        # Simulate a pre-P1-D row that only ever had raw text.
        T(setup).rulebook_text = "متن قدیمی آیین‌نامه"
        db.session.commit()

        body = setup["app"].test_client().get(
            f"/{setup['public_id']}").get_data(as_text=True)
        assert "متن قدیمی آیین‌نامه" in body


class TestPublicRendering:
    def test_public_page_renders_all_configured_forms_in_order(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["organizer"]))
        _post(client, f"/{setup['public_id']}/settings/rulebook", data={
            "rulebook_text": "پایان متن آزاد",
            "sections_json": SECTIONS_JSON,
        })
        _post(client, f"/{setup['public_id']}/settings/rulebook/pdf",
              data={"rulebook_pdf": (
                  io.BytesIO(PDF_BYTES), "book.pdf")},
              content_type="multipart/form-data")

        anon = setup["app"].test_client()
        body = anon.get(f"/{setup['public_id']}").get_data(as_text=True)
        assert "مشاهده / دانلود فایل PDF" in body
        assert body.index("ثبت‌نام") < body.index("تای‌بریک‌ها")   # order
        assert "متن سفارشی" in body                                # other
        assert "پایان متن آزاد" in body

    def test_empty_state_message_when_nothing_configured(self, setup):
        body = setup["app"].test_client().get(
            f"/{setup['public_id']}").get_data(as_text=True)
        assert "آیین‌نامه‌ای برای این مسابقه ثبت نشده است" in body


class TestAuthorization:
    def test_arbiter_cannot_modify_rulebook(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["arbiter"]))
        resp = _post(client, f"/{setup['public_id']}/settings/rulebook", data={
            "rulebook_text": "هک", "sections_json": "[]",
        })
        assert resp.status_code == 302                 # bounced to login
        assert T(setup).rulebook_text != "هک"

    def test_arbiter_cannot_upload_or_remove_pdf(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["arbiter"]))
        resp = _post(client, f"/{setup['public_id']}/settings/rulebook/pdf",
                     data={"rulebook_pdf": (io.BytesIO(PDF_BYTES), "a.pdf")},
                     content_type="multipart/form-data")
        assert resp.status_code == 403
        assert T(setup).rulebook_pdf_path is None

    @pytest.mark.parametrize("who", ("organizer", "chief", "sysadmin"))
    def test_manager_tier_can_edit(self, setup, who):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup[who]))
        marker = f"متنی از طرف {who}"
        resp = _post(client, f"/{setup['public_id']}/settings/rulebook",
                     data={"rulebook_text": marker, "sections_json": "[]"},
                     follow_redirects=True)
        assert resp.status_code == 200
        assert T(setup).rulebook_text == marker

    def test_editor_page_get_forbidden_for_arbiter(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["arbiter"]))
        assert _get(client, f"/{setup['public_id']}/settings/rulebook") \
            .status_code == 302


class TestPdfHandling:
    def _upload(self, setup, who="organizer", content=PDF_BYTES,
                filename="book.pdf"):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup[who]))
        return _post(
            client, f"/{setup['public_id']}/settings/rulebook/pdf",
            data={"rulebook_pdf": (io.BytesIO(content), filename)},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    def test_valid_pdf_uploads_and_is_public_without_login(self, setup):
        resp = self._upload(setup)
        assert "بارگذاری شد" in resp.get_data(as_text=True)

        t = T(setup)
        assert t.rulebook_pdf_path == \
            f"rulebook_{t.id}.pdf"
        stored = os.path.join(setup["dir"], t.rulebook_pdf_path)
        assert os.path.isfile(stored)
        # Never under static/.
        assert not stored.startswith(setup["app"].static_folder)

        anon = setup["app"].test_client()      # no login at all
        pdf_resp = anon.get(f"/uploads/rulebook/{setup['public_id']}")
        assert pdf_resp.status_code == 200
        assert pdf_resp.mimetype == "application/pdf"
        assert pdf_resp.data.startswith(b"%PDF-")

    def test_invalid_content_rejected_even_with_pdf_name(self, setup):
        resp = self._upload(setup, content=b"<html>not a pdf</html>")
        assert "PDF معتبر نیست" in resp.get_data(as_text=True)
        assert T(setup).rulebook_pdf_path is None
        assert not os.path.isdir(setup["dir"]) or \
            os.listdir(setup["dir"]) == []

    def test_oversize_pdf_rejected(self, setup):
        big = b"%PDF-" + b"A" * (5 * 1024 * 1024)
        resp = self._upload(setup, content=big)
        assert "۵ مگابایت" in resp.get_data(as_text=True)
        assert T(setup).rulebook_pdf_path is None

    def test_replacement_overwrites_previous_file(self, setup):
        self._upload(setup)
        stored = T(setup).rulebook_pdf_path
        path = os.path.join(setup["dir"], stored)
        first_bytes = open(path, "rb").read()

        # Same base name by design (fixed .pdf extension): the second
        # upload must overwrite the single stored file.
        newer = b"%PDF-1.7\nnewer-version"
        self._upload(setup, content=bytearray(newer))

        t = T(setup)
        assert t.rulebook_pdf_path == stored
        assert len(os.listdir(setup["dir"])) == 1
        assert open(path, "rb").read() != first_bytes
        assert bytes(open(path, "rb").read()).startswith(newer[:10]) or \
            open(path, "rb").read().startswith(b"%PDF-")

    def test_remove_endpoint_deletes_file_and_clears_column(self, setup):
        client = setup["app"].test_client()
        _login(client, UserModel.query.get(setup["organizer"]))
        self._upload(setup)
        stored = T(setup).rulebook_pdf_path

        resp = _post(client,
                     f"/{setup['public_id']}/settings/rulebook/pdf/remove",
                     follow_redirects=True)
        assert "حذف شد" in resp.get_data(as_text=True)
        assert T(setup).rulebook_pdf_path is None
        assert not os.path.exists(os.path.join(setup["dir"], stored))
        assert setup["app"].test_client().get(
            f"/uploads/rulebook/{setup['public_id']}").status_code == 404

    def test_unknown_tournament_pdf_route_404(self, setup):
        anon = setup["app"].test_client()
        assert anon.get("/uploads/rulebook/99999999").status_code == 404
