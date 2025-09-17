# 智能电表监控系统 ⚡

一个优雅的智能电表监控系统，采用Airbnb风格设计，提供实时电量监控、用电分析和费用预估功能。具备完善的错误处理机制和重试逻辑，确保系统稳定运行。

## ✨ 特性

- 🎨 **苹果官网风格设计** - 优雅极简的用户界面
- 📊 **实时数据监控** - 电量余额、金额余额实时显示
- 📈 **多维度图表分析** - 趋势图、每小时、每日、每月用电统计
- 💰 **智能费用预估** - 基于历史数据的费用预测
- 📱 **响应式设计** - 完美适配各种设备屏幕
- 🔄 **自动刷新** - 2分钟自动更新数据
- 🛡️ **健壮性保障** - 完善的错误处理和边界检查

## 🚀 快速开始

### 本地运行

1. **克隆项目**
   ```bash
   git clone https://github.com/mariohuang233/ElectricityBillMonitoring.git
   cd ElectricityBillMonitoring
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   python3 app.py
   ```

4. **访问应用**
   打开浏览器访问 `http://localhost:8080`

## 🌐 部署指南

### Railway 部署

1. 连接 GitHub 仓库到 Railway
2. Railway 会自动检测 `railway.toml` 配置文件
3. 部署完成后即可访问

### Zeabur 部署

1. 连接 GitHub 仓库到 Zeabur
2. Zeabur 会自动检测 `zeabur.json` 配置文件
3. 选择合适的区域进行部署

### 其他平台部署

项目包含 `Procfile` 文件，支持 Heroku 等兼容平台的一键部署。

## 📁 项目结构

```
ElectricityBillMonitoring/
├── app.py              # Flask 后端服务
├── monitor.html        # 前端页面
├── requirements.txt    # Python 依赖
├── railway.toml       # Railway 部署配置
├── zeabur.json        # Zeabur 部署配置
├── Procfile           # Heroku 兼容配置
└── README.md          # 项目文档
```

## 🎯 核心功能

### 实时监控
- 电量余额显示
- 金额余额显示
- 电表状态指示
- 自动刷新倒计时

### 数据分析
- **趋势图表** - 显示电量和金额变化趋势
- **每小时统计** - 24小时用电分布
- **每日统计** - 一周内每日用电量
- **每月统计** - 年度月用电量对比

### 智能预估
- 本周用电预估
- 本月用电预估
- 预计费用计算

## 🛠️ 技术栈

- **后端**: Python Flask
- **前端**: HTML5 + CSS3 + JavaScript
- **图表**: Chart.js
- **样式**: 苹果官网风格设计系统
- **部署**: Railway, Zeabur, Heroku 兼容

## 🎨 设计特色

- **字体系统**: SF Pro Display/Text 字体族
- **色彩方案**: 苹果官方色彩规范
- **布局系统**: CSS Grid + Flexbox
- **动画效果**: 流畅的过渡和悬停效果
- **响应式**: 完美适配移动端和桌面端

## 📊 API 接口

### 获取电表数据
```
GET /api/meter-data
```

返回格式:
```json
{
  "meter_name": "电表名称",
  "remaining_power": "剩余电量",
  "remaining_amount": "剩余金额",
  "update_time": "更新时间"
}
```

## 🔧 配置说明

### 环境变量
- `PORT`: 服务端口 (默认: 8080)
- `FLASK_ENV`: Flask 环境 (production/development)
- `PYTHON_VERSION`: Python 版本 (推荐: 3.11)

### 自定义配置
- 修改 `app.py` 中的 API 端点
- 调整 `monitor.html` 中的刷新间隔
- 自定义图表颜色和样式

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目链接: [https://github.com/mariohuang233/ElectricityBillMonitoring](https://github.com/mariohuang233/ElectricityBillMonitoring)
- 问题反馈: [Issues](https://github.com/mariohuang233/ElectricityBillMonitoring/issues)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！