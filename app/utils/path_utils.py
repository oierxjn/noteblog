"""Utilities for converting between absolute and relative filesystem paths."""
from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlparse

from flask import current_app, has_app_context


def _project_root() -> str:
    """Return the project root directory as configured on the Flask app."""
    if has_app_context():
        project_root = current_app.config.get('PROJECT_ROOT')
        if project_root:
            return project_root

    return os.path.abspath(os.getenv('PROJECT_ROOT', os.getcwd()))


def is_external_path(value: Optional[str]) -> bool:
    """Return True if the string points to an external URL."""
    if not value:
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def normalize_separators(path: str) -> str:
    """Collapse duplicated separators and always use forward slashes."""
    return path.replace('\\', '/').replace('//', '/')


def to_project_relative_path(path: Optional[str]) -> Optional[str]:
    """Convert an absolute filesystem path into one relative to PROJECT_ROOT."""
    if not path or is_external_path(path):
        return path

    normalized = os.path.abspath(path)
    base = _project_root()
    try:
        relative = os.path.relpath(normalized, base)
    except ValueError:
        return normalize_separators(normalized)
    return normalize_separators(relative)


def to_absolute_project_path(path: Optional[str]) -> Optional[str]:
    """Convert the stored relative path back to an absolute filesystem path."""
    if not path or is_external_path(path):
        return path

    if os.path.isabs(path):
        return os.path.normpath(path)

    base = _project_root()
    return os.path.normpath(os.path.join(base, path))

def project_path(*parts: str) -> str:
    """Join arbitrary path parts to the configured project root."""
    base = _project_root()
    return os.path.join(base, *parts)
