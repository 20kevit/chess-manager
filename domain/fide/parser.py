"""
FIDE XML Rating List Parser.
Pure parsing logic - no HTTP calls or DB access here.
Uses iterative parsing to handle large XML files efficiently.
"""
import xml.etree.ElementTree as ET
from typing import Generator, List, Optional
from domain.fide.models import FidePlayerData


def parse_fide_xml(
    file_path: str, 
    allowed_federations: Optional[List[str]] = None
) -> Generator[FidePlayerData, None, None]:
    """
    Parses a FIDE XML file and yields FidePlayerData objects.
    
    Args:
        file_path: Path to the unzipped XML file.
        allowed_federations: List of federation codes to include (e.g., ['IRI']).
                             If None or empty, all federations are included.
                             
    Yields:
        FidePlayerData objects one by one.
    """
    # Use iterparse for memory efficiency
    context = ET.iterparse(file_path, events=("start", "end"))
    
    # Get the root element to clear it periodically
    _, root = next(context)
    
    fed_filter = set(allowed_federations) if allowed_federations else None
    
    for event, elem in context:
        if event == "end" and elem.tag == "player":
            country = elem.findtext("country", "")
            
            # Apply federation filter early to save memory
            if fed_filter and country not in fed_filter:
                root.clear()
                continue
                
            fide_id = elem.findtext("fideid", "")
            if not fide_id:
                root.clear()
                continue
                
            name = elem.findtext("name", "")
            sex = elem.findtext("sex", "M")
            
            def _get_int(tag: str) -> int:
                val = elem.findtext(tag, "0")
                try:
                    return int(val) if val else 0
                except ValueError:
                    return 0
                
            yield FidePlayerData(
                fide_id=fide_id,
                name=name,
                federation=country,
                sex=sex,
                title=elem.findtext("title"),
                wtitle=elem.findtext("wtitle"),
                otitle=elem.findtext("otitle"),
                foatitle=elem.findtext("foatitle"),
                rating_standard=_get_int("rating"),
                games_standard=_get_int("games"),
                k_standard=_get_int("k"),
                rating_rapid=_get_int("rapid_rating"),
                games_rapid=_get_int("rapid_games"),
                k_rapid=_get_int("rapid_k"),
                rating_blitz=_get_int("blitz_rating"),
                games_blitz=_get_int("blitz_games"),
                k_blitz=_get_int("blitz_k"),
                birth_year=elem.findtext("birth_year"),
                inactive=(elem.findtext("flag") == "inactive")
            )
            
            # Clear the element from memory to prevent RAM bloat
            root.clear()