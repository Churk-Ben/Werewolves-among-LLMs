from manager import Manager
from model import Message


class Game:
    def __init__(self, server):
        self.server = server
        self.manager = Manager(self)
        self.state = {
            "phase": "欢迎来到狼人杀.",
            "night": 0,
            "players": [],
        }

    def parse_order(self, order):
        """处理游戏指令, 分发给对应角色"""
        try:
            match order:
                case "auto":
                    self.game_run()
                case _:
                    self.server.send_message("系统", f"未知指令: {order}", "thought")
        except Exception as e:
            self.server.send_message("系统", f"指令解析异常: {str(e)}", "error")

    def game_init(self):
        """初始化游戏, 分配角色"""
        try:
            self.state["phase"] = "游戏正在初始化..."
            result = self.manager.init_players()
            self.state["players"] = result.get("players", [])
            self.state["night"] = 0
            if "error" in result:
                self.server.send_message(
                    "系统", f"玩家初始化异常: {result['error']}", "error"
                )
        except Exception as e:
            self.server.send_message("系统", f"游戏初始化异常: {str(e)}", "error")

    def game_start(self):
        self.state["phase"] = "天黑请闭眼."
        self.manager.broadcast_to_player(
            "ALL",
            self.server.send_message(
                "系统",
                "天黑请闭眼.",
                "speech",
            ),
        )
        # 让狼人知晓友方信息
        werewolfs = []
        for player in self.state["players"]:
            if player["role"] == "WEREWOLF":
                werewolfs.append(player["name"])
        if werewolfs:
            werewolf_info = f"本场狼人是: {', '.join(werewolfs)}."
            self.manager.broadcast_to_player(
                "WEREWOLF",
                werewolf_info,
            )
        # 开始第一夜
        self.night_phase()

    def night_phase(self):
        """夜晚阶段. 狼人行动, 预言家行动, 女巫行动"""
        try:
            self.state["night"] += 1
            night_number = self.state["night"]
            self.state["phase"] = f"第{str(night_number)}夜"
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    "@death_message",
                    "speech",
                ),
            )
        except Exception as e:
            self.server.send_message("系统", f"夜晚阶段异常: {str(e)}", "error")

    def day_phase(self):
        """白天阶段. 发言, 投票"""
        try:
            self.state["phase"] = "天亮了"
            day_number = self.state["night"]
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    f"现在是第{day_number}天，白天阶段开始。",
                    "speech",
                ),
            )
            alive_players = []
            for player in self.manager.players_state:
                if player["alive"]:
                    alive_players.append(player["name"])
            for player in alive_players:
                self.manager.let_player_act(
                    player,
                    "白天阶段，请发言。",
                )
            self.vote_phase()
        except Exception as e:
            self.server.send_message("系统", f"白天阶段异常: {str(e)}", "error")

    def vote_phase(self):
        """投票阶段"""
        try:
            self.state["phase"] = "投票阶段"
            day_number = self.state["night"]
            alive_players = []
            for player in self.manager.players_state:
                if player["alive"]:
                    alive_players.append(player["name"])
            vote_message = f"现在是第{day_number}天投票环节，存活玩家: {', '.join(alive_players)}。请投票."
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    vote_message,
                    "speech",
                ),
            )
            self.check_game_end()
        except Exception as e:
            self.server.send_message("系统", f"投票阶段异常: {str(e)}", "error")

    def check_game_end(self):
        """检查游戏是否结束"""
        try:
            alive_werewolves = 0
            alive_villagers = 0
            for player in self.state["players"]:
                if player["alive"]:
                    if player["role"] == "WEREWOLF":
                        alive_werewolves += 1
                    else:
                        alive_villagers += 1
            if alive_werewolves == 0:
                end_message = "游戏结束！所有狼人都已出局，好人阵营胜利！"
                self.state["phase"] = "游戏结束 - 好人胜利"
            elif alive_werewolves >= alive_villagers:
                end_message = "游戏结束！狼人数量已经大于等于好人数量，狼人阵营胜利！"
                self.state["phase"] = "游戏结束 - 狼人胜利"
            else:
                return
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    end_message,
                    "speech",
                ),
            )
        except Exception as e:
            self.server.send_message("系统", f"结算阶段异常: {str(e)}", "error")

    def game_run(self):
        """游戏主循环"""
        try:
            self.game_init()
            self.game_start()
            while True:
                self.night_phase()
                self.day_phase()
                if (
                    self.state["phase"] == "游戏结束 - 好人胜利"
                    or self.state["phase"] == "游戏结束 - 狼人胜利"
                ):
                    break
        except Exception as e:
            self.server.send_message("系统", f"主循环异常: {str(e)}", "error")
