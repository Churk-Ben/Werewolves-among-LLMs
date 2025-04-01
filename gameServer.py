from flask import Flask, render_template
from flask_socketio import SocketIO, emit


class Server:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "secret"
        self.socketio = SocketIO(self.app)
        self.bind()
        self.game = Game(self)

    def bind(self):
        self.app.route("/")(self.index)
        self.socketio.on("connect")(self.connect)
        self.socketio.on("order")(self.handle_order)

    def index(self):
        return render_template("index.html")

    def connect(self, sid, auth=None):
        self.send_message("System", "欢迎来到狼人杀游戏！", "speech")
        self.fresh_state()

    def handle_order(self, data):
        order = data["content"]
        self.send_message("System", "...", "thought")
        self.game.parse_order(order)

    def send_message(self, player, content, type, room=None):
        emit(
            "message",
            {"player": player, "content": content, "type": type},
            room=room,
            broadcast=True,
        )

    def fresh_state(self):
        emit(
            "fresh_state",
            {
                "phase": "投票结束",
                "players": [
                    {
                        "name": "Alice",
                        "role": "WEREWOLF",
                        "alive": True,
                        "voted": 3,
                    },
                    {
                        "name": "Bob",
                        "role": "VILLAGER",
                        "alive": True,
                        "voted": 0,
                    },
                ],
            },
            broadcast=True,
        )

    def run_debug(self):
        self.socketio.run(self.app, debug=True)

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port)


class Game:
    def __init__(self, server: Server):
        self.server = server

    def parse_order(self, order):  # 之后会用ai分析指令
        print(f"Received order: {order}")
        match True:
            case _ if "开始" in order:
                msg = self.game_start()
            case _ if "结束" in order:
                msg = self.game_end()
            case _:
                msg = self.default()
        self.server.send_message("System", msg, "speech")

    def game_start(self):
        print("Game started")
        return "Game started"

    def game_end(self):
        print("Game ended")
        return "Game ended"

    def default(self):
        print("Invalid order")
        return "Invalid order"


if __name__ == "__main__":
    server = Server()
    server.run_debug()
