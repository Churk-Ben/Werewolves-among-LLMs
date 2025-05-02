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
            case "狼人行动":
                self.manager.let_player_act("WEREWOLF", "狼人请选择要击杀的目标")
            case "预言家查验":
                self.manager.let_player_act("SEER", "预言家请选择要查验的玩家")
            case "女巫救人/毒人":
                self.manager.let_player_act("WITCH", "女巫请选择要救或毒的目标")
            case "白天发言":
                self.day_phase()
            case "投票":
                self.vote_phase()
            case "游戏开始":
                self.game_start()
            case "初始化游戏":
                self.game_init()
            case _:
                self.manager.broadcast_to_player("ALL", f"未知指令: {order}")

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
        alive_players = [player for player in self.state["players"] if player["alive"]]

    def vote_phase(self):
        """投票阶段"""
        self.state["phase"] = "投票阶段"

        # 获取存活玩家列表
        alive_players = [
            player["name"] for player in self.state["players"] if player["alive"]
        ]

        # 发送系统消息，开始投票
        day_number = self.state["current_night"]
        vote_message = f"现在是第{day_number}天投票环节，存活玩家: {', '.join(alive_players)}。请各位玩家投出你认为是狼人的玩家。得票最多的玩家将被放逐。"
        temp = self.server.send_message(
            "系统",
            vote_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )

        # 让所有存活玩家进行投票
        day_number = self.state["current_night"]
        vote_prompt = f"现在是第{day_number}天投票阶段，请投票选出你认为是狼人的玩家，可选目标: {', '.join(alive_players)}。明确写出玩家名字，格式为'我投票给XXX'。"
        self.manager.let_player_act(
            "ALL",
            vote_prompt,
        )

        # 这里应该有投票统计的逻辑，暂时模拟一下
        # 实际应该从玩家的回复中解析出投票目标
        # 简化处理：假设投票第一个狼人
        voted_player = None
        for player in self.state["players"]:
            if player["role"] == "WEREWOLF" and player["alive"]:
                voted_player = player
                self.state["day_voted"] = player["name"]
                player["alive"] = False
                break

        # 公布投票结果
        if voted_player:
            result_message = f"投票结束，{voted_player['name']}被放逐出局。"
            # 公布被放逐玩家的身份
            role_reveal = f"{voted_player['name']}的身份是{voted_player['role']}。"
            result_message += role_reveal
        else:
            result_message = "投票结束，没有玩家被放逐。"

        temp = self.server.send_message(
            "系统",
            result_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
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
            # 狼人全部出局，好人胜利
            end_message = "游戏结束！所有狼人都已出局，好人阵营胜利！"
            self.state["phase"] = "游戏结束 - 好人胜利"
        elif alive_werewolves >= alive_villagers:
            # 狼人数量大于等于好人，狼人胜利
            end_message = "游戏结束！狼人数量已经大于等于好人数量，狼人阵营胜利！"
            self.state["phase"] = "游戏结束 - 狼人胜利"
        else:
            # 游戏继续
            return

        # 发送游戏结束消息
        temp = self.server.send_message(
            "系统",
            end_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )

        # 公布所有玩家身份
        roles_message = "玩家身份揭晓：\n"
        for player in self.state["players"]:
            roles_message += f"{player['name']}: {player['role']}\n"

        temp = self.server.send_message(
            "系统",
            roles_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
