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

    def bind(self):
        self.app.route("/")(self.index)
        self.socketio.on("connect")(self.connect)
        self.socketio.on("order")(self.handle_order)

    def index(self):
        return render_template("index.html")

    def send_message(self, player, content, type, room=None, chunk_size=200):
        if len(content) <= chunk_size:
            emit(
                "message",
                {"player": player, "content": content, "type": type},
                room=room,
                broadcast=True,
            )
        else:
            # Send start signal
            emit(
                "message_start",
                {"player": player, "type": type},
                room=room,
                broadcast=True,
            )
            
            # Send content in chunks
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                emit(
                    "message_chunk",
                    {"chunk": chunk},
                    room=room,
                    broadcast=True,
                )
            
            # Send end signal
            emit(
                "message_end",
                {},
                room=room,
                broadcast=True,
            )

    def fresh_state(self):
        emit(
            "fresh_state",
            self.game.state,
            broadcast=True,
        )

    def connect(self, sid, auth=None):
        self.game = Game(self)
        self.game.game_start()
        self.fresh_state()
        self.send_message(
            "System",
            "下面宣读本场游戏规则...<br><br>" + self.game.rules,
            "speech",
        )

    def handle_order(self, data):
        order = data["content"]
        self.game.parse_order(order)

    def run_debug(self):
        self.socketio.run(self.app, debug=True)

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    server = Server()
    server.run_debug()
