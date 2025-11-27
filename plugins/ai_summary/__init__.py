"""
AI 摘要插件
首次访问文章时向大模型请求摘要并缓存，后续直接使用，支持后台强制重算与模型配置。
"""
import os
import json
import hashlib
from typing import Optional, Dict, Any, Tuple

from flask import current_app, Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

try:
    import requests
except Exception:  # 避免导入期失败
    requests = None

from app import db
from app.models.post import Post
from app.services.plugin_manager import PluginBase
from .models import PostAISummary


DEFAULT_ENDPOINT = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
DEFAULT_MODEL = 'GLM-4.5-Flash'


class AISummaryPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = 'ai_summary'
        self.version = '1.0.0'
        self.description = '为文章生成 AI 摘要并缓存'
        self.author = 'Noteblog'

    # -------- 安装/配置 --------
    def install(self):
        current_app.logger.info(f'Installing {self.name} plugin')
        try:
            db.create_all()
        except Exception as e:
            current_app.logger.error(f'创建表失败: {e}')
            return False

        # 初始化默认配置
        cfg = self.get_config() or {}
        if 'model' not in cfg:
            cfg['model'] = DEFAULT_MODEL
        if 'endpoint' not in cfg:
            cfg['endpoint'] = DEFAULT_ENDPOINT
        if 'temperature' not in cfg:
            cfg['temperature'] = 0.7
        if 'max_tokens' not in cfg:
            cfg['max_tokens'] = 300
        # api_key 由用户在后台填写
        self.set_config(cfg)
        return True

    def register_hooks(self):
        # 在文章详情上下文注入摘要（post_context 过滤器）
        if hasattr(current_app, 'plugin_manager'):
            current_app.plugin_manager.register_filter(
                'post_context', self._inject_summary_to_post_context, priority=10, accepted_args=2, plugin_name=self.name
            )
            current_app.plugin_manager.register_filter(
                'admin_post_editor_hooks',
                self._inject_admin_editor_hooks,
                priority=20,
                accepted_args=3,
                plugin_name=self.name
            )

    # -------- 过滤器：注入摘要 --------
    def _inject_summary_to_post_context(self, context: Dict[str, Any], post: Post) -> Dict[str, Any]:
        try:
            # 仅对普通文章生效
            if not post or getattr(post, 'post_type', 'post') != 'post':
                return context

            summary = self.get_cached_summary(post)

            # 将摘要注入 post_meta，显示在文章标题下方
            hooks = context.get('plugin_hooks') or {}
            hooks.setdefault('post_meta', [])
            hooks['post_meta'].append(self._render_summary_block(post_id=post.id, summary=summary))
            context['plugin_hooks'] = hooks
            return context
        except Exception as e:
            current_app.logger.error(f'注入AI摘要失败: {e}')
            return context

    def get_cached_summary(self, post: Post) -> Optional[str]:
        row = PostAISummary.query.filter_by(post_id=post.id).first()
        if row and row.summary:
            return row.summary
        return None

    def _render_summary_block(self, post_id: int, summary: Optional[str]) -> str:
        has_summary = bool(summary)
        state = 'ready' if has_summary else 'pending'
        body = summary if has_summary else 'AI 摘要生成中，通常几秒内完成…'
        script = '' if has_summary else self._pending_loader_script()
        return f'''
<section class="ai-summary" data-ai-summary data-post-id="{post_id}" data-state="{state}" style="margin-top:1.5rem;padding:1rem;border:1px solid var(--nb-border,#e5e7eb);border-radius:0.5rem;background:var(--nb-card,#fafafa)">
    <div style="font-weight:600;margin-bottom:0.5rem;display:flex;align-items:center;gap:.4rem">
        <span aria-hidden>🤖</span><span>AI 摘要</span>
    </div>
    <div data-ai-summary-body style="white-space:pre-wrap;line-height:1.7;color:var(--nb-text,#374151)">{body}</div>
    <div style="margin-top:.5rem;color:#9ca3af;font-size:.85em">首访生成，后台可强制重算</div>
</section>
{script}
'''

    def _pending_loader_script(self) -> str:
        return '''
<script>
(function() {
    function fetchSummary(block) {
        if (!block || block.dataset.loading === '1') {
            return;
        }
        var postId = block.getAttribute('data-post-id');
        if (!postId) {
            return;
        }
        var body = block.querySelector('[data-ai-summary-body]');
        block.dataset.loading = '1';
        block.dataset.state = 'loading';
        fetch('/plugins/ai_summary/api/public/summary/' + postId, {
            credentials: 'same-origin'
        })
            .then(function(res) {
                if (!res.ok) {
                    throw new Error('AI 摘要生成失败，请稍后重试');
                }
                return res.json();
            })
            .then(function(data) {
                if (!data || !data.success || !data.summary) {
                    throw new Error(data && data.message ? data.message : 'AI 摘要暂不可用');
                }
                block.dataset.state = 'ready';
                block.dataset.loading = '0';
                if (body) {
                    body.textContent = data.summary;
                }
            })
            .catch(function(err) {
                block.dataset.state = 'error';
                block.dataset.loading = '0';
                if (body) {
                    body.textContent = err && err.message ? err.message : 'AI 摘要暂不可用';
                }
            });
    }

    function initAISummaryBlocks() {
        var blocks = document.querySelectorAll('[data-ai-summary][data-state="pending"]');
        if (!blocks.length) {
            return;
        }
        blocks.forEach(fetchSummary);
    }

    if (window.__AISummaryLoaderInitialized) {
        initAISummaryBlocks();
        return;
    }
    window.__AISummaryLoaderInitialized = true;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAISummaryBlocks);
    } else {
        initAISummaryBlocks();
    }
})();
</script>
'''

    def _inject_admin_editor_hooks(self, hooks: Dict[str, Any], mode: str = 'create', post: Optional[Post] = None):
        hooks = hooks or {}
        try:
            hooks.setdefault('excerpt_tools', [])
            hooks.setdefault('scripts', [])

            toolbar_html = render_template('ai_summary_editor_tools.html', mode=mode, post=post)
            hooks['excerpt_tools'].append(toolbar_html)

            script_html = render_template('ai_summary_editor_scripts.html')
            # 避免重复注入脚本
            if script_html not in hooks['scripts']:
                hooks['scripts'].append(script_html)
            return hooks
        except Exception as exc:
            current_app.logger.error(f'注入AI摘要后台钩子失败: {exc}')
            return hooks

    # -------- 摘要生成与缓存 --------
    def get_or_create_summary(self, post: Post) -> str:
        # 查缓存
        row = PostAISummary.query.filter_by(post_id=post.id).first()
        if row and row.summary:
            return row.summary

        # 没有则生成
        summary, tokens = self._generate_summary(post)
        if not summary:
            return '（AI 摘要暂不可用）'

        # 保存
        try:
            if row is None:
                row = PostAISummary(post_id=post.id, model=self._get_model(), summary=summary, tokens_used=tokens)
                db.session.add(row)
            else:
                row.model = self._get_model()
                row.summary = summary
                row.tokens_used = tokens
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'保存AI摘要失败: {e}')
        return summary

    def _truncate(self, text: str, max_chars: int) -> str:
        if text is None:
            return ''
        return text if len(text) <= max_chars else text[:max_chars]

    def _get_cfg(self) -> Dict[str, Any]:
        cfg = self.get_config() or {}
        return cfg

    def _get_model(self) -> str:
        return (self._get_cfg().get('model') or DEFAULT_MODEL).strip()

    def _get_endpoint(self) -> str:
        ep = self._get_cfg().get('endpoint') or DEFAULT_ENDPOINT
        return ep.strip()

    def _get_api_key(self) -> Optional[str]:
        # 允许从环境变量覆盖（优先）
        env_key = os.getenv('BIGMODEL_API_KEY')
        if env_key:
            return env_key
        cfg = self._get_cfg()
        return (cfg.get('api_key') or '').strip()

    def _generate_summary(self, post: Post) -> Tuple[str, Optional[int]]:
        api_key = self._get_api_key()
        if not api_key:
            current_app.logger.warning('AI 摘要未配置 API Key')
            return '', None
        if requests is None:
            current_app.logger.warning('requests 未安装，无法请求大模型接口')
            return '', None

        model = self._get_model()
        endpoint = self._get_endpoint()
        temperature = float(self._get_cfg().get('temperature', 0.7))
        max_tokens = int(self._get_cfg().get('max_tokens', 300))

        # 构造提示词（控制长度）
        title = self._truncate(post.title or '', 120)
        content = self._truncate(post.content or '', 4000)
        system_prompt = '你是博客文章的总结助手，用不超过120字中文概括要点，保留关键词，避免赘述，不输出多余说明。'
        user_prompt = f'标题：{title}\n正文：\n{content}\n请输出一段中文摘要：'

        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': False
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        try:
            resp = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=30)
            if resp.status_code != 200:
                current_app.logger.error(f'AI 摘要请求失败 status={resp.status_code}, body={resp.text[:300]}')
                return '', None
            data = resp.json()
            # 兼容 OpenAI 风格返回
            content = None
            if isinstance(data, dict):
                if 'choices' in data and data['choices']:
                    msg = data['choices'][0].get('message') or {}
                    content = msg.get('content')
            if not content:
                current_app.logger.error(f'AI 摘要响应解析失败: {str(data)[:300]}')
                return '', None
            tokens_used = None
            if isinstance(data, dict) and 'usage' in data and isinstance(data['usage'], dict):
                tokens_used = data['usage'].get('total_tokens')
            # 清理结果
            summary = content.strip()
            return summary, tokens_used
        except Exception as e:
            current_app.logger.error(f'AI 摘要请求异常: {e}')
            return '', None

    def generate_preview_summary(self, title: str, content: str) -> Tuple[str, Optional[int]]:
        """为后台编辑器生成临时摘要，不落盘缓存"""
        pseudo_post = type('AISummaryPreviewPost', (), {})()
        pseudo_post.title = title or ''
        pseudo_post.content = content or ''
        pseudo_post.post_type = 'post'
        return self._generate_summary(pseudo_post)


