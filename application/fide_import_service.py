"""
FIDE Import Service - Backward Compatibility Facade.

Delegates to application.fide package services.
"""
from application.fide.fide_import_orchestrator import (
    FideImportOrchestrator as _FideImportOrchestrator,
    STALE_RUN_MINUTES,
    BATCH_SIZE,
)


class FideImportService:
    """Backward compatibility facade. Use application.fide package directly."""

    @staticmethod
    def run_import() -> dict:
        return _FideImportOrchestrator.run_import()

    @staticmethod
    def start_async() -> str:
        return _FideImportOrchestrator.start_async()

    @staticmethod
    def execute_import(source_label: str = "auto_download") -> dict:
        return _FideImportOrchestrator.execute_import(source_label)

    @staticmethod
    def latest_status() -> dict:
        return _FideImportOrchestrator.latest_status()
