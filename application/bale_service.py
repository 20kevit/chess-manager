"""
Bale Service - Backward Compatibility Facade.

Delegates to application.bale package services.
Re-exports module-level functions for backward compatibility.
"""
from application.bale.bale_service import (
    BaleService,
    _log_file_path,
    _ensure_log_handler,
    _mask,
    logger,
)
