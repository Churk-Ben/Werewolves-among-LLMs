from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sys
import io
import threading
import re
import json
from contextlib import redirect_stdout, redirect_stderr
from game.Game import WerewolfGame


class ConsoleCapture:
    """控制台输出捕获类"""

    def __init__(self, socketio):
        self.socketio = socketio
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.buffer = io.StringIO()
        self.game_phase = "等待中"
        self.players = []

    def write(self, text: str):
        """捕获输出文本"""
        # 写入原始输出
        self.original_stdout.write(text)
        self.original_stdout.flush()

        # 处理并转发消息
        if text.strip():
            # 移除rich库的边框字符
            clean_text = (
                text.strip()
                .replace("╭", "")
                .replace("╰", "")
                .replace("─", "")
                .replace("│", "")
                .replace("╮", "")
                .replace("╯", "")
                .strip()
            )

            self.process_message(clean_text)

    def flush(self):
        """刷新缓冲区"""
        self.original_stdout.flush()

    def process_message(self, text):
        """处理消息并分类"""
        # 移除ANSI转义序列
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_text = ansi_escape.sub("", text)

        # 判断消息类型
        message_type = self.classify_message(clean_text)

        # 更新游戏状态
        self.update_game_state(clean_text)

        # 发送消息到前端
        self.socketio.emit(
            "message",
            {
                "type": message_type,
                "content": clean_text,
                "timestamp": self.get_timestamp(),
            },
        )

        # 发送游戏状态更新
        self.socketio.emit(
            "game_state", {"phase": self.game_phase, "players": self.players}
        )

    def classify_message(self, text):
        """分类消息类型"""
        # 系统消息特征
        system_patterns = [r"#@.*", r"玩家.*已加入游戏"]

        # 玩家发言特征
        speech_patterns = [r"#:.*", r".*发言:.*"]

        # 错误消息特征
        error_patterns = [r"#!.*", r"错误", r"Error", r"Exception", r"Traceback"]

        for pattern in error_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "error"

        for pattern in system_patterns:
            if re.search(pattern, text):
                return "system"

        for pattern in speech_patterns:
            if re.search(pattern, text):
                return "speech"

        return "system"  # 默认为系统消息

    def update_game_state(self, text):
        """更新游戏状态"""
        # 更新游戏阶段
        if "等待中" in text:
            self.game_phase = "等待中"
        elif "夜晚" in text or "夜晚降临" in text:
            self.game_phase = "夜晚阶段"
        elif "白天" in text or "天亮了" in text:
            self.game_phase = "白天阶段"
        elif "发言阶段" in text:
            self.game_phase = "发言阶段"
        elif "投票阶段" in text:
            self.game_phase = "投票阶段"
        elif "游戏结束" in text:
            self.game_phase = "游戏结束"

        # 解析玩家信息
        if "你的身份是" in text:
            match = re.search(r"(\w+), 你的身份是: (\w+)", text)
            if match:
                player_name = match.group(1)
                player_role = match.group(2)
                
                # 检查玩家是否已存在，避免重复添加
                existing_player = None
                for player in self.players:
                    if player["name"] == player_name:
                        existing_player = player
                        break
                
                if existing_player:
                    # 更新现有玩家信息
                    existing_player["role"] = player_role
                    existing_player["status"] = "存活"
                else:
                    # 添加新玩家
                    self.players.append(
                        {
                            "name": player_name,
                            "role": player_role,
                            "status": "存活",
                            "temperature": 0.8,
                        }
                    )

        # 解析玩家死亡信息
        death_match = re.search(r"(\w+) 死了", text)
        if death_match:
            dead_player = death_match.group(1)
            for player in self.players:
                if player["name"] == dead_player:
                    player["status"] = "死亡"
                    break

    def get_timestamp(self):
        """获取时间戳"""
        import datetime

        return datetime.datetime.now().strftime("%H:%M:%S")


class GameServer:
    """游戏服务器类"""

    def __init__(self):
        self.app = Flask(
            __name__, static_folder="../static", template_folder="../templates"
        )
        self.app.config["SECRET_KEY"] = "werewolf_game_secret"
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.console_capture = ConsoleCapture(self.socketio)
        self.game = None
        self.game_thread = None

        self.setup_routes()
        self.setup_socketio_events()

    def setup_routes(self):
        """设置路由"""

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/api/status")
        def status():
            return jsonify(
                {
                    "phase": self.console_capture.game_phase,
                    "players": self.console_capture.players,
                }
            )

    def setup_socketio_events(self):
        """设置SocketIO事件"""

        @self.socketio.on("connect")
        def handle_connect():
            print(f"客户端已连接")
            # 发送当前游戏状态
            emit(
                "game_state",
                {
                    "phase": self.console_capture.game_phase,
                    "players": self.console_capture.players,
                },
            )

        @self.socketio.on("disconnect")
        def handle_disconnect():
            print("客户端已断开连接")

        @self.socketio.on("command")
        def handle_command(data):
            command = data.get("command", "").strip()
            if command == "/start":
                self.start_game()
            elif command == "/cancel":
                self.game._cancel()
            elif command == "/comment":
                print("#! 等待ai复盘游戏")
            else:
                emit(
                    "message",
                    {
                        "type": "error",
                        "content": f"未知命令: {command}",
                        "timestamp": self.console_capture.get_timestamp(),
                    },
                )

    def start_game(self):
        """启动游戏"""
        if self.game_thread and self.game_thread.is_alive():
            self.socketio.emit(
                "message",
                {
                    "type": "error",
                    "content": "游戏已在运行中",
                    "timestamp": self.console_capture.get_timestamp(),
                },
            )
            return

        # 重定向控制台输出
        sys.stdout = self.console_capture

        # 在新线程中启动游戏
        self.game_thread = threading.Thread(target=self._run_game)
        self.game_thread.daemon = True
        self.game_thread.start()

        self.socketio.emit(
            "message",
            {
                "type": "system",
                "content": "游戏启动中...",
                "timestamp": self.console_capture.get_timestamp(),
            },
        )

    def _run_game(self):
        """运行游戏的内部方法"""
        try:
            self.game = WerewolfGame()
            self.game.run()
        except Exception as e:
            self.socketio.emit(
                "message",
                {
                    "type": "error",
                    "content": f"游戏运行错误: {str(e)}",
                    "timestamp": self.console_capture.get_timestamp(),
                },
            )
        finally:
            # 恢复原始输出
            sys.stdout = self.console_capture.original_stdout

    def run(self, host="127.0.0.1", port=5000, debug=False):
        """运行服务器"""
        print(f"服务器启动在 http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)
