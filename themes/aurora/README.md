# Aurora 主题

Aurora 是一个现代化的 noteblog 主题，灵感来自北极光的美妙色彩。它采用渐变色彩设计和流畅动画，为用户提供优雅的阅读体验。

## 🌟 特性

### 🎨 设计特色
- **渐变色彩系统** - 灵感来自北极光的美丽渐变
- **深色模式支持** - 平滑的主题切换动画
- **响应式设计** - 完美适配各种设备尺寸
- **卡片式布局** - 现代化的内容展示方式
- **流畅动画** - 精心设计的微交互效果

### 📱 功能特性
- **高级搜索** - 实时搜索建议和关键词高亮
- **社交分享** - 内置分享到各大社交平台
- **评论系统** - 集成评论功能
- **数学公式** - 支持 KaTeX 数学公式渲染
- **代码高亮** - 语法高亮显示
- **图片懒加载** - 优化页面加载性能
- **阅读进度** - 文章阅读进度指示器
- **目录导航** - 长文章自动生成目录
- **相关文章** - 智能推荐相关内容

### 🏗️ 技术特性
- **SEO 优化** - 良好的搜索引擎优化
- **性能优化** - 最小化依赖，快速加载
- **可定制设置** - 丰富的主题配置选项
- **插件支持** - 完整的插件钩子系统
- **无障碍支持** - 遵循 WCAG 无障碍标准

## 📁 文件结构

```
aurora/
├── theme.json              # 主题配置文件
├── screenshot.txt           # 主题说明
├── README.md               # 主题文档
├── static/
│   ├── css/
│   │   └── aurora.css      # 主样式文件
│   ├── js/
│   │   └── aurora.js       # 主脚本文件
│   └── images/             # 图片资源目录
├── extensions.py           # 主题扩展入口（后台接口 + 自定义页面）
└── templates/
    ├── base.html           # 基础模板
    ├── index.html          # 首页模板
    ├── post.html           # 文章页模板
    ├── search.html         # 搜索页模板
    ├── categories.html     # 分类页模板
    ├── tags.html           # 标签页模板
    ├── archives.html       # 归档页模板
    ├── pages/
    │   └── timeline.html   # 自定义页面示例
    ├── 404.html            # 404错误页模板
    ├── 500.html            # 500错误页模板
    ├── admin/
    │   └── base.html       # 管理后台基础模板
    └── auth/
        └── login.html      # 登录页模板
```

## 🎨 主题配置

Aurora 主题提供丰富的配置选项，可以通过 `theme.json` 文件进行自定义：

### 颜色配置
- `primary_color` - 主色调
- `secondary_color` - 次要色调
- `accent_color` - 强调色
- `background_color` - 背景色
- `text_color` - 文字颜色

### 布局配置
- `sidebar_position` - 侧边栏位置
- `card_style` - 卡片样式
- `animation_enabled` - 动画开关
- `dark_mode_enabled` - 深色模式开关

### 功能配置
- `search_enabled` - 搜索功能
- `social_sharing` - 社交分享
- `comment_system` - 评论系统
- `math_support` - 数学公式支持

## 🚀 安装使用

1. 将 `aurora` 文件夹复制到 `themes/` 目录下
2. 在管理后台的"主题管理"中选择 Aurora 主题
3. 根据需要调整主题配置选项
4. 保存设置并刷新网站

## 🛠️ 自定义开发

### 主题扩展入口（extensions.py）
`extensions.py` 是 Aurora 的统一扩展文件：

```python
THEME_BLUEPRINTS = [extension_bp]

CUSTOM_PAGES = [
    {
        "name": "aurora-timeline",
        "route": "/aurora/timeline",
        "template": "pages/timeline.html",
        "context": {"page_title": "Aurora 时间线"}
    }
]
```

- `THEME_BLUEPRINTS`：注册后台接口（例如 `/admin/theme/aurora/status`）。
- `CUSTOM_PAGES`：声明自定义前端页面，Noteblog 会自动为其添加路由并渲染指定模板。

如需更多页面或 API，只需在 `extensions.py` 中继续添加 Blueprint 路由或新的 `CUSTOM_PAGES` 项目。

### CSS 变量
主题使用 CSS 变量系统，方便自定义颜色和样式：

```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --background-color: #ffffff;
    --text-primary: #2d3748;
    --text-secondary: #718096;
    /* 更多变量... */
}
```

### JavaScript API
主题提供 JavaScript API 用于扩展功能：

```javascript
// 主题切换
AuroraTheme.toggleDarkMode();

// 搜索功能
AuroraTheme.performSearch(query);

// 动画控制
AuroraTheme.enableAnimations(true);
```

### 模板钩子
主题支持多种模板钩子，方便插件扩展：

```html
<!-- 头部钩子 -->
{% hook 'head' %}

<!-- 侧边栏钩子 -->
{% hook 'sidebar' %}

<!-- 页脚钩子 -->
{% hook 'footer' %}
```

## 📱 响应式断点

- **移动设备**: < 768px
- **平板设备**: 768px - 1024px
- **桌面设备**: > 1024px

## 🌐 浏览器支持

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个主题。

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 查看文档和 FAQ
2. 搜索已有的 Issue
3. 创建新的 Issue 描述问题
4. 联系主题开发者

---

**Aurora Theme** - 让您的博客如北极光般绚丽多彩 ✨
