"""Normalize stored filesystem paths to project-relative values."""
from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app, db
from app.models.plugin import Plugin
from app.models.theme import Theme
from app.utils import path_utils


def normalize_plugin_paths() -> int:
    changed = 0
    for plugin in Plugin.query.all():
        absolute = plugin.install_path
        relative = path_utils.to_project_relative_path(absolute)
        if relative and plugin.install_path_relative != relative:
            plugin._install_path = relative  # pylint: disable=protected-access
            changed += 1
    return changed


def normalize_theme_paths() -> int:
    changed = 0
    for theme in Theme.query.all():
        absolute = theme.install_path
        relative = path_utils.to_project_relative_path(absolute)
        if relative and theme.install_path_relative != relative:
            theme._install_path = relative  # pylint: disable=protected-access
            changed += 1
    return changed


def main() -> None:
    app = create_app()
    with app.app_context():
        plugin_changes = normalize_plugin_paths()
        theme_changes = normalize_theme_paths()
        if plugin_changes or theme_changes:
            db.session.commit()
        print(f"Normalized plugin paths: {plugin_changes}")
        print(f"Normalized theme paths: {theme_changes}")


if __name__ == '__main__':
    main()
