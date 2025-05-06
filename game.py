from manager import Manager
from prompts import GAME_PROMPTS, GAME_PHASES, PLAYER_PROMPTS


class Game:
    def __init__(self, server):
        self.server = server
        self.manager = Manager(self)
        self.state = {
            "phase": GAME_PHASES["welcome"],
            "night": 0,
            "players": [],
        }

    def parse_order(self, order):
        """处理游戏指令并分发给对应角色, 增加异常处理"""
        try:
            match order:
                case "auto":
                    self.game_run()
                case _:
                    self.server.send_message(
                        "系统", GAME_PROMPTS["unknown_command"].format(order), "thought"
                    )
        except Exception as e:
            self.server.send_message("系统", GAME_PROMPTS["parse_order_error"].format(str(e)), "error")

    def game_init(self):
        """初始化游戏, 分配角色. 这会创建新的Player对象, 清空AI玩家的记忆, 增加异常处理"""
        try:
            self.state["phase"] = GAME_PHASES["initializing"]
            result = self.manager.init_players()
            self.state["players"] = result.get("players", [])
            self.state["night"] = 0
            if "error" in result:
                self.server.send_message(
                    "系统", GAME_PROMPTS["init_error"].format(result["error"]), "error"
                )
        except Exception as e:
            self.server.send_message(
                "系统", GAME_PROMPTS["game_init_error"].format(str(e)), "error"
            )

    def game_start(self):
        self.state["phase"] = GAME_PHASES["night"]
        self.manager.broadcast_to_player(
            "ALL",
            self.server.send_message(
                "系统",
                GAME_PROMPTS["night_start"],
                "speech",
            ),
        )
        # 告知所有玩家场信息
        self.manager.broadcast_to_player(
            "ALL",
            self.server.send_message(
                "系统",
                GAME_PROMPTS["player_list"].format(', '.join([player['name'] for player in self.state['players']])) + "\n" +
                GAME_PROMPTS["role_list"].format(', '.join([player['role'] for player in self.state['players']])),
                "speech",
            ),
        )
        # 让狼人知晓友方信息
        werewolfs = []
        for player in self.state["players"]:
            if player["role"] == "WEREWOLF":
                werewolfs.append(player["name"])
        if werewolfs:
            werewolf_info = GAME_PROMPTS["werewolf_info"].format(', '.join(werewolfs))
            self.manager.broadcast_to_player(
                "WEREWOLF",
                werewolf_info,
            )
        # 开始第一夜
        self.night_phase()

    def night_phase(self):
        """夜晚阶段. 狼人行动, 预言家行动, 女巫行动，增加异常处理"""
        try:
            self.state["night"] += 1
            night_number = self.state["night"]
            self.state["phase"] = GAME_PHASES["night"].format(str(night_number))
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    PLAYER_PROMPTS["death_message"],
                    "speech",
                ),
            )
        except Exception as e:
            self.server.send_message(
                "系统", GAME_PROMPTS["night_phase_error"].format(str(e)), "error"
            )

    def day_phase(self):
        """白天阶段. 发言, 投票，增加异常处理"""
        try:
            self.state["phase"] = GAME_PHASES["day"]
            day_number = self.state["night"]
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    GAME_PROMPTS["day_start"].format(day_number),
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
                    GAME_PROMPTS["day_phase"],
                )
            self.vote_phase()
        except Exception as e:
            self.server.send_message(
                "系统", GAME_PROMPTS["day_phase_error"].format(str(e)), "error"
            )

    def vote_phase(self):
        """投票阶段，增加异常处理"""
        try:
            self.state["phase"] = GAME_PHASES["vote"]
            day_number = self.state["night"]
            alive_players = []
            for player in self.manager.players_state:
                if player["alive"]:
                    alive_players.append(player["name"])
            vote_message = GAME_PROMPTS["vote_phase"].format(
                day_number, ", ".join(alive_players)
            )
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
            self.server.send_message(
                "系统", GAME_PROMPTS["vote_phase_error"].format(str(e)), "error"
            )

    def check_game_end(self):
        """检查游戏是否结束，增加异常处理"""
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
                end_message = GAME_PROMPTS["villagers_win"]
                self.state["phase"] = GAME_PHASES["villagers_win"]
            elif alive_werewolves >= alive_villagers:
                end_message = GAME_PROMPTS["werewolves_win"]
                self.state["phase"] = GAME_PHASES["werewolves_win"]
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
            self.server.send_message(
                "系统", GAME_PROMPTS["game_end_error"].format(str(e)), "error"
            )

    def game_run(self):
        """游戏主循环，增加异常处理"""
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
            self.server.send_message(
                "系统", GAME_PROMPTS["main_loop_error"].format(str(e)), "error"
            )
