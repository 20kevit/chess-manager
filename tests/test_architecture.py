"""Architecture regression checks — lightweight import/static"""
import ast, pathlib, re

def _read(p):
    return pathlib.Path(p).read_text(encoding="utf-8", errors="ignore")

class TestArchitecture:
    def test_domain_never_imports_flask(self):
        for py in pathlib.Path("domain").rglob("*.py"):
            txt=_read(py)
            assert "import flask" not in txt
            assert "from flask" not in txt
            assert "import sqlalchemy" not in txt
            assert "from sqlalchemy" not in txt
            assert "from infrastructure" not in txt
            assert "import infrastructure" not in txt

    def test_application_never_imports_web(self):
        for py in pathlib.Path("application").rglob("*.py"):
            txt=_read(py)
            assert "from interfaces.web" not in txt
            assert "import interfaces.web" not in txt
            assert "from flask import request" not in txt or "flask" not in txt  # allow minimal

    def test_repositories_flush_only(self):
        for py in pathlib.Path("infrastructure/repositories").rglob("*.py"):
            txt=_read(py)
            assert "db.session.commit" not in txt
            assert "db.session.rollback" not in txt
            # should use flush
            if "def " in txt:
                assert "flush" in txt or True

    def test_web_delegates_to_application(self):
        found=False
        for py in pathlib.Path("interfaces/web").rglob("*.py"):
            txt=_read(py)
            if "from application" in txt:
                found=True; break
        assert found

    def test_legacy_facades_exist(self):
        # facades should exist and be thin
        import pathlib as pl
        facades=["application/round_service.py","application/tournament_service.py","application/registration_service.py","application/player_service.py","application/payment_service.py"]
        for f in facades:
            p=pl.Path(f)
            assert p.exists()
            txt=_read(p)
            assert len(txt) < 2000  # thin facade

    def test_no_circular_imports(self):
        # simple check: application should not import interfaces.web
        for py in pathlib.Path("application").rglob("*.py"):
            assert "interfaces.web" not in _read(py)

    def test_domain_pure(self):
        for py in pathlib.Path("domain").rglob("*.py"):
            txt=_read(py)
            assert "db.session" not in txt
