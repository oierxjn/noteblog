"""
Vercel Serverless Function 入口文件
用于将 Flask 应用部署到 Vercel
"""
import sys
import os
import tempfile
from urllib.parse import unquote
from flask import request

# --- 1. 环境和路径设置 ---
# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 为 Vercel 环境设置可写的临时目录
temp_dir = tempfile.gettempdir()
os.environ.setdefault('FLASK_INSTANCE_PATH', temp_dir)

# 数据库配置
database_url = os.getenv('DATABASE_URL')
if database_url:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    os.environ.setdefault('DATABASE_URL', database_url)

# 确保临时目录存在
os.makedirs(temp_dir, exist_ok=True)

# --- 2. 创建 Flask 应用实例 ---
from app import create_app, db
app = create_app()

# 如果设置了数据库URL，覆盖应用默认配置
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# --- 3. 定义初始化函数 ---
def initialize_app(flask_app):
    """
    在应用上下文中执行所有一次性初始化任务。
    这包括数据库、设置、管理员用户和插件/主题。
    """
    with flask_app.app_context():
        print("开始执行一次性应用初始化...")

        # --- 数据库初始化 ---
        try:
            db.create_all()
            print("数据库表创建成功")
        except Exception as e:
            print(f"数据库表创建失败: {e}")
            return # 如果数据库失败，则后续操作无法进行

        # --- 默认设置初始化 ---
        from app.models.setting import Setting
        default_settings = [
            ('site_title', 'Noteblog', 'string', '网站标题', True),
            ('site_description', '一个基于Flask的博客系统', 'string', '网站描述', True),
            # ... (其他设置项保持不变) ...
        ]
        try:
            for key, value, value_type, description, is_public in default_settings:
                if not Setting.query.filter_by(key=key).first():
                    setting = Setting(key, value, value_type=value_type, description=description, is_public=is_public)
                    db.session.add(setting)
            db.session.commit()
            print("默认设置初始化成功")
        except Exception as e:
            print(f"默认设置初始化失败: {e}")
            db.session.rollback()

        # --- 管理员用户创建 ---
        from app.models.user import User
        try:
            if not User.query.filter_by(is_admin=True).first():
                admin = User('admin', 'admin@example.com', 'admin123', display_name='管理员', is_admin=True, is_active=True)
                db.session.add(admin)
                db.session.commit()
                print("管理员用户创建成功")
        except Exception as e:
            print(f"管理员用户创建失败: {e}")
            db.session.rollback()

        # --- 插件和主题初始化 (关键步骤) ---
        try:
            from app.services.plugin_manager import plugin_manager
            from app.services.theme_manager import theme_manager
            plugin_manager.init_app(flask_app)
            theme_manager.init_app(flask_app)
            print("插件和主题系统初始化成功")
        except Exception as e:
            print(f"插件和主题系统初始化失败: {e}")

        print("应用初始化完成。")

# --- 4. 注册请求处理钩子 ---
@app.before_request
def handle_url_encoding():
    """处理URL编码问题，这个需要在每个请求前执行"""
    if request.path and '%' in request.path:
        decoded_path = unquote(request.path)
        if decoded_path != request.path:
            request.environ['PATH_INFO'] = decoded_path

# --- 5. 执行一次性初始化 ---
# 这段代码只在模块被Python解释器加载时执行一次。
initialize_app(app)

# --- 6. 导出 WSGI 应用 ---
# Vercel 会自动调用这个应用来处理请求
application = app