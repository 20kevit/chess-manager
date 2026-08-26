# infrastructure/file_storage.py
"""
Private file-storage helpers shared by upload endpoints.

Hardening rules (extends the Category-H receipt pattern to profile media):
- files live under instance-anchored directories, never under static/
- filenames are server-generated via secure_filename of an internal base
  name; user-supplied filenames are discarded entirely
- image content is verified by magic bytes, not by the declared extension
- stored values are bare filenames; resolution takes os.path.basename only,
  which makes path traversal impossible
"""
import os

from werkzeug.utils import secure_filename


class FileStorageError(Exception):
    """Raised on invalid uploads; `reason` is a stable machine code."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


# 5 MB per private media file (global request ceiling stays at 8 MB).
MAX_IMAGE_BYTES = 5 * 1024 * 1024

# P1-D: public rulebook PDFs share the same per-file ceiling as other
# uploads (consistent with the receipt cap).
MAX_PDF_BYTES = 5 * 1024 * 1024

PDF_MIMETYPE = "application/pdf"

IMAGE_MIMETYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
}

# Extensions that may exist on disk for a given base name (replacement set).
IMAGE_EXTENSIONS = ("png", "jpg", "jpeg")
PDF_EXTENSIONS = ("pdf",)


def detect_image_type(stream) -> str:
    """Return 'jpg' | 'png' based on magic bytes ('' when unknown).

    The stream position is rewound before returning.
    """
    head = stream.read(8)
    stream.seek(0)
    if head[:3] == b"\xff\xd8\xff":
        return "jpg"
    if head == b"\x89PNG\r\n\x1a\n":
        return "png"
    stream.seek(0)
    return ""


def _remove_existing(dir_path: str, base_name: str, extensions) -> None:
    """Remove every existing file for this base name across extensions."""
    for ext in extensions:
        candidate = os.path.join(
            dir_path, secure_filename(f"{base_name}.{ext}")
        )
        if os.path.exists(candidate):
            os.remove(candidate)


def save_image(file_storage, target_dir: str, base_name: str,
               max_bytes: int = MAX_IMAGE_BYTES) -> str:
    """Validate and store an uploaded image privately.

    Returns the stored bare filename. Raises FileStorageError with reason
    'empty' | 'size' | 'type' on invalid input.
    """
    if file_storage is None or not file_storage.filename:
        raise FileStorageError("empty")

    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > max_bytes:
        raise FileStorageError("size")
    if size == 0:
        raise FileStorageError("empty")

    ext = detect_image_type(file_storage.stream)
    if not ext:
        raise FileStorageError("type")

    os.makedirs(target_dir, exist_ok=True)
    _remove_existing(target_dir, base_name, IMAGE_EXTENSIONS)

    filename = secure_filename(f"{base_name}.{ext}")
    file_storage.save(os.path.join(target_dir, filename))
    return filename


def remove_image(dir_path: str, base_name: str,
                 extensions=IMAGE_EXTENSIONS) -> bool:
    """Delete any stored file for this base name; True when one was removed."""
    before = {ext: os.path.exists(
        os.path.join(dir_path, secure_filename(f"{base_name}.{ext}")))
        for ext in extensions}
    _remove_existing(dir_path, base_name, extensions)
    return any(before.values())


def resolve_private_file(base_dir: str, stored_value: str):
    """Resolve a stored bare filename inside a private directory.

    Traversal-proof: only the basename of the stored value is used, so the
    result can never escape base_dir. Returns None when no readable file
    exists.
    """
    if not stored_value:
        return None
    candidate = os.path.join(base_dir, os.path.basename(stored_value))
    return candidate if os.path.isfile(candidate) else None


# ── P1-D: public rulebook PDF support ─────────────────────────────────

def detect_pdf(stream) -> bool:
    """True when the stream starts with the '%PDF-' magic; rewinds."""
    head = stream.read(5)
    stream.seek(0)
    return head == b"%PDF-"


def save_pdf(file_storage, target_dir: str, base_name: str,
             max_bytes: int = MAX_PDF_BYTES) -> str:
    """Validate and store an uploaded PDF.

    Same hardening contract as save_image (magic-byte sniffing instead of
    trusting names/extension, server-generated secure filename, previous
    file replaced). Returns the stored bare filename; raises
    FileStorageError with reason 'empty' | 'size' | 'type'.
    """
    if file_storage is None or not file_storage.filename:
        raise FileStorageError("empty")

    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > max_bytes:
        raise FileStorageError("size")
    if size == 0:
        raise FileStorageError("empty")

    if not detect_pdf(file_storage.stream):
        raise FileStorageError("type")

    os.makedirs(target_dir, exist_ok=True)
    _remove_existing(target_dir, base_name, PDF_EXTENSIONS)

    filename = secure_filename(f"{base_name}.pdf")
    file_storage.save(os.path.join(target_dir, filename))
    return filename


def remove_pdf(dir_path: str, base_name: str) -> bool:
    """Delete any stored PDF for this base name; True when removed."""
    existed = any(
        os.path.exists(os.path.join(
            dir_path, secure_filename(f"{base_name}.{ext}")))
        for ext in PDF_EXTENSIONS
    )
    _remove_existing(dir_path, base_name, PDF_EXTENSIONS)
    return existed
