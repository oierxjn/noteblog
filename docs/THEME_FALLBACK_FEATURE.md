# 主题回退机制

## 功能描述

Noteblog 现在支持主题回退机制。当当前激活的主题缺少某个页面模板时，系统会自动回退到 `default` 主题使用对应的模板。

## 工作原理

1. **模板查找顺序**：
   - 首先在当前激活的主题中查找请求的模板
   - 如果找不到，则自动在 `default` 主题中查找
   - 如果 `default` 主题中也没有，则返回模板未找到的错误

2. **回退条件**：
   - 当前主题不是 `default` 主题
   - 当前主题中不存在请求的模板文件
   - `default` 主题中存在对应的模板文件

3. **日志记录**：
   - 当发生回退时，系统会在日志中记录信息
   - 格式：`主题 {theme_name} 缺少模板 {template_name}，回退到default主题`

## 实现细节

### 修改的文件

- `app/services/theme_manager.py` - 主题管理器的 `render_template` 方法

### 核心代码逻辑

```python
# 如果当前主题没有该模板，尝试回退到default主题
if not os.path.exists(template_path):
    default_theme = Theme.query.filter_by(name='default').first()
    if default_theme and default_theme.name != self.current_theme.name:
        default_template_path = os.path.join(default_theme.install_path, 'templates', template_name)
        if os.path.exists(default_template_path):
            template_path = default_template_path
            current_app.logger.info(f"主题 {self.current_theme.name} 缺少模板 {template_name}，回退到default主题")
```

### 模板目录处理

当回退到 `default` 主题时，系统会自动使用 `default` 主题的模板目录来渲染模板，确保模板继承和包含正常工作。

## 使用场景

### 1. 自定义主题开发
开发者可以创建只包含部分模板的自定义主题，其他页面自动使用 `default` 主题的模板。

### 2. 主题兼容性
当新版本 Noteblog 添加新的页面时，旧版本的主题仍然可以正常工作，通过回退机制使用 `default` 主题的新模板。

### 3. 渐进式主题定制
用户可以逐步替换 `default` 主题的模板，而不需要一次性创建所有模板文件。

## 示例

假设有一个自定义主题 `my_theme`，只包含以下模板：
- `templates/index.html`
- `templates/base.html`

当用户访问以下页面时：
- `/` - 使用 `my_theme/templates/index.html`
- `/auth/login` - 回退到 `default/templates/auth/login.html`
- `/admin/dashboard` - 回退到 `default/templates/admin/dashboard.html`

## 注意事项

1. **性能考虑**：回退机制会进行额外的文件系统检查，但影响很小
2. **样式一致性**：回退的模板可能使用 `default` 主题的样式，需要确保CSS兼容性
3. **功能完整性**：回退的模板可能包含当前主题不支持的功能，需要测试兼容性

## 测试

系统包含了完整的测试用例来验证回退机制：
- 测试存在模板的正常渲染
- 测试不存在模板的回退行为
- 测试模板目录的正确切换

## 向后兼容性

此功能完全向后兼容，不会影响现有主题的正常工作。
