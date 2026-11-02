"""Shared utilities."""

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """Resolve path for both dev and PyInstaller builds."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base_path / relative_path


def sanitize_filename(filename: str) -> str:
    """Replace characters Windows does not allow in file names, falling back to 'id_ssh'."""
    sanitized = filename
    for char in '<>:"/\\|?*':
        sanitized = sanitized.replace(char, "_")
    sanitized = sanitized.strip().strip(".")
    return sanitized if sanitized.strip("_") else "id_ssh"
