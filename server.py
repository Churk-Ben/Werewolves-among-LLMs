from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from game import Game


class Server:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "secret"
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.bind()

    def bind(self):
        self.app.route("/")(self.index)
        self.socketio.on("connect")(self.connect)
        self.socketio.on("order")(self.handle_order)
        self.socketio.on("get_player_history")(self.get_player_history)

    def index(self):
        return render_template("index.html")

    def connect(self):
        self.game = Game(self)
        self.game.game_init()
        self.fresh_state()

    def handle_order(self, data):
        order = data["content"]
        self.game.parse_order(order)
        self.fresh_state()

    def get_player_history(self):
        """获取所有玩家的历史记忆并发送到前端"""
        try:
            if hasattr(self, "game") and hasattr(self.game, "manager"):
                players_history = {}
                for player in self.game.manager.players_object:
                    players_history[player.name] = player.history
                emit("player_history", players_history)
        except Exception as e:
            emit(
                "message",
                {
                    "player": "系统",
                    "content": f"获取玩家历史记忆失败: {str(e)}",
                    "type": "error",
                },
            )

    # communal functions
    def send_message(self, player, content, type, room="ALL"):
        message = {
            "player": player,
            "content": content,
            "type": type,
            "room": room,
        }
        self._emit_message(message)
        return message

    def send_stream(self, player, response, type, room="ALL"):
        # response须为client回复对象
        message = {
            "player": player,
            "type": type,
            "room": room,
        }
        self._emit_message(message, event="message_start")
        content = ""
        try:
            for chunk in response:
                chunk_content = getattr(chunk.choices[0].delta, "content", None)
                if chunk_content:
                    content += chunk_content
                    self._emit_message({"chunk": chunk_content}, event="message_chunk")
        except Exception as e:
            self._emit_message({"error": str(e)}, event="message_error")
        self._emit_message({}, event="message_end")
        message["content"] = content
        return message

    def _emit_message(self, message, event="message"):
        try:
            emit(event, message, broadcast=True)
        except Exception as e:
            # 可以根据需要记录日志
            pass

    def fresh_state(self):
        try:
            emit(
                "fresh_state",
                getattr(self.game, "state", {}),
                broadcast=True,
            )
        except Exception as e:
            # 可以根据需要记录日志
            pass

    # run functions
    def run_debug(self):
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=True,
            allow_unsafe_werkzeug=True,
        )

    def run(self):
        self.socketio.run(
            self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True
        )


if __name__ == "__main__":
    server = Server()
    server.run_debug()