# ------ 插件入口点 ------
def create_plugin():
    return AISummaryPlugin()


# ------ 蓝图与后台接口 ------
ai_summary_bp = Blueprint('ai_summary', __name__, template_folder='templates', static_folder='static')


@ai_summary_bp.route('/plugins/ai_summary/admin')
def admin_page():
    try:
        plugin = current_app.plugin_manager.get_plugin('ai_summary')
        if not plugin:
            return '插件未找到', 404
        
        config = plugin.get_config() or {}
        base_defaults = {
            'model': DEFAULT_MODEL,
            'endpoint': DEFAULT_ENDPOINT,
            'temperature': 0.7,
            'max_tokens': 300,
        }
        
        # 不回显密钥，并为模板填充默认值，确保所有值都是可序列化的
        safe_config = {
            'model': config.get('model') or base_defaults['model'],
            'endpoint': config.get('endpoint') or base_defaults['endpoint'],
            'temperature': config.get('temperature') or base_defaults['temperature'],
            'max_tokens': config.get('max_tokens') or base_defaults['max_tokens'],
        }
        
        return render_template('ai_summary_admin.html', config=safe_config)
    except Exception as e:
        current_app.logger.error(f'加载 AI 摘要后台失败: {e}')
        return f'插件加载失败: {str(e)}', 500


