"""Shared view helpers for route modules.

Delegates to application.round.display_service.RoundDisplayService for
crosstable and score formatting logic.
"""
from application.round.display_service import RoundDisplayService

# Re-export for backward compatibility with existing imports
build_cell = RoundDisplayService.build_crosstable_cell