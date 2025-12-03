# Hoshizora Theme

一款简洁的深色系博客主题，带有渐变色彩和微妙动效。

## 特性

- **渐变配色**：可自定义的主色/副色/强调色三段式渐变
- **粒子背景**：可选的背景粒子动画
- **响应式布局**：移动端友好
- **完整模板**：首页、文章、分类/标签、归档、搜索、后台等

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
