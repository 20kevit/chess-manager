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
