"""Aurora 主题扩展入口：后台接口 + 自定义页面定义。"""
from flask import Blueprint, jsonify
from flask_login import login_required

from app.services.theme_manager import theme_manager

extension_bp = Blueprint('aurora_theme_extension', __name__, url_prefix='/admin/theme/aurora')


@extension_bp.route('/status')
@login_required
def theme_status():
    """返回当前主题的基础信息，便于在后台展示。"""
    info = theme_manager.get_theme_info('aurora') or {}
    return jsonify({
        'name': info.get('display_name', 'Aurora'),
        'version': info.get('version', 'unknown'),
        'description': info.get('description', ''),
        'supports_customizer': info.get('supports_customizer', True)
    })


# ThemeManager 会自动检测 THEME_BLUEPRINTS 与 CUSTOM_PAGES
THEME_BLUEPRINTS = [extension_bp]

CUSTOM_PAGES = [
    {
        'name': 'aurora-timeline',
        'route': '/aurora/timeline',
        'template': 'pages/timeline.html',
        'methods': ['GET'],
        'context': {
            'page_title': 'Aurora 时间线'
        }
    }
]
