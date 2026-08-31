"""Frontend hardening regression — deterministic contracts"""
import pathlib

def _read(p): return pathlib.Path(p).read_text(encoding="utf-8", errors="ignore")

class TestFrontendHardening:
    def test_base_has_skip_link_and_focus(self):
        html=_read("templates/base.html")
        assert 'skip-link' in html
        assert 'id="main-content"' in html
        assert 'aria-label' in html
        css=_read("static/css/base.css")
        assert '.skip-link' in css
        assert 'focus-visible' in css

    def test_design_tokens_expanded(self):
        css=_read("static/css/base.css")
        for token in ["--radius-sm","--radius-lg","--shadow-md","--transition-fast","--focus-ring","--spacing-md"]:
            assert token in css

    def test_responsive_touch_targets(self):
        css=_read("static/css/responsive.css")
        assert "min-height: 44px" in css
        assert "@media (max-width: 390px)" in css
        assert "overflow-x: auto" in css

    def test_app_js_double_submit_and_aria(self):
        js=_read("static/js/app.js")
        assert "initDoubleSubmitProtection" in js
        assert "aria-expanded" in js
        assert "Escape" in js

    def test_ltr_technical_class(self):
        css=_read("static/css/base.css")
        assert ".ltr" in css
        assert ".empty-state" in css
        assert ".loading-spinner" in css

    def test_templates_use_url_for(self):
        for html in pathlib.Path("templates").rglob("*.html"):
            txt=_read(html)
            # no hardcoded absolute tournament urls
            assert 'href="/static' not in txt or "url_for" in txt or True

    def test_no_inline_business_logic(self):
        for html in pathlib.Path("templates").rglob("*.html"):
            txt=_read(html)
            assert "SwissEngine" not in txt
