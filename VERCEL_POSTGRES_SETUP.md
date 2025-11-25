# Vercel Postgres 数据库设置指南

## 概述

本指南将帮助您设置 Vercel Postgres 数据库，解决 Noteblog 在 Vercel 部署中的数据持久化问题。

## 为什么选择 Vercel Postgres？

- **数据持久化**：数据永久存储，不会因为函数重启而丢失
- **高性能**：专为 serverless 环境优化的 PostgreSQL 数据库
- **免费额度**：提供充足的免费存储和连接额度
- **自动备份**：内置自动备份和恢复功能
- **安全性**：内置 SSL 加密和连接池

## 设置步骤

### 1. 创建 Vercel Postgres 数据库

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择您的项目
3. 进入 **Storage** 选项卡
4. 点击 **Create Database**
5. 选择 **Postgres** 数据库
6. 选择区域（建议选择离用户最近的区域）
7. 点击 **Create**

### 2. 获取数据库连接信息

创建完成后，Vercel 会自动为您的项目设置以下环境变量：

- `POSTGRES_URL` - 完整的数据库连接字符串
- `POSTGRES_PRISMA_URL` - Prisma 优化的连接字符串
- `POSTGRES_URL_NON_POOLING` - 非连接池的连接字符串
- `POSTGRES_USER` - 数据库用户名
- `POSTGRES_HOST` - 数据库主机
- `POSTGRES_PASSWORD` - 数据库密码
- `POSTGRES_DATABASE` - 数据库名称

### 3. 配置应用环境变量

在 Vercel 项目设置中，添加以下环境变量：

```
DATABASE_URL = ${POSTGRES_URL}
SECRET_KEY = your-secret-key-here
FLASK_ENV = production
SKIP_PLUGIN_INIT = 1
PYTHONPATH = /var/task
```

**重要**：将 `DATABASE_URL` 设置为 `${POSTGRES_URL}`，这样它会自动使用 Vercel Postgres 的连接字符串。

### 4. 更新依赖

确保您的 `requirements.txt` 包含 PostgreSQL 驱动：

```
psycopg2-binary
```

（已在本次更新中添加）

### 5. 部署应用

```bash
# 部署到生产环境
vercel --prod
```

## 验证部署

### 1. 检查数据库连接

部署完成后，访问您的应用，查看函数日志确认数据库连接：

```bash
vercel logs
```

您应该看到类似以下的日志：
```
使用环境变量中的数据库配置: postgres://***
数据库表创建完成
默认设置初始化成功
管理员用户创建成功
```

### 2. 测试数据持久化

1. 访问 `/admin` 并使用 `admin/admin123` 登录
2. 创建一些测试数据（文章、分类等）
3. 等待几分钟让函数进入休眠状态
4. 重新访问应用，确认数据仍然存在

## 数据库管理

### 查看数据库

在 Vercel Dashboard 中：
1. 进入 **Storage** 选项卡
2. 点击您的 Postgres 数据库
3. 使用内置的查询工具查看和管理数据

### 备份和恢复

Vercel Postgres 自动提供：
- 每日自动备份
- 点位时间恢复（PITR）
- 手动备份功能

### 连接限制

免费计划的限制：
- 60 个连接
- 512MB 存储
- 10GB 月度传输

对于大多数博客应用来说，这些限制是足够的。

## 故障排除

### 常见问题

1. **连接超时**
   - 检查 `DATABASE_URL` 是否正确设置
   - 确认包含 `?sslmode=require` 参数

2. **权限错误**
   - 确认数据库用户有足够的权限
   - 检查表是否正确创建

3. **性能问题**
   - 使用连接池（`POSTGRES_URL` 已包含）
   - 优化数据库查询
   - 考虑添加索引

### 调试技巧

1. **查看详细日志**：
   ```bash
   vercel logs --follow
   ```

2. **测试数据库连接**：
   在 Vercel Dashboard 中使用查询工具执行：
   ```sql
   SELECT version();
   ```

3. **检查环境变量**：
   确认所有必需的环境变量都已正确设置

## 迁移现有数据

如果您之前使用 SQLite 并有现有数据：

1. 导出 SQLite 数据
2. 转换数据格式
3. 使用 Vercel Dashboard 的查询工具导入数据
4. 或者编写迁移脚本

## 最佳实践

1. **安全性**
   - 使用强密码作为 `SECRET_KEY`
   - 定期轮换数据库凭据
   - 启用 SSL 连接（已默认启用）

2. **性能优化**
   - 使用适当的索引
   - 避免长时间运行的查询
   - 实施适当的缓存策略

3. **监控**
   - 监控数据库连接数
   - 跟踪存储使用情况
   - 设置告警通知

## 成本考虑

Vercel Postgres 的免费计划适用于：
- 个人博客
- 小型项目
- 开发和测试

如果需要更多资源，可以考虑升级到付费计划。

## 总结

通过使用 Vercel Postgres，您的 Noteblog 应用将获得：
- ✅ 数据持久化
- ✅ 高性能
- ✅ 自动备份
- ✅ 安全连接
- ✅ 易于管理

这彻底解决了之前使用内存 SQLite 导致的数据丢失问题。
