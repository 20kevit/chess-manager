"""
Coronate provider implementation combining parser and generator.
"""
from application.import_export_interface import ImportProvider, ExportProvider, BackupFileData
from infrastructure.providers.coronate_parser import parse_coronate_json
from infrastructure.providers.coronate_generator import generate_coronate_json


class CoronateProvider(ImportProvider, ExportProvider):
    """Provider for Coronate (coronate.netlify.app) JSON format."""
    
    def parse_file(self, file_content: str) -> BackupFileData:
        """Parse Coronate JSON file content."""
        return parse_coronate_json(file_content)
    
    def generate_file(self, backup_data: BackupFileData) -> str:
        """Generate Coronate JSON file content."""
        return generate_coronate_json(backup_data)