@ai_summary_bp.route('/plugins/ai_summary/api/config', methods=['POST'])
def save_config():
    try:
        plugin = current_app.plugin_manager.get_plugin('ai_summary')
        if not plugin:
            return jsonify({'success': False, 'message': '插件未找到'})
        data = request.get_json() or {}
        # 合并配置，api_key 可选更新
        cfg = plugin.get_config() or {}
        for key in ['model', 'endpoint', 'temperature', 'max_tokens']:
            if key in data:
                cfg[key] = data[key]
        if 'api_key' in data and data['api_key']:
            cfg['api_key'] = data['api_key']
        plugin.set_config(cfg)
        return jsonify({'success': True, 'message': '配置已保存'})
    except Exception as e:
        current_app.logger.error(f'保存配置失败: {e}')
        return jsonify({'success': False, 'message': str(e)})


@ai_summary_bp.route('/plugins/ai_summary/api/force/<int:post_id>', methods=['POST'])
def force_regenerate(post_id: int):
    try:
        # 删除缓存记录，下一次访问将自动重算
        row = PostAISummary.query.filter_by(post_id=post_id).first()
        if row:
            db.session.delete(row)
            db.session.commit()
        return jsonify({'success': True, 'message': '已标记重算'})
    except Exception as e:
        current_app.logger.error(f'强制重算失败: {e}')
        return jsonify({'success': False, 'message': str(e)})


@ai_summary_bp.route('/plugins/ai_summary/api/force_all', methods=['POST'])
def force_regenerate_all():
    try:
        deleted = PostAISummary.query.delete()
        db.session.commit()
        return jsonify({'success': True, 'message': f'已清空缓存（{deleted}）'})
    except Exception as e:
        current_app.logger.error(f'清空缓存失败: {e}')
        return jsonify({'success': False, 'message': str(e)})


@ai_summary_bp.route('/plugins/ai_summary/api/generate_preview', methods=['POST'])
@login_required
def generate_preview():
    try:
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': '权限不足'}), 403

        plugin = current_app.plugin_manager.get_plugin('ai_summary') if hasattr(current_app, 'plugin_manager') else None
        if not plugin:
            return jsonify({'success': False, 'message': '插件未加载'}), 500

        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()
        if not content:
            return jsonify({'success': False, 'message': '请先填写文章内容'}), 400

        summary, tokens = plugin.generate_preview_summary(title=title, content=content)
        if not summary:
            return jsonify({'success': False, 'message': 'AI 摘要暂不可用，请检查插件配置'}), 502

        return jsonify({'success': True, 'summary': summary, 'tokens_used': tokens})
    except Exception as e:
        current_app.logger.error(f'即时生成摘要失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@ai_summary_bp.route('/plugins/ai_summary/api/public/summary/<int:post_id>')
def fetch_public_summary(post_id: int):
    try:
        post = Post.query.filter_by(id=post_id, status='published').first()
        if not post or getattr(post, 'post_type', 'post') != 'post':
            return jsonify({'success': False, 'message': '文章不存在或未发布'}), 404

        plugin = current_app.plugin_manager.get_plugin('ai_summary') if hasattr(current_app, 'plugin_manager') else None
        if not plugin:
            return jsonify({'success': False, 'message': '插件未加载'}), 500

        summary = plugin.get_or_create_summary(post)
        if not summary:
            return jsonify({'success': False, 'message': 'AI 摘要暂不可用'}), 502

        return jsonify({'success': True, 'post_id': post_id, 'summary': summary})
    except Exception as e:
        current_app.logger.error(f'公开获取AI摘要失败: {e}')
        return jsonify({'success': False, 'message': 'AI 摘要暂不可用'}), 500
