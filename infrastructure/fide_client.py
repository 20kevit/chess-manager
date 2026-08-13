import time
import logging
import requests
from typing import Optional

# Setup standard logging
logger = logging.getLogger(__name__)

_FIDE_BASE = "https://ratings.fide.com/profile"

# Improved headers to bypass basic bot protection and WAFs
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

_MAX_RETRIES = 3
_RETRY_DELAY = 1.0  # Base delay in seconds


def fetch_fide_html(fide_id: str) -> Optional[str]:
    """
    Fetch FIDE profile HTML for a given ID with retry logic.
    Returns HTML string or None on failure.
    """
    fide_id = str(fide_id).strip()
    if not fide_id:
        return None

    url = f"{_FIDE_BASE}/{fide_id}"

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=_HEADERS, timeout=10)
            
            if response.status_code == 200:
                return response.text
                
            # If player does not exist, do not retry
            if response.status_code == 404:
                logger.warning(f"Player {fide_id} not found on FIDE (404).")
                return None
                
            logger.warning(
                f"FIDE API returned status {response.status_code} for {fide_id}. "
                f"Attempt {attempt}/{_MAX_RETRIES}"
            )
            
        except requests.RequestException as e:
            logger.warning(f"Network error fetching {fide_id}: {e}. Attempt {attempt}/{_MAX_RETRIES}")
            
        # Wait before retrying (exponentially or fixed)
        if attempt < _MAX_RETRIES:
            time.sleep(_RETRY_DELAY * attempt)

    logger.error(f"Failed to fetch FIDE profile for {fide_id} after {_MAX_RETRIES} attempts.")
    return None