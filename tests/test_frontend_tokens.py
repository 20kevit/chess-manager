"""Frontend token contract: no hardcoded light-theme colors.

Components must consume semantic design tokens (static/css/tokens.css).
Fixed dark bands (header/footer/hero) and print paper are allowlisted.
See docs/UI_UX_REDESIGN.md and AGENTS.md frontend rules.
"""
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")

# Fixed dark-band fills/text that are identical in both themes.
FIXED_BANDS = {
    "#fff", "#ffffff",  # on-fill text / skip link / pagination current
    "#0b1220", "#101924", "#17212b",  # dark bands (header/footer/hero)
    "#f2f6fa", "#c9d4e0", "#9db0c2",  # text on dark bands
    "#e8eef4",  # toast dark-mode surface
    "#231300",  # dark text on accent badge
}

CSS_ALLOW = {"tokens.css", "print.css"}  # token home + print paper


def _css_hexes():
    offenders = {}
    for css in (REPO / "static" / "css").glob("*.css"):
        if css.name in CSS_ALLOW:
            continue
        found = sorted({h for h in HEX.findall(css.read_text(encoding="utf-8"))}
                       - FIXED_BANDS)
        if found:
            offenders[css.name] = found
    return offenders


def _template_hexes():
    offenders = {}
    for html in (REPO / "templates").rglob("*.html"):
        src = html.read_text(encoding="utf-8")
        hits = set()
        for m in re.finditer(r"<style>(.*?)</style>", src, re.S):
            hits.update(HEX.findall(m.group(1)))
        for m in re.finditer(r'style="([^"]*)"', src):
            hits.update(HEX.findall(m.group(1)))
        hits -= FIXED_BANDS
        if hits:
            offenders[str(html.relative_to(REPO))] = sorted(hits)
    return offenders


class TestTokenContract:
    def test_css_uses_semantic_tokens(self):
        assert _css_hexes() == {}, (
            "Hardcoded colors outside tokens.css/print.css/fixed bands. "
            "Use semantic var(--*) tokens instead.")

    def test_templates_use_semantic_tokens(self):
        assert _template_hexes() == {}, (
            "Hardcoded colors in templates. Use semantic var(--*) tokens.")
