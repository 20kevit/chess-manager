"""
Manual test script for FIDE XML Parser.
Run from project root: python scripts/test_fide_parser.py
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.fide.parser import parse_fide_xml

def test_parser():
    # Mock XML data simulating FIDE structure
    mock_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<playerslist>
    <player>
        <fideid>1234567</fideid>
        <name>ALIREZA, FIROUZJA</name>
        <country>IRI</country>
        <sex>M</sex>
        <title>GM</title>
        <wtitle></wtitle>
        <otitle></otitle>
        <foatitle></foatitle>
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
        <flag>inactive</flag>
    </player>
    <player>
        <fideid>7654321</fideid>
        <name>DOE, JOHN</name>
        <country>USA</country>
        <sex>M</sex>
        <title>IM</title>
        <wtitle></wtitle>
        <otitle></otitle>
        <foatitle></foatitle>
        <rating>2400</rating>
        <games>10</games>
        <k>20</k>
        <rapid_rating>2350</rapid_rating>
        <rapid_games>5</rapid_games>
        <rapid_k>20</rapid_k>
        <blitz_rating>2380</blitz_rating>
        <blitz_games>8</blitz_games>
        <blitz_k>20</blitz_k>
        <birth_year>1990</birth_year>
    </player>
</playerslist>
"""
    
    file_path = "test_fide_mock.xml"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mock_xml_content)

    print("Testing FIDE Parser (Filtered by IRI)...")
    
    # Parse with IRI filter
    players = list(parse_fide_xml(file_path, allowed_federations=["IRI"]))
    
    # Assertions
    assert len(players) == 1, f"Expected 1 player, got {len(players)}"
    assert players[0].fide_id == "1234567"
    assert players[0].federation == "IRI"
    assert players[0].rating_standard == 2780
    assert players[0].inactive == True
    assert players[0].title == "GM"
    
    print("✅ Parser test passed! IRI filter works correctly.")
    
    # Clean up
    os.remove(file_path)

if __name__ == "__main__":
    test_parser()