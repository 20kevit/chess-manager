"""Architectural regression — web layer boundaries"""
import ast, pathlib, re

WEB_DIR = pathlib.Path("interfaces/web")
APP_DIR = pathlib.Path("application")

def _read(p):
    return pathlib.Path(p).read_text(encoding="utf-8", errors="ignore")

class TestWebArch:
    def test_no_direct_model_query_in_web(self):
        offenders=[]
        for py in WEB_DIR.rglob("*.py"):
            txt=_read(py)
            if "Model.query" in txt:
                offenders.append(str(py))
        # grandfathered tech-debt allowed; ensure not unbounded
        assert len(offenders) <= 10, f"Too many direct Model.query in web: {offenders}"

    def test_web_does_not_import_db_commit(self):
        # allow commits in a few legacy routes; just ensure not pervasive
        count=0
        for py in WEB_DIR.rglob("*.py"):
            txt=_read(py)
            if "db.session.commit" in txt:
                count+=1
        assert count <= 5, f"Too many commits in web layer: {count}"

    def test_web_delegates_to_application(self):
        # at least some routes should import from application
        found=False
        for py in WEB_DIR.rglob("*.py"):
            if "from application" in _read(py) or "import application" in _read(py):
                found=True; break
        assert found, "Web layer should delegate to application services"

    def test_no_business_logic_in_templates(self):
        # templates should not contain python business logic markers like "SwissEngine"
        for html in pathlib.Path("templates").rglob("*.html"):
            txt=_read(html)
            assert "SwissEngine" not in txt
            assert "pair_round" not in txt

    def test_no_inline_javascript_heavy(self):
        heavy=[]
        for html in pathlib.Path("templates").rglob("*.html"):
            txt=_read(html)
            inline = re.findall(r"<script(?![^>]*src)[^>]*>(.*?)</script>", txt, flags=re.DOTALL|re.IGNORECASE)
            for block in inline:
                if len(block.strip()) > 10000:
                    heavy.append(str(html))
        assert len(heavy)==0, f"Large inline JS found: {heavy}"

    def test_css_js_externalized(self):
        # tournament/view.html should load tournament-view.js via extra_js
        txt=_read("templates/tournament/view.html")
        assert "tournament-view.js" in txt
        # register should have registration.js
        assert "registration.js" in _read("templates/tournament/register.html")

    def test_data_attrs_used(self):
        # register.html should have data-api-url
        assert "data-api-url" in _read("templates/tournament/register.html")
        # notifications index should have data-id
        assert "data-id" in _read("templates/notifications/index.html")

    def test_csrf_meta_in_base(self):
        assert 'csrf-token' in _read("templates/base.html")
        assert 'csrf_token' in _read("templates/base.html").lower()

    def test_no_hardcoded_urls(self):
        # tournament view should use url_for
        txt=_read("templates/tournament/view.html")
        assert "url_for" in txt
        assert txt.count('"/') < 5  # few hardcoded absolute paths allowed

    def test_application_does_not_import_web(self):
        for py in APP_DIR.rglob("*.py"):
            txt=_read(py)
            assert "from interfaces.web" not in txt
            assert "import interfaces.web" not in txt
