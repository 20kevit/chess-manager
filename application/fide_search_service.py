"""
FIDE Search Service - Backward Compatibility Facade.

Delegates to application.fide.fide_search_service.FideSearchService.
"""
from typing import List, Dict, Optional

from application.fide.fide_search_service import FideSearchService as _FideSearchService


class FideSearchService:
    """Backward compatibility facade. Use application.fide.fide_search_service directly."""

    @staticmethod
    def search(query: str, federation: Optional[str] = None, limit: int = 20) -> List[Dict]:
        return _FideSearchService.search(query, federation, limit)
