# 电表监控系统部署指南

## 概述

本系统支持部署到 Railway 和 Zeabur 两个云平台。两个平台都提供免费套餐，适合个人项目使用。

## 部署前准备

### 1. 代码准备
确保你的代码已经推送到 GitHub 仓库，包含以下文件：
- `app.py` - 主应用文件
- `scraper.py` - 数据抓取模块
- `requirements.txt` - Python依赖
- `railway.toml` - Railway配置
- `zeabur.json` - Zeabur配置
- `Procfile` - 进程配置

### 2. 环境变量
系统会自动设置以下环境变量：
- `PORT=8080` - 应用端口
- `PYTHON_VERSION=3.11` - Python版本
- `FLASK_ENV=production` - Flask环境
- `PYTHONUNBUFFERED=1` - Python输出缓冲
- `TZ=Asia/Shanghai` - 时区设置

## Railway 部署

### 优势
- 免费额度：每月 $5 USD 额度
- 自动构建和部署
- 支持自定义域名
- 优秀的日志系统

### 部署步骤

1. **注册 Railway 账号**
   - 访问 [railway.app](https://railway.app)
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的电表监控仓库

3. **配置部署**
   - Railway 会自动检测 `railway.toml` 配置
   - 系统会自动安装依赖并启动服务
   - 部署完成后会提供一个 `.railway.app` 域名

4. **验证部署**
   - 访问提供的域名
   - 检查 `/api/status` 接口是否正常返回

### Railway 配置说明

```toml
[build]
builder = "nixpacks"  # 使用 Nixpacks 构建器

[deploy]
startCommand = "python3 app.py"  # 启动命令
restartPolicyType = "ON_FAILURE"  # 失败时重启
restartPolicyMaxRetries = 10  # 最大重试次数

[variables]
PORT = "8080"
PYTHON_VERSION = "3.11"
FLASK_ENV = "production"
PYTHONUNBUFFERED = "1"
TZ = "Asia/Shanghai"

[healthcheck]
path = "/api/status"  # 健康检查路径
interval = 30  # 检查间隔（秒）
timeout = 10   # 超时时间（秒）
retries = 3    # 重试次数

[networking]
port = 8080  # 网络端口
```

## Zeabur 部署

### 优势
- 免费额度：每月 3 个免费项目
- 亚洲节点（香港）延迟低
- 简单的配置文件
- 支持多种编程语言

### 部署步骤

1. **注册 Zeabur 账号**
   - 访问 [zeabur.com](https://zeabur.com)
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "Create Project"
   - 选择 "Deploy from GitHub"
   - 选择你的电表监控仓库

3. **配置部署**
   - Zeabur 会自动检测 `zeabur.json` 配置
   - 系统会自动构建和部署
   - 部署完成后会提供一个 `.zeabur.app` 域名

4. **验证部署**
   - 访问提供的域名
   - 检查系统是否正常运行

### Zeabur 配置说明

```json
{
  "name": "electricity-bill-monitoring",
  "build": {
    "buildCommand": "pip install -r requirements.txt",
    "outputDirectory": ".",
    "installCommand": "pip install -r requirements.txt"
  },
  "run": {
    "startCommand": "python3 app.py"
  },
  "env": {
    "PORT": "8080",
    "PYTHON_VERSION": "3.11",
    "FLASK_ENV": "production",
    "PYTHONUNBUFFERED": "1",
    "TZ": "Asia/Shanghai"
  },
  "regions": ["hkg1"],  # 香港节点
  "plan": "hobby",      # 免费套餐
  "healthCheck": {
    "path": "/api/status",
    "interval": 30,
    "timeout": 10,
    "retries": 3
  }
}
```

## 最佳实践建议

### 1. 选择平台建议

**选择 Railway 如果：**
- 需要更多的免费额度（$5/月）
- 需要更详细的日志和监控
- 项目访问量较大

**选择 Zeabur 如果：**
- 用户主要在亚洲地区（延迟更低）
- 需要简单快速的部署
- 项目访问量较小

### 2. 性能优化

- 使用 `gunicorn` 作为 WSGI 服务器
- 配置合适的 worker 数量（推荐 2 个）
- 设置请求超时和连接保持
- 启用请求限制防止过载

### 3. 监控和维护

- 定期检查 `/api/status` 接口
- 监控应用日志
- 设置健康检查确保服务可用性
- 定期更新依赖包

### 4. 数据持久化注意事项

⚠️ **重要提醒：**
- 云平台的文件系统是临时的
- 每次重新部署会丢失本地数据
- 建议使用云数据库存储重要数据
- 或者定期备份数据到外部存储

### 5. 成本控制

- 监控资源使用情况
- 合理设置健康检查频率
- 避免不必要的请求
- 使用缓存减少计算负载

## 故障排除

### 常见问题

1. **部署失败**
   - 检查 `requirements.txt` 是否包含所有依赖
   - 确认 Python 版本兼容性
   - 查看构建日志错误信息

2. **服务无法访问**
   - 检查端口配置是否正确
   - 确认健康检查路径可访问
   - 查看应用日志

3. **数据丢失**
   - 云平台重启会清空本地文件
   - 考虑使用外部数据库
   - 实现数据备份机制

### 调试命令

```bash
# 本地测试健康检查
curl http://localhost:8080/api/status

# 检查依赖安装
pip install -r requirements.txt

# 本地运行测试
python3 app.py
```

## 总结

两个平台都能很好地支持电表监控系统的部署：

- **Railway**：更适合需要稳定性和详细监控的项目
- **Zeabur**：更适合快速部署和亚洲用户访问的项目

建议先在两个平台都尝试部署，然后根据实际使用体验选择最适合的平台。