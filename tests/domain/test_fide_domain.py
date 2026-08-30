"""FIDE parser — domain/fide/parser.py — pure XML, no DB/HTTP"""
import pytest
from pathlib import Path
from domain.fide.parser import parse_fide_xml

def write_xml(tmp_path, content):
    p = tmp_path / "fide.xml"
    p.write_text(content, encoding="utf-8")
    return str(p)

MIN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<playerslist>
    <player>
        <fideid>1234567</fideid>
        <name>FIROUZJA, ALIREZA</name>
        <country>IRI</country>
        <sex>M</sex>
        <title>GM</title>
        <rating>2780</rating>
        <games>15</games>
        <k>10</k>
        <rapid_rating>2755</rapid_rating>
        <rapid_games>10</rapid_games>
        <rapid_k>20</rapid_k>
        <blitz_rating>2800</blitz_rating>
        <blitz_games>20</blitz_games>
        <blitz_k>20</blitz_k>
        <birth_year>2003</birth_year>
    </player>
    <player>
        <fideid>7654321</fideid>
        <name>CARLSEN, MAGNUS</name>
        <country>NOR</country>
        <sex>M</sex>
        <title>GM</title>
        <rating>2830</rating>
    </player>
    <player>
        <fideid>1111111</fideid>
        <name>NOID, TEST</name>
        <country>IRI</country>
        <sex>F</sex>
        <rating>1500</rating>
    </player>
</playerslist>
"""

class TestFideParserBasic:
    def test_parse_with_federation_filter(self, tmp_path):
        fp = write_xml(tmp_path, MIN_XML)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        assert len(players) == 2
        assert all(p.federation == "IRI" for p in players)
        ids = {p.fide_id for p in players}
        assert "1234567" in ids
        assert "1111111" in ids

    def test_parse_without_filter(self, tmp_path):
        fp = write_xml(tmp_path, MIN_XML)
        players = list(parse_fide_xml(fp, allowed_federations=None))
        assert len(players) == 3

    def test_parse_empty_filter_means_all(self, tmp_path):
        fp = write_xml(tmp_path, MIN_XML)
        players = list(parse_fide_xml(fp, allowed_federations=[]))
        assert len(players) == 3

    def test_fields_mapped_correctly(self, tmp_path):
        fp = write_xml(tmp_path, MIN_XML)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        alireza = next(p for p in players if p.fide_id == "1234567")
        assert alireza.name == "FIROUZJA, ALIREZA"
        assert alireza.federation == "IRI"
        assert alireza.title == "GM"
        assert alireza.rating_standard == 2780
        assert alireza.games_standard == 15
        assert alireza.k_standard == 10
        assert alireza.rating_rapid == 2755
        assert alireza.rating_blitz == 2800
        assert alireza.birth_year == "2003"
        assert alireza.inactive is False

    def test_missing_optional_fields_default(self, tmp_path):
        fp = write_xml(tmp_path, MIN_XML)
        players = list(parse_fide_xml(fp, allowed_federations=None))
        carlsen = next(p for p in players if p.fide_id == "7654321")
        # rapid/blitz missing -> 0
        assert carlsen.rating_rapid == 0
        assert carlsen.rating_blitz == 0
        assert carlsen.birth_year is None or isinstance(carlsen.birth_year, str) or carlsen.birth_year is None

    def test_missing_fideid_skipped(self, tmp_path):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<playerslist>
    <player><name>NOFIDE</name><country>IRI</country><rating>1500</rating></player>
    <player><fideid>999</fideid><name>OK</name><country>IRI</country><rating>1500</rating></player>
</playerslist>"""
        fp = write_xml(tmp_path, xml)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        assert len(players) == 1
        assert players[0].fide_id == "999"

    def test_malformed_rating_defaults_zero(self, tmp_path):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<playerslist>
    <player><fideid>1</fideid><name>X</name><country>IRI</country><rating>notanumber</rating></player>
</playerslist>"""
        fp = write_xml(tmp_path, xml)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        assert players[0].rating_standard == 0

    def test_inactive_flag(self, tmp_path):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<playerslist>
    <player><fideid>1</fideid><name>X</name><country>IRI</country><flag>inactive</flag><rating>1500</rating></player>
    <player><fideid>2</fideid><name>Y</name><country>IRI</country><rating>1500</rating></player>
</playerslist>"""
        fp = write_xml(tmp_path, xml)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        assert next(p for p in players if p.fide_id == "1").inactive is True
        assert next(p for p in players if p.fide_id == "2").inactive is False

    def test_streaming_generator(self, tmp_path):
        fp = write_xml(tmp_path, MIN_XML)
        gen = parse_fide_xml(fp, allowed_federations=["IRI"])
        # Should be generator, not list
        import types
        assert isinstance(gen, types.GeneratorType)
        first = next(gen)
        assert first.fide_id in ("1234567","1111111")

    def test_empty_file(self, tmp_path):
        xml = """<?xml version="1.0" encoding="UTF-8"?><playerslist></playerslist>"""
        fp = write_xml(tmp_path, xml)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        assert players == []

    def test_federation_case_sensitive(self, tmp_path):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<playerslist>
    <player><fideid>1</fideid><name>X</name><country>iri</country><rating>1500</rating></player>
    <player><fideid>2</fideid><name>Y</name><country>IRI</country><rating>1500</rating></player>
</playerslist>"""
        fp = write_xml(tmp_path, xml)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        assert len(players) == 1
        assert players[0].fide_id == "2"

    def test_sex_defaults(self, tmp_path):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<playerslist>
    <player><fideid>1</fideid><name>X</name><country>IRI</country><rating>1500</rating></player>
</playerslist>"""
        fp = write_xml(tmp_path, xml)
        players = list(parse_fide_xml(fp, allowed_federations=["IRI"]))
        assert players[0].sex == "M"
