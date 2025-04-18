from manager import Manager
from model import Message


class Game:
    def __init__(self, server):
        self.server = server
        self.manager = Manager(self)
        self.rules = ""
        self.state = {
            "phase": "欢迎来到狼人杀！",
            "players": [],
            "current_night": 0,
            "killed_player": None,
            "witch_saved": False,
            "witch_poisoned": False,
            "seer_checked": [],  # 预言家已查验的玩家
            "werewolves": [],  # 狼人列表，用于让狼人互相知晓
            "day_voted": None,  # 白天投票出局的玩家
        }

    def parse_order(self, order):  # 之后会用ai分析指令
        # 检查是否是开始游戏指令
        if "0" in order:
            self.game_start()
            return

        # 检查是否是自动流程指令
        if "auto" in order:
            self.game_flow()
            return

        # 其他指令处理
        match True:
            case _ if "1" in order:
                self.night_phase()

            case _ if "2" in order:
                self.day_phase()

            case _ if "3" in order:
                self.vote_phase()

            case _:
                message = Message("系统", "未解析的指令", "system")
                self.server.send_message("系统", "未解析的指令", "thought")

    def game_flow(self):
        """自动执行游戏流程，从当前阶段开始自动进行到游戏结束"""

    def game_init(self):
        # 初始化玩家，这会创建新的Player对象，清空AI玩家的记忆
        self.state["players"] = self.manager.init_players()["players"]
        self.rules = self.manager.get_game_rules()

        # 初始化狼人列表，让狼人互相知晓
        self.state["werewolves"] = []
        for player in self.state["players"]:
            if player["role"] == "WEREWOLF":
                self.state["werewolves"].append(player["name"])

        # 重置游戏状态
        self.state["current_night"] = 0  # 从第0夜开始
        self.state["killed_player"] = None
        self.state["witch_saved"] = False
        self.state["witch_poisoned"] = False
        self.state["seer_checked"] = []
        self.state["day_voted"] = None

    def game_start(self):
        self.state["phase"] = "游戏开始！"

    def night_phase(self):
        """夜晚阶段，包括狼人行动、预言家查验、女巫救人/毒人"""

    def werewolf_act(self):
        """狼人行动阶段"""
        self.state["phase"] = "天黑请闭眼，狼人请睁眼。"

    def seer_act(self):
        """预言家行动阶段"""
        self.state["phase"] = "狼人请闭眼，预言家请睁眼。"

    def witch_act(self):
        """女巫行动阶段"""
        self.state["phase"] = "预言家请闭眼，女巫请睁眼。"

    def day_phase(self):
        """白天发言阶段"""
        self.state["phase"] = "白天发言阶段"

    def vote_phase(self):
        """投票阶段"""
        self.state["phase"] = "投票阶段"

    def check_game_end(self):
        """检查游戏是否结束"""
        pass
