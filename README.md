# Werewolves among LLMs

基于 Python 的狼人杀游戏实现，支持 AI 玩家和网页界面。
> [!note]
> 目前非推理模型因为没有适配思维能力, 所以表现较差.

## 目录 / Table of Contents

- [功能特点 / Features](#功能特点--features)
- [安装指南 / Installation](#安装指南--installation)
- [使用说明 / Usage](#使用说明--usage)
- [游戏流程 / Game-Flow](#游戏流程--game-flow)
- [文件结构 / File-Structure](#文件结构--file-structure)
- [技术架构 / Tech-Stack](#技术架构--tech-stack)
- [注意事项 / Notes](#注意事项--notes)

## 功能特点 / Features

- 具有记忆功能的 AI 玩家（AI-powered players with memory）
- 完整的昼夜循环（Complete day-night cycle）
- 角色分配系统（Role assignment system）
- 投票机制（Voting mechanism）
- 基于网页的界面（Web-based interface）
- 实时消息转发与状态跟踪
- 支持通过 Web 界面发送游戏命令

## 安装指南 / Installation

1. 克隆本仓库 / Clone this repository

   ```bash
   git clone https://github.com/your-repo/Werewolves-of-Deepseeks.git
   cd Werewolves-of-Deepseeks
   ```

2. 安装依赖 / Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. 创建 .env 文件并添加 API 密钥 / Create .env file with your API key

   ```bash
   echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
   echo "CHAT_GPT_API_KEY=your_api_key_here" > .env
   ...
   ```

## 使用说明 / Usage

### 配置文件 / Configuration File

- `config.yaml`：配置游戏设置、AI 玩家和本地服务等
- `.env`：配置 API 密钥等敏感信息

### 在控制台启动游戏 / Start Game in Console

``` yaml
web:
    enable: false
```

```bash
python app.py
```


### 启动本地服务器

``` yaml
web:
    enable: true
```

```bash
python app.py
```

浏览器访问 `http://127.0.0.1:5000`，在输入框中输入 `/start` 开始游戏

## 游戏流程 / Game Flow

1. 游戏初始化 - 随机分配角色
2. 夜晚阶段 - 狼人选择受害者
3. 白天阶段 - 讨论和投票
4. 重复直到游戏结束

## 文件结构 / File Structure

- `server/Server.py`：主服务器类，包含控制台捕获和消息转发逻辑
- `static/js/main.js`：前端 JavaScript，处理 WebSocket 连接和 UI 更新
- `static/css/`：样式文件
- `templates/index.html`：主页面模板
- `requirements.txt`：依赖列表
- `server.py`：游戏主服务器入口
- `app.py`：Web 服务器入口

## 技术架构 / Tech Stack

- **后端**: Python, Flask, Flask-SocketIO
- **前端**: HTML, CSS, JavaScript, Socket.IO
- **AI**: LiteLLM

## 注意事项 / Notes

- 服务器监听控制台输出，不修改游戏逻辑
- 支持 Rich 库输出格式，自动移除 ANSI 转义序列
- 玩家信息解析基于游戏输出的文本模式匹配

---

## 感谢开源
- LiteLLM

---

欢迎贡献和反馈！
