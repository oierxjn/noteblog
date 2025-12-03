# 星空幻奏 · Hoshizora Theme

一款参照现代主题体系打造的二次元风格主题，灵感来自星空偶像舞台与赛博霓虹贴纸。提供完整页面模板、可配置的渐变色调、粒子背景、贴纸风侧边栏组件，以及登录/注册模态。

## 特性亮点

- ⚡ **多层霓虹**：主色/副色/星屑强调色三段式渐变，可自定义方向与纹理。
- 🌠 **角色式 Hero**：支持角色昵称、话题标签与 CTA 文案，营造番剧预告感。
- 🧩 **贴纸侧边栏**：内置资料卡、最新文章、分类、标签、友情链接的胶囊样式。
- 🛰️ **粒子与视差**：可选星屑粒子动画与滚动视差，增强沉浸式体验。
- 📱 **移动优化**：全站响应式布局，底部浮动操作条方便小屏浏览。
- 🧃 **全模板覆盖**：提供首页、文章、分类/标签、归档、搜索、错误页、后台、登录模态等。

## 目录结构

```
hoshizora/
├── extensions.py
├── README.md
├── screenshot.txt
├── static/
│   ├── css/hoshizora.css
│   └── js/hoshizora.js
├── templates/
│   ├── admin/base.html
│   ├── auth/login.html
│   ├── auth/change_password.html
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   ├── archives.html
│   ├── search.html
│   ├── categories.html
│   ├── category.html
│   ├── tags.html
│   ├── tag.html
│   ├── pages/gallery.html
│   ├── 404.html
│   └── 500.html
└── theme.json
```

## 自定义配置

所有可编辑字段都暴露在 `theme.json` 的 `config_schema` 中，可在 Noteblog 后台自定义。

| 配置键 | 说明 |
| --- | --- |
| `primary_color` / `secondary_color` / `accent_color` | 控制渐变与组件高亮色。 |
| `gradient_direction` | 调整背景渐变方向（to right / 120deg 等）。 |
| `background_texture` | 选择背景纹理（stars / grid / waves / none）。 |
| `hero_*` | Hero 区域的文案与角色昵称。 |
| `show_sidebar` / `sidebar_widgets` | 开关侧边栏与默认组件。 |
| `enable_parallax` / `enable_particle_field` | 视觉效果控制。 |
| `enable_dark_mode_toggle` | 是否展示深浅色切换按钮。 |
| `footer_text` | 页脚版权或附加说明。 |

## 开发提示

- 样式集中在 `static/css/hoshizora.css`，根据需要覆盖变量即可。
- 所有动画/交互逻辑在 `static/js/hoshizora.js`，保持无依赖原生实现。
- 若要扩展自定义页面，可以在 `extensions.py` 中追加 `add_custom_page`。
- 暴露的 Blueprint `/admin/theme/hoshizora/status` 方便探测主题状态。

欢迎基于本主题二次创作，记得在 Noteblog 仓库提 PR 分享你的魔改款！
