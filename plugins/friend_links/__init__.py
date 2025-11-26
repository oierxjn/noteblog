"""
友链插件
在侧边栏显示友链
"""
import os
from flask import current_app, render_template_string, Blueprint, request, jsonify
from app.services.plugin_manager import PluginBase
from .models import FriendLink


class FriendLinksPlugin(PluginBase):
    """友链插件类"""
    
    def __init__(self):
        super().__init__()
        self.name = 'friend_links'
        self.version = '1.0.0'
        self.description = '在侧边栏显示友链'
        self.author = 'Noteblog'
        
    def get_info(self):
        """返回插件信息"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'hooks': self.get_registered_hooks(),
            'filters': self.get_registered_filters()
        }
    
    def install(self):
        """插件安装时的操作"""
        current_app.logger.info(f"Installing {self.name} plugin")
        
        # 创建数据库表
        try:
            from app import db
            db.create_all()
            current_app.logger.info("Friend links table created successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to create friend links table: {e}")
            return False
        
        # 添加一些默认友链
        if FriendLink.query.count() == 0:
            default_links = [
                {
                    'name': 'GitHub',
                    'url': 'https://github.com',
                    'description': '全球最大的代码托管平台',
                    'logo': 'https://github.com/favicon.ico',
                    'sort_order': 100
                },
                {
                    'name': 'Python',
                    'url': 'https://python.org',
                    'description': 'Python官方网站',
                    'logo': 'https://python.org/favicon.ico',
                    'sort_order': 90
                },
                {
                    'name': 'Flask',
                    'url': 'https://flask.palletsprojects.com',
                    'description': 'Python Web框架',
                    'logo': 'https://flask.palletsprojects.com/favicon.ico',
                    'sort_order': 80
                }
            ]
            
            for link_data in default_links:
                link = FriendLink(**link_data)
                link.save()
        
        return True
    
    def uninstall(self):
        """插件卸载时的操作"""
        current_app.logger.info(f"Uninstalling {self.name} plugin")
        # 可选择是否删除数据库表
        return True
    
    def get_links(self):
        """获取友链列表"""
        config = self.get_config()
        max_links = config.get('max_links', 10)
        
        links = FriendLink.get_active_links()
        if len(links) > max_links:
            links = links[:max_links]
            
        return links
    
    def render_sidebar_widget(self):
        """渲染侧边栏友链组件"""
        config = self.get_config()
        
        # 只有在配置显示时才渲染
        if not config.get('show_in_sidebar', True):
            return ""
        
        # 渲染友链模板
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'sidebar.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        context = {
            'friend_links': {
                'title': config.get('title', '友情链接'),
                'links': self.get_links(),
                'open_new_window': config.get('open_new_window', True),
                'show_description': config.get('show_description', False)
            }
        }
        
        # 使用插件管理器的模板渲染方法，提供Flask上下文
        html_content = current_app.plugin_manager.render_plugin_template(
            self.name, template_content, context
        )
        
        # 注册 JavaScript 和 CSS 加载钩子
        self._register_assets()
        
        return html_content
    
    def _register_assets(self):
        """注册资源文件（CSS 和 JavaScript）"""
        # 注册 CSS 到 head 钩子
        if hasattr(current_app, 'plugin_manager'):
            current_app.plugin_manager.register_template_hook(
                'head_assets',
                lambda: f'<link rel="stylesheet" href="/static/plugins/friend_links/css/friend_links.css">',
                priority=10,
                plugin_name=self.name
            )
            
            # 注册 JavaScript 到 scripts 钩子
            current_app.plugin_manager.register_template_hook(
                'scripts_assets',
                self._get_script_content,
                priority=10,
                plugin_name=self.name
            )
    
    def _get_script_content(self):
        """获取 JavaScript 内容"""
        # 等待 Vue 应用初始化完成后再加载友情链接功能
        return '''
<script>
// 等待Vue应用初始化完成后再加载友情链接功能
(function() {
    // 检查Vue应用是否已经挂载
    function waitForVueApp() {
        if (window._noteblog_app && document.getElementById('app').__vue__) {
            // Vue应用已挂载，加载友情链接功能
            loadFriendLinksScript();
        } else {
            // Vue应用未挂载，等待一段时间后重试
            setTimeout(waitForVueApp, 100);
        }
    }
    
    // 动态加载友情链接脚本
    function loadFriendLinksScript() {
        // 检查是否已经加载过
        if (document.getElementById('friend-links-script')) {
            return;
        }
        
        const script = document.createElement('script');
        script.id = 'friend-links-script';
        script.src = '/static/plugins/friend_links/js/friend_links.js';
        script.onload = function() {
            // 脚本加载完成后初始化友情链接功能
            if (window.FriendLinks && typeof window.FriendLinks.init === 'function') {
                window.FriendLinks.init();
                window.FriendLinks.adjustLayout();
                window.FriendLinks.watchTheme();
                window.FriendLinks.initLazyLoading();
            }
        };
        document.head.appendChild(script);
    }
    
    // 开始等待Vue应用
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', waitForVueApp);
    } else {
        waitForVueApp();
    }
})();
</script>
        '''
    
    def register_hooks(self):
        """注册插件钩子"""
        # 注册侧边栏底部钩子
        if hasattr(current_app, 'plugin_manager'):
            current_app.plugin_manager.register_template_hook(
                'sidebar_bottom', 
                self.render_sidebar_widget, 
                priority=10, 
                plugin_name=self.name
            )


# 插件入口点
def create_plugin():
    """创建插件实例"""
    return FriendLinksPlugin()


# 创建蓝图
friend_links_bp = Blueprint('friend_links', __name__, 
                           template_folder='templates',
                           static_folder='static')


@friend_links_bp.route('/plugins/friend_links/admin')
def admin_page():
    """插件的管理页面"""
    from flask import render_template_string
    
    template = """
    <style>
    .friend-links-admin {
        font-family: "Segoe UI", Arial, sans-serif;
        color: #303133;
    }
    .friend-links-admin .admin-card {
        background: #fff;
        border: 1px solid #ebeef5;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    .friend-links-admin .card-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 24px;
    }
    .friend-links-admin .card-header h2 {
        font-size: 20px;
        margin: 0;
    }
    .friend-links-admin .card-header .subtitle {
        margin: 4px 0 0;
        color: #909399;
        font-size: 13px;
    }
    .friend-links-admin .btn-primary {
        background: #409eff;
        color: #fff;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    .friend-links-admin .btn-primary:hover {
        background: #66b1ff;
    }
    .friend-links-admin .btn-primary:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
    .friend-links-admin .config-form {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-bottom: 24px;
    }
    .friend-links-admin .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px 24px;
    }
    .friend-links-admin .form-row {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .friend-links-admin .form-row label {
        font-weight: 600;
        color: #606266;
    }
    .friend-links-admin .form-row input[type="text"],
    .friend-links-admin .form-row input[type="number"] {
        padding: 8px 12px;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        font-size: 14px;
        color: #303133;
    }
    .friend-links-admin .form-row input[type="text"]:focus,
    .friend-links-admin .form-row input[type="number"]:focus {
        outline: none;
        border-color: #409eff;
        box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.15);
    }
    .friend-links-admin .form-row-switch {
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
    .friend-links-admin .switch {
        position: relative;
        display: inline-block;
        width: 44px;
        height: 22px;
    }
    .friend-links-admin .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    .friend-links-admin .switch-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #dcdfe6;
        transition: 0.3s;
        border-radius: 22px;
    }
    .friend-links-admin .switch-slider:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 2px;
        bottom: 2px;
        background: white;
        transition: 0.3s;
        border-radius: 50%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    .friend-links-admin .switch input:checked + .switch-slider {
        background: #409eff;
    }
    .friend-links-admin .switch input:checked + .switch-slider:before {
        transform: translateX(22px);
    }
    .friend-links-admin .links-table {
        width: 100%;
        border-collapse: collapse;
        border: 1px solid #ebeef5;
        border-radius: 6px;
        overflow: hidden;
        background: #fff;
    }
    .friend-links-admin .links-table th,
    .friend-links-admin .links-table td {
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid #ebeef5;
        font-size: 14px;
    }
    .friend-links-admin .links-table tbody tr:hover {
        background: #f5f7fa;
    }
    .friend-links-admin .actions {
        display: flex;
        gap: 12px;
    }
    .friend-links-admin .btn-text {
        background: none;
        border: none;
        color: #409eff;
        cursor: pointer;
        padding: 0;
        font-size: 14px;
    }
    .friend-links-admin .btn-text:hover {
        text-decoration: underline;
    }
    .friend-links-admin .btn-danger {
        color: #f56c6c;
    }
    .friend-links-admin .empty-row {
        text-align: center;
        padding: 24px;
        color: #909399;
        font-size: 14px;
    }
    .friend-links-admin .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.35);
        align-items: center;
        justify-content: center;
        z-index: 2000;
        padding: 16px;
    }
    .friend-links-admin .modal-dialog {
        background: #fff;
        border-radius: 8px;
        width: 480px;
        max-width: 100%;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    }
    .friend-links-admin .modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 24px;
        border-bottom: 1px solid #ebeef5;
    }
    .friend-links-admin .modal-title {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
    }
    .friend-links-admin .modal-close {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #909399;
    }
    .friend-links-admin .modal-body {
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    .friend-links-admin .modal-body .form-row {
        margin: 0;
    }
    .friend-links-admin .modal-body input,
    .friend-links-admin .modal-body textarea {
        width: 100%;
    }
    .friend-links-admin .modal-body textarea {
        resize: vertical;
        min-height: 80px;
    }
    .friend-links-admin .modal-footer {
        padding: 16px 24px 24px;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        border-top: 1px solid #ebeef5;
    }
    .friend-links-admin .btn-secondary {
        background: #fff;
        border: 1px solid #dcdfe6;
        color: #606266;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
    }
    .friend-links-admin .btn-secondary:hover {
        border-color: #c6e2ff;
        color: #409eff;
    }
    .friend-links-admin .help-text {
        font-size: 12px;
        color: #a0a0a0;
    }
    </style>
    <div class="friend-links-admin" id="friend-links-admin">
        <div class="admin-card">
            <div class="card-header">
                <div>
                    <h2>友情链接管理</h2>
                    <p class="subtitle">自定义在站点侧边栏展示的优质外部链接</p>
                </div>
                <button type="button" class="btn-primary" onclick="showAddDialog()">+ 添加链接</button>
            </div>
            <div class="card-body">
                <form id="config-form" class="config-form" onsubmit="return false;">
                    <div class="form-grid">
                        <div class="form-row">
                            <label for="config-title">模块标题</label>
                            <input type="text" id="config-title" placeholder="友情链接" value="{{ config.title or '友情链接' }}">
                        </div>
                        <div class="form-row">
                            <label for="config-max-links">最大显示数量</label>
                            <input type="number" id="config-max-links" value="{{ config.max_links or 10 }}" min="1" max="50">
                            <span class="help-text">超出数量的链接将在前台被隐藏</span>
                        </div>
                        <div class="form-row form-row-switch">
                            <label for="config-show-in-sidebar">显示在侧边栏</label>
                            <label class="switch">
                                <input type="checkbox" id="config-show-in-sidebar" {% if config.show_in_sidebar != False %}checked{% endif %}>
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="form-row form-row-switch">
                            <label for="config-open-new-window">新窗口打开链接</label>
                            <label class="switch">
                                <input type="checkbox" id="config-open-new-window" {% if config.open_new_window != False %}checked{% endif %}>
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                        <div class="form-row form-row-switch">
                            <label for="config-show-description">显示链接描述</label>
                            <label class="switch">
                                <input type="checkbox" id="config-show-description" {% if config.show_description %}checked{% endif %}>
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                    </div>
                    <div>
                        <button type="button" class="btn-primary" onclick="saveConfig()">保存配置</button>
                    </div>
                </form>

                <table class="links-table">
                    <thead>
                        <tr>
                            <th style="width: 20%;">网站名称</th>
                            <th style="width: 30%;">链接地址</th>
                            <th style="width: 30%;">描述</th>
                            <th style="width: 20%; text-align: right;">操作</th>
                        </tr>
                    </thead>
                    <tbody id="links-tbody">
                        <tr class="empty-row">
                            <td colspan="4">暂无友链，请点击右上角“添加链接”。</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="modal" id="link-dialog" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-header">
                    <h3 class="modal-title" id="dialog-title">添加链接</h3>
                    <button type="button" class="modal-close" onclick="hideDialog()" aria-label="关闭">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-row">
                        <label for="link-name">网站名称 *</label>
                        <input type="text" id="link-name" placeholder="请输入网站名称" required>
                    </div>
                    <div class="form-row">
                        <label for="link-url">链接地址 *</label>
                        <input type="url" id="link-url" placeholder="请输入链接地址，例如 https://example.com" required>
                    </div>
                    <div class="form-row">
                        <label for="link-description">描述</label>
                        <textarea id="link-description" placeholder="请输入一句话描述（可选）"></textarea>
                    </div>
                    <div class="form-row">
                        <label for="link-logo">Logo</label>
                        <input type="url" id="link-logo" placeholder="请输入 Logo 图片地址（可选）">
                    </div>
                    <div class="form-row">
                        <label for="link-sort-order">排序权重</label>
                        <input type="number" id="link-sort-order" value="0" min="0" max="999">
                        <span class="help-text">数值越大显示越靠前</span>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn-secondary" onclick="hideDialog()">取消</button>
                    <button type="button" class="btn-primary" onclick="saveLink()">保存</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    (function() {
        let links = {{ links|tojson }};
        let editingId = null;

        function renderLinksTable() {
            const tbody = document.getElementById('links-tbody');
            if (!tbody) {
                return;
            }

            tbody.innerHTML = '';

            if (!Array.isArray(links) || links.length === 0) {
                const emptyRow = document.createElement('tr');
                emptyRow.className = 'empty-row';
                const emptyCell = document.createElement('td');
                emptyCell.colSpan = 4;
                emptyCell.textContent = '暂无友链，请点击右上角“添加链接”。';
                emptyRow.appendChild(emptyCell);
                tbody.appendChild(emptyRow);
                return;
            }

            links.forEach(function(link) {
                const tr = document.createElement('tr');

                const nameCell = document.createElement('td');
                nameCell.textContent = link.name || '';
                tr.appendChild(nameCell);

                const urlCell = document.createElement('td');
                const urlAnchor = document.createElement('a');
                urlAnchor.href = link.url || '#';
                urlAnchor.textContent = link.url || '';
                urlAnchor.target = '_blank';
                urlAnchor.rel = 'noopener noreferrer';
                urlAnchor.className = 'link-url';
                urlCell.appendChild(urlAnchor);
                tr.appendChild(urlCell);

                const descCell = document.createElement('td');
                descCell.textContent = link.description || '';
                tr.appendChild(descCell);

                const actionsCell = document.createElement('td');
                actionsCell.style.textAlign = 'right';
                const actionsWrapper = document.createElement('div');
                actionsWrapper.className = 'actions';

                const editButton = document.createElement('button');
                editButton.type = 'button';
                editButton.className = 'btn-text';
                editButton.textContent = '编辑';
                editButton.addEventListener('click', function() {
                    window.editLink(link.id);
                });

                const deleteButton = document.createElement('button');
                deleteButton.type = 'button';
                deleteButton.className = 'btn-text btn-danger';
                deleteButton.textContent = '删除';
                deleteButton.addEventListener('click', function() {
                    window.deleteLink(link.id);
                });

                actionsWrapper.appendChild(editButton);
                actionsWrapper.appendChild(deleteButton);
                actionsCell.appendChild(actionsWrapper);
                tr.appendChild(actionsCell);

                tbody.appendChild(tr);
            });
        }

        function getMessageInstance() {
            if (typeof window.ElMessage !== 'undefined') {
                return window.ElMessage;
            }
            if (window.ElementPlus && window.ElementPlus.ElMessage) {
                return window.ElementPlus.ElMessage;
            }
            if (typeof window.ELEMENT !== 'undefined' && window.ELEMENT.Message) {
                return window.ELEMENT.Message;
            }
            return null;
        }

        function showMessage(message, type) {
            const Message = getMessageInstance();
            if (Message) {
                try {
                    Message({ message: message, type: type, duration: 3000 });
                } catch (err) {
                    Message(message);
                }
            } else {
                alert(message);
            }
        }

        function loadLinks() {
            fetch('/plugins/friend_links/api/links', { credentials: 'same-origin' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        links = data.data;
                        renderLinksTable();
                    }
                })
                .catch(error => {
                    console.error('加载链接失败:', error);
                });
        }

        window.showAddDialog = function() {
            document.getElementById('dialog-title').textContent = '添加链接';
            document.getElementById('link-name').value = '';
            document.getElementById('link-url').value = '';
            document.getElementById('link-description').value = '';
            document.getElementById('link-logo').value = '';
            document.getElementById('link-sort-order').value = '0';
            editingId = null;
            const dialog = document.getElementById('link-dialog');
            dialog.style.display = 'flex';
            dialog.setAttribute('aria-hidden', 'false');
            setTimeout(function() {
                const nameField = document.getElementById('link-name');
                if (nameField) {
                    nameField.focus();
                }
            }, 50);
        };

        window.hideDialog = function() {
            const dialog = document.getElementById('link-dialog');
            dialog.style.display = 'none';
            dialog.setAttribute('aria-hidden', 'true');
        };

        window.editLink = function(id) {
            const link = links.find(function(l) { return l.id === id; });
            if (link) {
                document.getElementById('dialog-title').textContent = '编辑链接';
                document.getElementById('link-name').value = link.name;
                document.getElementById('link-url').value = link.url;
                document.getElementById('link-description').value = link.description || '';
                document.getElementById('link-logo').value = link.logo || '';
                document.getElementById('link-sort-order').value = link.sort_order || 0;
                editingId = id;
                const dialog = document.getElementById('link-dialog');
                dialog.style.display = 'flex';
                dialog.setAttribute('aria-hidden', 'false');
                setTimeout(function() {
                    const nameField = document.getElementById('link-name');
                    if (nameField) {
                        nameField.focus();
                        nameField.select();
                    }
                }, 50);
            }
        };

        window.saveLink = function() {
            const name = document.getElementById('link-name').value.trim();
            const url = document.getElementById('link-url').value.trim();

            if (!name || !url) {
                showMessage('请填写网站名称和链接地址', 'error');
                return;
            }

            const data = {
                name: name,
                url: url,
                description: document.getElementById('link-description').value.trim(),
                logo: document.getElementById('link-logo').value.trim(),
                sort_order: parseInt(document.getElementById('link-sort-order').value, 10) || 0
            };

            const apiUrl = editingId ? `/plugins/friend_links/api/links/${editingId}` : '/plugins/friend_links/api/links';
            const method = editingId ? 'PUT' : 'POST';

            fetch(apiUrl, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin',
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        showMessage(editingId ? '链接更新成功' : '链接添加成功', 'success');
                        loadLinks();
                        window.hideDialog();
                    } else {
                        showMessage(result.message || '操作失败', 'error');
                    }
                })
                .catch(() => {
                    showMessage('网络错误', 'error');
                });
        };

        window.deleteLink = function(id) {
            if (!confirm('确定要删除这个链接吗？')) {
                return;
            }

            fetch(`/plugins/friend_links/api/links/${id}`, {
                method: 'DELETE',
                credentials: 'same-origin'
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        showMessage('链接删除成功', 'success');
                        loadLinks();
                    } else {
                        showMessage(result.message || '删除失败', 'error');
                    }
                })
                .catch(() => {
                    showMessage('网络错误', 'error');
                });
        };

        window.saveConfig = function() {
            const config = {
                title: document.getElementById('config-title').value.trim(),
                show_in_sidebar: document.getElementById('config-show-in-sidebar').checked,
                max_links: parseInt(document.getElementById('config-max-links').value, 10) || 10,
                open_new_window: document.getElementById('config-open-new-window').checked,
                show_description: document.getElementById('config-show-description').checked
            };

            fetch('/plugins/friend_links/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin',
                body: JSON.stringify(config)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        showMessage('配置保存成功', 'success');
                    } else {
                        showMessage(result.message || '配置保存失败', 'error');
                    }
                })
                .catch(() => {
                    showMessage('网络错误', 'error');
                });
        };

        renderLinksTable();
        loadLinks();
    })();
    </script>
    """
    
    # 延迟获取插件实例，避免在蓝图注册时访问current_app
    try:
        plugin = current_app.plugin_manager.get_plugin('friend_links')
        if plugin:
            config = plugin.get_config()
            links = [link.to_dict() for link in FriendLink.get_all_links()]
            return render_template_string(template, config=config, links=links)
        else:
            return "插件未找到", 404
    except Exception as e:
        current_app.logger.error(f"获取友链插件失败: {e}")
        return f"插件加载失败: {str(e)}", 500


@friend_links_bp.route('/plugins/friend_links/api/config', methods=['POST'])
def api_config():
    """API：保存配置"""
    try:
        plugin = current_app.plugin_manager.get_plugin('friend_links')
        if not plugin:
            return jsonify({'success': False, 'message': '插件未找到'})
        
        config_data = request.get_json()
        plugin.set_config(config_data)
        return jsonify({'success': True, 'message': '配置保存成功'})
    except Exception as e:
        current_app.logger.error(f"保存友链配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@friend_links_bp.route('/plugins/friend_links/api/links', methods=['GET', 'POST'])
def api_links():
    """API：管理链接"""
    try:
        plugin = current_app.plugin_manager.get_plugin('friend_links')
        if not plugin:
            return jsonify({'success': False, 'message': '插件未找到'})
        
        if request.method == 'GET':
            # 获取链接列表（后台不限制数量）
            links = [link.to_dict() for link in FriendLink.get_all_links()]
            return jsonify({'success': True, 'data': links})
        
        elif request.method == 'POST':
            # 添加新链接
            data = request.get_json()
            link = FriendLink(
                name=data.get('name'),
                url=data.get('url'),
                description=data.get('description', ''),
                logo=data.get('logo', ''),
                sort_order=data.get('sort_order', 0)
            )
            
            if link.save():
                return jsonify({'success': True, 'message': '链接添加成功'})
            else:
                return jsonify({'success': False, 'message': '链接添加失败'})
    except Exception as e:
        current_app.logger.error(f"管理友链失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@friend_links_bp.route('/plugins/friend_links/api/links/<int:link_id>', methods=['PUT', 'DELETE'])
def api_link_detail(link_id):
    """API：管理单个链接"""
    try:
        plugin = current_app.plugin_manager.get_plugin('friend_links')
        if not plugin:
            return jsonify({'success': False, 'message': '插件未找到'})
        
        link = FriendLink.get_by_id(link_id)
        if not link:
            return jsonify({'success': False, 'message': '链接不存在'})
        
        if request.method == 'PUT':
            # 更新链接
            data = request.get_json()
            link.name = data.get('name', link.name)
            link.url = data.get('url', link.url)
            link.description = data.get('description', link.description)
            link.logo = data.get('logo', link.logo)
            link.sort_order = data.get('sort_order', link.sort_order)
            
            if link.save():
                return jsonify({'success': True, 'message': '链接更新成功'})
            else:
                return jsonify({'success': False, 'message': '链接更新失败'})
        
        elif request.method == 'DELETE':
            # 删除链接
            if link.delete():
                return jsonify({'success': True, 'message': '链接删除成功'})
            else:
                return jsonify({'success': False, 'message': '链接删除失败'})
    except Exception as e:
        current_app.logger.error(f"管理友链详情失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
