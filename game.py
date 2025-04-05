from manager import Manager


class Game:
    def __init__(self, server):
        self.server = server
        self.manager = Manager(self)
        self.rules = ""
        self.state = {
            "phase": "欢迎来到狼人杀！",
            "players": [],
        }
        self.history = [
            {"role": "system", "content": "You are a helpful assistant"},
        ]

    def parse_order(self, order):  # 之后会用ai分析指令
        match True:
            case _ if "0" in order:
                self.game_start()
                self.game_loop()

            case _:
                self.server.send_message("系统", "未解析的指令", "thought")

    def game_start(self):
        self.state["players"] = self.manager.init_players()["players"]
        self.rules = self.manager.get_game_rules()

    def game_loop(self):
        self.state["phase"] = "游戏开始！"
        temp = self.server.send_message(
            "系统",
            "下面宣读本场游戏规则...<br><br>" + self.rules,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
