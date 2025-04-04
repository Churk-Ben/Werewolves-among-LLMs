from manager import Manager


class Game:
    def __init__(self, server):
        self.server = server
        self.manager = Manager(self)
        self.rules = self.manager.aware_game_rules()["content"]
        self.state = {
            "phase": "欢迎来到狼人杀！",
            "players": [],
        }

    def parse_order(self, order):  # 之后会用ai分析指令
        print(f"Received order: {order}")
        match True:
            case _ if "0" in order:
                msg = self.game_start()
            case _ if "1" in order:
                msg = self.game_end()
            case _ if "2" in order:
                msg = self.change()
            case _ if "5" in order:
                msg = self.fresh_state()
            case _:
                msg = self.default()
        if msg:
            self.server.send_message("System", msg, "thought")

    def game_start(self):
        self.state["phase"] = "天黑请闭眼。"
        self.state["players"] = self.manager.init_players()["players"]
        return "Game started"

    def game_end(self):
        return "Game ended"

    def change(self):
        import random

        self.state["players"][0]["alive"] = random.choice([True, False])
        self.state["players"][1]["alive"] = random.choice([True, False])
        self.state["players"][2]["alive"] = random.choice([True, False])
        self.state["players"][3]["alive"] = random.choice([True, False])
        return "Change randomly"

    def fresh_state(self):
        self.server.fresh_state()

    def default(self):
        return "Invalid order"
