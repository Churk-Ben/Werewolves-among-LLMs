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

    def parse_order(self, order):  # 之后会用ai分析指令
        match True:
            case _ if "0" in order:
                self.game_start()

            case _ if "1" in order:
                self.werewolf_act()

            case _:
                self.server.send_message("系统", "未解析的指令", "thought")

    def game_init(self):
        self.state["players"] = self.manager.init_players()["players"]
        self.rules = self.manager.get_game_rules()

    def game_start(self):
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

    def werewolf_act(self):
        self.state["phase"] = "天黑请闭眼，狼人请睁眼。"
        temp=self.manager.let_player_act(
            "WEREWOLF",
            "请选择你们要🔪的人",
        )
        self.manager.broadcast_to_player(
            "WEREWOLF",
            temp,
        )
