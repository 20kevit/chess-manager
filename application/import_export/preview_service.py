"""
Preview Service.

Handles tournament preview from backup files.
"""
from typing import List

from application.provider_registry import registry
from application.import_export_interface import TournamentPreviewData, BackupFileData
from application.import_export_interface import ImportProvider
from application.import_export.export_service import ImportExportError


class PreviewService:
    """Handles preview of tournaments in backup files."""

    @staticmethod
    def preview_tournaments_in_file(
        provider_name: str,
        file_content: str
    ) -> List[TournamentPreviewData]:
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'parse_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support import.")

        try:
            backup_data = provider.parse_file(file_content)
            previews = [
                TournamentPreviewData(
                    internal_id=t.internal_id,
                    name=t.name
                )
                for t in backup_data.tournaments
            ]
            return previews
        except Exception as e:
            raise ImportExportError(f"Failed to parse backup file: {str(e)}")