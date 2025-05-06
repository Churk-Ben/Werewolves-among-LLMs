# Werewolves of Deepseeks / Deepseek 狼人杀

A Python-based Werewolf game implementation with AI players.  
基于Python的狼人杀游戏实现，包含AI玩家功能。

## Table of Contents / 目录
- [Features / 功能特点](#features--功能特点)
- [Requirements / 环境要求](#requirements--环境要求)
- [Installation / 安装指南](#installation--安装指南)
- [Usage / 使用说明](#usage--使用说明)
- [Game Flow / 游戏流程](#game-flow--游戏流程)
- [File Structure / 文件结构](#file-structure--文件结构)

## Features / 功能特点
- AI-powered players with memory / 具有记忆功能的AI玩家
- Complete day-night cycle / 完整的昼夜循环
- Role assignment system / 角色分配系统
- Voting mechanism / 投票机制
- Web-based interface / 基于网页的界面

## Requirements / 环境要求
- Python 3.8+  
- Required packages:
```bash
pip install python-dotenv
```

## Installation / 安装指南
1. Clone this repository  
   克隆本仓库
```bash
git clone https://github.com/your-repo/Werewolves-of-Deepseeks.git
cd Werewolves-of-Deepseeks
```

2. Install dependencies  
   安装依赖
```bash
pip install -r about/requirements.txt
```

3. Create .env file with your API key  
   创建.env文件并添加API密钥
```bash
echo "API_KEY=your_api_key_here" > .env
```

## Usage / 使用说明
To start the game server:  
启动游戏服务器:
```bash
python server.py
```

Then open `http://localhost:5000` in your browser.  
然后在浏览器中打开 `http://localhost:5000`

## Game Flow / 游戏流程
1. Game initialization - roles are randomly assigned  
   游戏初始化 - 随机分配角色
2. Night phase - werewolves choose victims  
   夜晚阶段 - 狼人选择受害者
3. Day phase - discussion and voting  
   白天阶段 - 讨论和投票
4. Repeat until game ends  
   重复直到游戏结束

## File Structure / 文件结构
```
├── game.py          # Main game logic / 主游戏逻辑
├── manager.py       # Player management / 玩家管理
├── player.py        # Player class / 玩家类
├── prompts.py       # Game messages / 游戏提示信息
├── server.py        # Web server / 网页服务器
├── static/          # Static files / 静态文件
│   ├── css/         # Stylesheets / 样式表
│   └── js/          # JavaScript / 前端脚本
└── templates/       # HTML templates / HTML模板
```

## License / 许可证
[MIT License](#)
