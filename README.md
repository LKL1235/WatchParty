# Watch Party

一个在线视频观看聚会的Python Web应用项目。

## 项目简介

Watch Party 是一个基于Flask的Web应用，提供在线视频观看聚会功能。用户可以创建房间，邀请朋友一起同步观看视频，享受共同观影的乐趣。项目采用模块化设计，支持多用户实时同步和互动功能。

## 功能特性

- 🎬 在线视频观看聚会
- 👥 多用户同步观看
- 🏠 房间创建和管理
- 🌐 Web API 接口
- 🔐 用户认证和管理
- 📊 日志记录和监控
- 🔧 配置管理
- 🎨 现代化Web界面

## 项目结构

```
src/watch_party/
├── main.py          # Flask应用入口
├── api/             # API接口模块
├── auth/            # 认证模块
├── cmd/             # 命令行工具
├── commons/         # 公共工具
├── config/          # 配置管理
├── core/            # 核心功能
├── log/             # 日志模块
├── manager/         # 管理器模块
├── static/          # 静态文件
├── templates/       # HTML模板
└── types/           # 类型定义
```

## 环境要求

- Python 3.9+
- pip

## 安装说明

### 1. 克隆项目

```bash
git clone <repository-url>
cd video_python
```

### 2. 创建虚拟环境(可选)

```bash
python -m venv .venv
```

### 3. 激活虚拟环境(可选)

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -e .
```

### 5. 安装开发依赖（可选）

```bash
pip install -e ".[dev]"
```

### 6. 安装高级功能依赖（可选）

```bash
pip install -e ".[advanced]"
```

## 使用方法

### 启动Web应用

```bash
python src/watch_party/main.py
```

或使用安装后的命令：

```bash
watch-party
```

应用将在 `http://localhost:5000` 启动。

### 开始观看聚会

1. 访问主页创建或加入房间
2. 邀请朋友加入房间
3. 同步观看视频内容
4. 享受共同观影体验

### 开发模式

项目支持热重载，修改代码后会自动重启服务。

## 配置

运行目录下需要创建 `config` 目录。可以通过配置文件进行自定义配置。

## 开发工具

项目配置了以下开发工具：

- **Black**: 代码格式化
- **isort**: 导入排序
- **pytest**: 单元测试
- **pre-commit**: Git钩子

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src/
isort src/
```

## 贡献

欢迎提交Issues和Pull Requests！

## 许可证

本项目采用 [MIT许可证](LICENSE)。

## 作者

- **LKL1235** - [hood1235@foxmail.com](mailto:hood1235@foxmail.com)

---

如有问题或建议，请通过Issues联系我们。 