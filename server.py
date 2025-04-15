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

    def send_message(self, player, content, type, room="ALL"):
        message = {
            "player": player,
            "content": content,
            "type": type,
            "room": room,
        }
        emit(
            "message",
            message,
            broadcast=True,
        )
        return message

    def send_stream(self, player, response, type, room="ALL"):
        """response须为client回复对象"""
        message = {
            "player": player,
            "type": type,
            "room": room,
        }
        emit(
            "message_start",
            message,
            broadcast=True,
        )
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                content += chunk_content
                emit(
                    "message_chunk",
                    {"chunk": chunk_content},
                    broadcast=True,
                )
        emit(
            "message_end",
            {},
            broadcast=True,
        )
        message["content"] = content
        return message

    def fresh_state(self):
        emit(
            "fresh_state",
            self.game.state,
            broadcast=True,
        )

    def connect(self):
        self.game = Game(self)
        self.game.game_init()
        self.fresh_state()

    def handle_order(self, data):
        order = data["content"]
        self.game.parse_order(order)
        self.fresh_state()

    def run_debug(self):
        self.socketio.run(self.app, debug=True,allow_unsafe_werkzeug=True)

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    server = Server()
    server.run_debug()
