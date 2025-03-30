from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from game import Game


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "secret!"
        self.socketio = SocketIO(self.app)

        # 注册路由和事件处理函数
        self.app.route("/")(self.index)
        self.socketio.on("connect")(self.connect)
        self.socketio.on("order")(self.handle_order)

    def index(self):
        return render_template("index.html")

    def connect(self):
        emit(
            "message",
            {"player": "System", "content": "欢迎来到狼人杀游戏！", "type": "speech"},
            broadcast=True,
        )

    def handle_order(self, data):
        order = data["content"]
        Game.parse_order(data["content"])()
        emit(
            "message",
            {"player": "Assistant", "content": "法官的指令：" + order, "type": "note"},
            broadcast=True,
        )

    def run(self):
        self.socketio.run(self.app, debug=True)


if __name__ == "__main__":
    server = Server()
    server.run()
