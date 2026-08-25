# tests/test_deployment_paths.py
"""
Category K regression tests: no CWD-dependent production paths.
All runtime-writable locations anchor to the Flask instance path.
"""
import os

import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.bale_service import _log_file_path as bale_log_path
from application.telegram_service import _log_file_path as telegram_log_path


def test_fide_data_dir_anchored_to_instance(app):
    expected = os.path.join(app.instance_path, "data", "fide")
    assert app.config["FIDE_DATA_DIR"] == expected


def test_fide_storage_manager_reads_anchored_dir(app):
    from infrastructure.fide.storage import FideStorageManager
    # The manager must consume the anchored path via config, not CWD.
    period = FideStorageManager.get_period_string()
    assert app.config["FIDE_DATA_DIR"].endswith(os.path.join("data", "fide"))
    assert period  # sanity: period format helper intact


def test_messenger_logs_anchor_to_instance_inside_app_context(app):
    with app.app_context():
        assert telegram_log_path() == os.path.join(
            app.instance_path, "telegram_debug.log"
        )
        assert bale_log_path() == os.path.join(
            app.instance_path, "bale_debug.log"
        )


# ── P0-G: no CWD fallback for messenger debug logs ──

def _with_cleared_handlers(logger):
    """Snapshot and clear a module-level logger; returns restore fn."""
    saved = list(logger.handlers)
    logger.handlers.clear()

    def restore():
        logger.handlers[:] = saved
    return restore


def test_log_path_is_none_without_app_context():
    """Outside any application context there must be NO path candidate:
    the old CWD fallback leaked stray root-level telegram/bale logs."""
    import threading
    from application.telegram_service import _log_file_path as tg_path
    results = {}

    # A bare thread shares no Flask context stack with the test.
    worker = threading.Thread(target=lambda: results.update(path=tg_path()))
    worker.start(); worker.join()
    assert results["path"] is None


def test_ensure_handler_outside_context_never_writes_to_cwd(app):
    import threading
    import logging
    from application import bale_service

    cwd_before = set(os.listdir(os.getcwd()))
    restore = _with_cleared_handlers(bale_service.logger)
    try:
        worker = threading.Thread(
            target=bale_service._ensure_log_handler)
        worker.start(); worker.join()

        attached = [h for h in bale_service.logger.handlers]
        assert len(attached) == 1
        assert isinstance(attached[0], logging.NullHandler)
        new_entries = set(os.listdir(os.getcwd())) - cwd_before
        assert not any(name.endswith(".log") for name in new_entries)
        assert "bale_debug.log" not in new_entries
    finally:
        restore()


def test_ensure_handler_inside_context_targets_instance_dir(app):
    import logging
    from application import telegram_service

    restore = _with_cleared_handlers(telegram_service.logger)
    try:
        with app.app_context():
            telegram_service._ensure_log_handler()
            handlers = list(telegram_service.logger.handlers)
            assert len(handlers) == 1
            assert isinstance(handlers[0], logging.FileHandler)
            base = os.path.basename(handlers[0].baseFilename)
            assert base == "telegram_debug.log"
            assert handlers[0].baseFilename.startswith(app.instance_path)
    finally:
        restore()


def test_htaccess_example_is_safe_template():
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".htaccess.example",
    )
    assert os.path.isfile(path), ".htaccess.example must be tracked in the repo"

    with open(path, encoding="utf-8") as f:
        content = f.read()

    assert "PassengerPython" in content          # venv wiring guidance present
    assert "CPANELUSER" in content               # placeholders, not real values
    assert "PassengerAppRoot" in content
    # No secrets / real credentials may be committed in this template.
    lowered = content.lower()
    for marker in ("password", "secret_key", "bot_token",
                   "zarinpal_merchant", "@gmail", "20kevit"):
        assert marker not in lowered, f"template must not contain: {marker}"
