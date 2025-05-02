from manager import Manager


class Game:
    def __init__(self, server):
        self.server = server
        self.manager = Manager(self)
        self.state = {
            "phase": "欢迎来到狼人杀！",
            "night": 0,
            "players": [],
        }

    def parse_order(self, order):
        """处理游戏指令并分发给对应角色"""
        match order:

            case "游戏开始":
                self.game_run()

            case _:
                self.server.send_message("系统", f"未知指令: {order}", "think")

    def game_init(self):
        """初始化游戏, 分配角色. 这会创建新的Player对象, 清空AI玩家的记忆"""
        self.state["phase"] = "游戏正在初始化..."
        self.state["players"] = self.manager.init_players()["players"]
        self.state["night"] = 0

    def game_start(self):
        self.state["phase"] = "天黑请闭眼."
        self.manager.broadcast_to_player(
            "ALL",
            self.server.send_message(
                "系统",
                "游戏开始.天黑,请闭眼.",
                "speech",
            ),
        )

        # 让狼人知晓友方信息
        werewolfs = []
        for player in self.state["players"]:
            if player["role"] == "WEREWOLF":
                werewolfs.append(player["name"])
        werewolf_info = f"本场狼人是: {', '.join(werewolfs)}。"
        self.manager.broadcast_to_player(
            "WEREWOLF",
            werewolf_info,
        )

        # 开始第一夜
        self.night_phase()

    def night_phase(self):
        """夜晚阶段. 狼人行动, 预言家行动, 女巫行动"""
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

    def day_phase(self):
        """白天阶段. 发言, 投票"""
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

        # 让所有存活玩家依次发言
        alive_players = []
        for player in self.manager.players_state:
            if player["alive"]:
                alive_players.append(player["name"])

        for player in alive_players:
            self.manager.let_player_act(
                player,
                "白天阶段，请发言。",
            )

        # 开始投票阶段
        self.vote_phase()

    def vote_phase(self):
        """投票阶段"""
        self.state["phase"] = "投票阶段"
        day_number = self.state["night"]

        # 获取存活玩家列表
        alive_players = []
        for player in self.manager.players_state:
            if player["alive"]:
                alive_players.append(player["name"])

        # 发送系统消息，开始投票
        vote_message = f"现在是第{day_number}天投票环节，存活玩家: {', '.join(alive_players)}。请投票."
        self.manager.broadcast_to_player(
            "ALL",
            self.server.send_message(
                "系统",
                vote_message,
                "speech",
            ),
        )

        # 检查游戏是否结束
        self.check_game_end()

    def check_game_end(self):
        """检查游戏是否结束"""
        # 统计存活的狼人和好人数量
        alive_werewolves = 0
        alive_villagers = 0

        for player in self.state["players"]:
            if player["alive"]:
                if player["role"] == "WEREWOLF":
                    alive_werewolves += 1
                else:
                    alive_villagers += 1

        # 判断游戏是否结束
        if alive_werewolves == 0:
            end_message = "游戏结束！所有狼人都已出局，好人阵营胜利！"
            self.state["phase"] = "游戏结束 - 好人胜利"
        elif alive_werewolves >= alive_villagers:
            end_message = "游戏结束！狼人数量已经大于等于好人数量，狼人阵营胜利！"
            self.state["phase"] = "游戏结束 - 狼人胜利"
        else:
            return

        # 发送游戏结束消息
        self.manager.broadcast_to_player(
            "ALL",
            self.server.send_message(
                "系统",
                end_message,
                "speech",
            ),
        )

    def game_run(self):
        """游戏主循环"""
        self.game_init()
        self.game_start()
        while True:
            # 夜晚阶段
            self.night_phase()

            # 白天阶段
            self.day_phase()

            # 结束游戏
            if (
                self.state["phase"] == "游戏结束 - 好人胜利"
                or self.state["phase"] == "游戏结束 - 狼人胜利"
            ):
                break
