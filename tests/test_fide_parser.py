"""
Unit tests for FIDE XML Parser.
Run with: pytest tests/test_fide_parser.py
"""
import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.fide.parser import parse_fide_xml

@pytest.fixture
def mock_xml_file(tmp_path):
    """Creates a temporary mock FIDE XML file."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
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
</playerslist>
"""
    file_path = tmp_path / "test.xml"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

def test_parse_with_federation_filter(mock_xml_file):
    """Test that parser correctly filters by federation."""
    players = list(parse_fide_xml(mock_xml_file, allowed_federations=["IRI"]))
    
    assert len(players) == 1
    assert players[0].fide_id == "1234567"
    assert players[0].federation == "IRI"
    assert players[0].rating_standard == 2780
    assert players[0].title == "GM"

def test_parse_without_filter(mock_xml_file):
    """Test that parser returns all players if no filter is applied."""
    players = list(parse_fide_xml(mock_xml_file, allowed_federations=None))
    
    assert len(players) == 2
    federations = [p.federation for p in players]
    assert "IRI" in federations
    assert "NOR" in federations