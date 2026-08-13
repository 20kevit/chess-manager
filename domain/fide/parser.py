"""
FIDE HTML parser.
Pure parsing logic - no HTTP calls here.
Supports both legacy and modern FIDE DOM structures.
"""
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class FidePlayerData:
    first_name: str = ""
    last_name: str = ""
    gender: str = "M"
    federation: str = ""
    fide_title: str = ""
    rating_standard: int = 0
    rating_rapid: int = 0
    rating_blitz: int = 0
    birth_year: str = ""
    k_factor: int = 20


_COUNTRY_TO_FED = {
    "Iran": "IRI", "Russia": "RUS", "China": "CHN",
    "India": "IND", "United States": "USA", "Germany": "GER",
    "France": "FRA", "Azerbaijan": "AZE", "Armenia": "ARM",
    "Georgia": "GEO", "Ukraine": "UKR", "Poland": "POL",
    "Hungary": "HUN", "Netherlands": "NED", "Spain": "ESP",
    "Italy": "ITA", "Turkey": "TUR", "Iraq": "IRQ",
    "Norway": "NOR", "England": "ENG", "Uzbekistan": "UZB",
    "Kazakhstan": "KAZ"
}

_TITLE_MAP = {
    "Grandmaster": "GM",
    "International Master": "IM",
    "FIDE Master": "FM",
    "Candidate Master": "CM",
    "Woman Grandmaster": "WGM",
    "Woman International Master": "WIM",
    "Woman FIDE Master": "WFM",
    "Woman Candidate Master": "WCM",
}


def parse_fide_html(html: str) -> Optional[FidePlayerData]:
    """
    Extract player data from FIDE profile HTML.
    Returns FidePlayerData or None if name not found.
    """
    data = FidePlayerData()

    # 1. Name parsing (Supports new and old DOMs, plus fallback to meta title)
    name_match = re.search(r'profile-top-title[^>]*>\s*([^<]+)\s*</div>', html, re.IGNORECASE)
    if not name_match:
        name_match = re.search(r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>\s*([^<]+)\s*</h1>', html, re.IGNORECASE)
    if not name_match:
        # Ultimate fallback: Page title
        name_match = re.search(r'<title>\s*([^<]+?)\s*(?:FIDE|-)', html, re.IGNORECASE)

    if not name_match:
        return None

    name = name_match.group(1).strip()
    if "," in name:
        parts = name.split(",", 1)
        data.last_name = parts[0].strip()
        data.first_name = parts[1].strip()
    else:
        parts = name.split()
        data.last_name = parts[0] if parts else name
        data.first_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    # 2. Ratings (Standard, Rapid, Blitz)
    # Tries modern <strong> structure, falls back to legacy classes
    std = re.search(r'std\s*<strong[^>]*>\s*(\d+)', html, re.IGNORECASE)
    if not std:
        std = re.search(r'profile-standart[^>]*>.*?([\d]{3,4})', html, re.DOTALL | re.IGNORECASE)
    if std:
        data.rating_standard = _safe_int(std.group(1))

    rapid = re.search(r'rapid\s*<strong[^>]*>\s*(\d+)', html, re.IGNORECASE)
    if not rapid:
        rapid = re.search(r'profile-rapid[^>]*>.*?([\d]{3,4})', html, re.DOTALL | re.IGNORECASE)
    if rapid:
        data.rating_rapid = _safe_int(rapid.group(1))

    blitz = re.search(r'blitz\s*<strong[^>]*>\s*(\d+)', html, re.IGNORECASE)
    if not blitz:
        blitz = re.search(r'profile-blitz[^>]*>.*?([\d]{3,4})', html, re.DOTALL | re.IGNORECASE)
    if blitz:
        data.rating_blitz = _safe_int(blitz.group(1))

    # 3. Birth year
    byear = re.search(r'B-Year:</div>\s*<div[^>]*>\s*(\d{4})\s*</div>', html, re.IGNORECASE)
    if not byear:
        byear = re.search(r'class="profile-info-byear\s*">\s*(\d{4})\s*</p>', html, re.IGNORECASE)
    if byear:
        data.birth_year = byear.group(1).strip()

    # 4. Gender
    sex_match = re.search(r'Sex:</div>\s*<div[^>]*>\s*(Male|Female)\s*</div>', html, re.IGNORECASE)
    if not sex_match:
        sex_match = re.search(r'class="profile-info-sex\s*">\s*(Male|Female)\s*</p>', html, re.IGNORECASE)
    
    if sex_match and sex_match.group(1).lower() == "female":
        data.gender = "F"
    else:
        data.gender = "M"

    # 5. Federation
    fed = re.search(r'Federation:</div>\s*<div[^>]*>.*?([A-Za-z\s]+)</div>', html, re.DOTALL | re.IGNORECASE)
    if not fed:
        fed = re.search(r'class="profile-info-country\s*">.*?([A-Za-z\s]+)</div>', html, re.DOTALL | re.IGNORECASE)
    
    if fed:
        country = fed.group(1).strip()
        if len(country) == 3 and country.isupper():
            data.federation = country
        else:
            data.federation = _COUNTRY_TO_FED.get(country, country[:3].upper())

    # 6. Title
    title_match = re.search(r'FIDE title:</div>\s*<div[^>]*>\s*([^<]+)\s*</div>', html, re.IGNORECASE)
    if not title_match:
        title_match = re.search(r'class="profile-info-title\s*">\s*<p>\s*([^<\n]+?)\s*</p>', html, re.IGNORECASE)
    
    if title_match:
        t = title_match.group(1).strip()
        if t.lower() != "none":
            if t in _TITLE_MAP:
                data.fide_title = _TITLE_MAP[t]
            elif len(t) <= 3:
                data.fide_title = t.upper()

    return data


def _safe_int(value: str) -> int:
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return 0