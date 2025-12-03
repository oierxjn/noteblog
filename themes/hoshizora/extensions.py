"""Hoshizora 主题扩展入口，挂载自定义 Blueprint 与页面。"""
from __future__ import annotations

from flask import Blueprint, jsonify
from flask_login import login_required

from app.services.theme_manager import ThemeExtensionBase, theme_manager


class HoshizoraThemeExtension(ThemeExtensionBase):
    """Hoshizora 主题扩展实现。"""

    def __init__(self) -> None:
        super().__init__(
            theme_name="hoshizora",
            display_name="Hoshizora",
            version="1.0.0",
            description="Hoshizora主题扩展",
        )
        self._register_admin_blueprint()
        self._register_custom_pages()

    def _register_admin_blueprint(self) -> None:
        blueprint = Blueprint(
            "hoshizora_theme_extension",
            __name__,
            url_prefix="/admin/theme/hoshizora",
        )

        @blueprint.route("/status")
        @login_required
        def theme_status():  # pragma: no cover - simple JSON helper
            return jsonify(self._resolve_theme_info())

        self.add_blueprint(blueprint)

    def _register_custom_pages(self) -> None:
        self.add_custom_page(
            {
                "name": "hoshizora-gallery",
                "route": "/hoshizora/gallery",
                "template": "pages/gallery.html",
                "methods": ["GET"],
                "context": {
                    "page_title": "相册",
                    "page_description": "图片展示",
                },
            }
        )

    def _resolve_theme_info(self) -> dict[str, str]:
        stored_info = theme_manager.get_theme_info(self.theme_name) or {}
        defaults = self.get_info()
        return {
            "name": stored_info.get("display_name", defaults["display_name"]),
            "version": stored_info.get("version", defaults["version"]),
            "description": stored_info.get("description", defaults["description"]),
            "supports_customizer": stored_info.get(
                "supports_customizer", defaults["supports_customizer"]
            ),
        }


extension = HoshizoraThemeExtension()

THEME_BLUEPRINTS = extension.get_blueprints()
CUSTOM_PAGES = extension.get_custom_pages()


def register(app, theme_manager, theme):
    return extension.register(app=app, theme_manager=theme_manager, theme=theme)


def create_extension():
    return extension
