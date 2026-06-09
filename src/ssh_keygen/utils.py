"""Shared utilities."""

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """Resolve path for both dev and PyInstaller builds."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent.parent))
    return base_path / relative_path


def sanitize_filename(filename: str) -> str:
    """Remove invalid filename characters."""
    invalid_chars = '<>:"/\\|?*'

    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    sanitized = sanitized.strip().strip(".")

    if not sanitized or sanitized.strip("_") == "":
        sanitized = "id_ssh"

    return sanitized
