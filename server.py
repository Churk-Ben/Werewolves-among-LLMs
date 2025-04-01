from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from game import Game


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
        init_state = self.game.state
        self.fresh_state(init_state)
        self.send_message("System", "欢迎来到狼人杀游戏！", "speech")
        self.send_message("System", self.game.game_rules["content"], "speech")

    def handle_order(self, data):
        order = data["content"]
        self.game.parse_order(order)

    def send_message(self, player, content, type, room=None):
        emit(
            "message",
            {"player": player, "content": content, "type": type},
            room=room,
            broadcast=True,
        )

    def fresh_state(self, state):
        emit(
            "fresh_state",
            state,
            broadcast=True,
        )

    def run_debug(self):
        self.socketio.run(self.app, debug=True)

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    server = Server()
    server.run_debug()
