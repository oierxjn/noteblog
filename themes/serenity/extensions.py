"""Serenity 主题扩展入口：提供后台接口与自定义页面声明。"""
from flask import Blueprint, jsonify
from flask_login import login_required

from app.services.theme_manager import theme_manager

extension_bp = Blueprint("serenity_theme_extension", __name__, url_prefix="/admin/theme/serenity")


@extension_bp.route("/status")
@login_required
def theme_status():
    """返回 Serenity 主题的基本信息，便于后台展示。"""
    info = theme_manager.get_theme_info("serenity") or {}
    return jsonify(
        {
            "name": info.get("display_name", "Serenity"),
            "version": info.get("version", "unknown"),
            "description": info.get("description", ""),
            "supports_customizer": info.get("supports_customizer", True),
        }
    )


THEME_BLUEPRINTS = [extension_bp]

CUSTOM_PAGES = [
    {
        "name": "serenity-timeline",
        "route": "/serenity/timeline",
        "template": "pages/timeline.html",
        "methods": ["GET"],
        "context": {
            "page_title": "Serenity 时间线",
            "page_description": "用一页的篇幅，记录值得记住的每一次发布",
        },
    }
]
