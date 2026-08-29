"""
Import/Export Service - Backward Compatibility Facade.

Delegates to application.import_export package services.
"""
from typing import List

from application.import_export.export_service import ExportService as _ExportService
from application.import_export.import_service import ImportService as _ImportService
from application.import_export.preview_service import PreviewService as _PreviewService
from application.import_export.export_service import ImportExportError


class ImportExportService:
    """Backward compatibility facade. Use application.import_export package directly."""

    @staticmethod
    def export_tournament(tournament, provider_name: str) -> str:
        return _ExportService.export_tournament(tournament, provider_name)

    @staticmethod
    def import_tournament(tournament, provider_name: str, file_content: str, mode: str = "merge") -> None:
        _ImportService.import_tournament(tournament, provider_name, file_content, mode)

    @staticmethod
    def preview_tournaments_in_file(provider_name: str, file_content: str) -> List:
        return _PreviewService.preview_tournaments_in_file(provider_name, file_content)

    @staticmethod
    def create_tournament_from_backup(provider_name: str, file_content: str, target_tournament_internal_id: str):
        return _ImportService.create_tournament_from_backup(provider_name, file_content, target_tournament_internal_id)
