"""
FIDE File Storage Manager.
Handles downloading, unzipping, and retention of raw FIDE XML files.

P1-G: the manager also honours SERVER-PLACED files (cPanel manual path):
an already-extracted players_list_xml.xml is used directly; a pre-placed
players_list_xml.zip is extracted in place. Automatic monthly download
stays the primary path when neither exists. Download progress can be
reported through an optional callback (fraction 0..1 or None when the
total size is unknown).
"""
import os
import zipfile
import shutil
import requests
from datetime import datetime, timedelta
from flask import current_app
from typing import Callable, Optional, Tuple


class FideStorageError(Exception):
    """Raised on invalid/unsafe archive contents."""


def _period_dir(base_dir: str) -> str:
    period = get_period_string()
    path = os.path.join(base_dir, period)
    os.makedirs(path, exist_ok=True)
    return path


def get_period_string() -> str:
    """Returns current period string: YYYY-MM"""
    return datetime.utcnow().strftime("%Y-%m")


def _safe_member_names(zip_ref: zipfile.ZipFile) -> list:
    """XML member names inside the archive, rejecting traversal paths."""
    safe = []
    for name in zip_ref.namelist():
        base = os.path.basename(name)
        if not base.lower().endswith(".xml"):
            continue
        if base != name and (".." in name or name.startswith(("/", "\\"))):
            raise FideStorageError(f"Unsafe archive member: {name}")
        safe.append(name)
    return safe


def extract_players_zip(zip_path: str) -> str:
    """Extract a players-list ZIP into its own folder.

    Validates the archive (magic + structure), accepts exactly the XML
    members it contains (first one wins — historical behaviour), renames
    to the canonical players_list_xml.xml next to the zip, and deletes
    the archive afterwards. Returns the XML path.
    """
    if not os.path.isfile(zip_path):
        raise FideStorageError("ZIP file not found.")
    with open(zip_path, "rb") as probe:
        if probe.read(4) != b"PK\x03\x04":
            raise FideStorageError("File is not a valid ZIP archive.")

    period_dir = os.path.dirname(os.path.abspath(zip_path))
    xml_path = os.path.join(period_dir, "players_list_xml.xml")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            members = _safe_member_names(zip_ref)
            if not members:
                raise FideStorageError(
                    "No XML file found inside the FIDE archive.")
            zip_ref.extract(members[0], period_dir)
            extracted = os.path.join(period_dir, members[0])
            if extracted != xml_path:
                os.replace(extracted, xml_path)
        os.remove(zip_path)
        return xml_path
    except FideStorageError:
        raise
    except Exception as exc:
        current_app.logger.error(f"FIDE zip extraction failed: {exc}")
        raise FideStorageError(f"ZIP extraction failed: {exc}")


def ensure_players_xml(progress_cb: Optional[Callable[[Optional[float]], None]] = None) -> Tuple[str, str]:
    """Guarantee a players_list_xml.xml for the current period.

    Order of preference:
      1. already-extracted XML   -> ('existing_xml', path)
      2. server-placed ZIP       -> ('existing_zip', path)  [extracted]
      3. automatic download      -> ('downloaded', path)

    progress_cb receives download fractions (0..1) or None while the
    total size is unknown. Raises FideStorageError on hard failures so
    callers record them loudly.
    """
    base_dir = current_app.config.get("FIDE_DATA_DIR")
    url = current_app.config.get("FIDE_XML_URL")
    if not base_dir:
        raise FideStorageError("FIDE configuration missing in config.py")

    period_dir = _period_dir(base_dir)
    zip_path = os.path.join(period_dir, "players_list_xml.zip")
    xml_path = os.path.join(period_dir, "players_list_xml.xml")

    # 1. Already extracted (covers previous runs AND manual XML placement).
    if os.path.exists(xml_path):
        return "existing_xml", xml_path

    # 2. Server-placed ZIP (cPanel manual fallback).
    if os.path.exists(zip_path):
        return "existing_zip", extract_players_zip(zip_path)

    # 3. Automatic monthly download (primary path, unchanged behaviour).
    if not url:
        raise FideStorageError("FIDE configuration missing in config.py")
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = r.headers.get("Content-Length")
            total = int(total) if total and total.isdigit() else None
            downloaded = 0
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb:
                        progress_cb(
                            downloaded / total if total else None)
        return "downloaded", extract_players_zip(zip_path)
    except FideStorageError:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        raise
    except Exception as exc:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        current_app.logger.error(f"FIDE download failed: {exc}")
        raise FideStorageError(f"Download failed: {exc}")


# Backwards-compatible wrapper used by older call sites/tests.
def download_and_extract_xml(progress_cb: Optional[Callable[[Optional[float]], None]] = None) -> Optional[str]:
    try:
        _, xml_path = ensure_players_xml(progress_cb)
        return xml_path
    except FideStorageError as exc:
        current_app.logger.error(f"FIDE storage error: {exc}")
        return None


def count_players_in_xml(xml_path: str) -> int:
    """Cheap byte-scan estimate of <player ...> occurrences (pre-scan
    total used to compute honest parse percentages)."""
    total = 0
    needle = b"<player"
    try:
        with open(xml_path, "rb") as f:
            tail = b""
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                window = tail + chunk
                total += window.count(needle)
                tail = window[-len(needle):]
    except OSError:
        return 0
    return total


def cleanup_old_files() -> int:
    """
    Deletes period directories older than the retention period.
    Returns the number of deleted directories.
    """
    base_dir = current_app.config.get("FIDE_DATA_DIR")
    retention_days = current_app.config.get("FIDE_RAW_RETENTION_DAYS", 90)

    if not base_dir or not os.path.exists(base_dir):
        return 0

    deleted_count = 0
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    for dirname in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, dirname)
        if not os.path.isdir(dir_path):
            continue

        # Expected format: YYYY-MM
        try:
            dir_date = datetime.strptime(dirname + "-01", "%Y-%m-%d")
            if dir_date < cutoff_date:
                shutil.rmtree(dir_path)
                deleted_count += 1
        except ValueError:
            continue

    return deleted_count


class FideStorageManager:
    """Static facade kept for existing callers/tests."""

    get_period_string = staticmethod(get_period_string)
    download_and_extract_xml = staticmethod(download_and_extract_xml)
    extract_players_zip = staticmethod(extract_players_zip)
    ensure_players_xml = staticmethod(ensure_players_xml)
    count_players_in_xml = staticmethod(count_players_in_xml)
    cleanup_old_files = staticmethod(cleanup_old_files)
