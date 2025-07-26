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
        """
        处理游戏指令并分发给对应角色
        """

        try:
            match order:
                case "auto":
                    self.game_run()
                case _:
                    self.server.send_message(
                        "系统", GAME_PROMPTS["unknown_command"].format(order), "thought"
                    )
        except Exception as e:
            self.server.send_message(
                "系统", GAME_PROMPTS["parse_order_error"].format(str(e)), "error"
            )

    def game_init(self):
        """
        初始化游戏, 分配角色.
        创建新的Player对象, 清空AI玩家的记忆
        """

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
        """
        开始游戏, 通知所有玩家游戏开始
        """

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
                GAME_PROMPTS["player_list"].format(
                    ", ".join([player["name"] for player in self.state["players"]])
                )
                + "\n"
                + GAME_PROMPTS["role_list"].format(
                    ", ".join([player["role"] for player in self.state["players"]])
                ),
                "speech",
            ),
        )
        # 让狼人知晓友方信息
        werewolfs = []
        for player in self.state["players"]:
            if player["role"] == "WEREWOLF":
                werewolfs.append(player["name"])
        if werewolfs:
            werewolfs = GAME_PROMPTS["werewolf_list"].format(", ".join(werewolfs))
            self.manager.broadcast_to_player(
                "WEREWOLF",
                werewolfs,
            )

    def night_phase(self):
        """
        夜晚阶段. 狼人行动, 预言家行动, 女巫行动
        """

        try:
            self.state["night"] += 1
            night_number = self.state["night"]
            self.state["phase"] = GAME_PHASES["night"].format(str(night_number))
            
            # 通知所有玩家进入夜晚阶段
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    GAME_PROMPTS["night_start"],
                    "speech",
                ),
            )
            
            # 获取存活玩家列表
            alive_players = []
            for player in self.manager.players_state:
                if player["alive"]:
                    alive_players.append(player["name"])
            
            # 狼人行动阶段
            werewolf_prompt = GAME_PROMPTS.get("werewolf_action", "狼人请睁眼，请选择你要击杀的对象: {}").format(
                ", ".join(alive_players)
            )
            self.manager.broadcast_to_player(
                "WEREWOLF",
                self.server.send_message(
                    "系统",
                    werewolf_prompt,
                    "speech",
                ),
            )
            
            # 让狼人进行选择
            werewolf_target = None
            for player in self.state["players"]:
                if player["role"] == "WEREWOLF" and player["alive"]:
                    response = self.manager.let_player_act(
                        player["name"],
                        werewolf_prompt
                    )
                    # 解析狼人的选择
                    player_obj = next((p for p in self.manager.players_object if p.name == player["name"]), None)
                    if player_obj and response and "content" in response:
                        target = player_obj.parse_action(response["content"], 'kill')
                        if target and target in alive_players:
                            werewolf_target = target
                            break
                    
                    # 如果没有成功解析到目标，默认选择一个非狼人玩家
                    if not werewolf_target:
                        for target in alive_players:
                            target_role = next((p["role"] for p in self.manager.players_state if p["name"] == target), None)
                            if target_role != "WEREWOLF":
                                werewolf_target = target
                                break
            
            # 预言家行动阶段
            seer_prompt = GAME_PROMPTS.get("seer_action", "预言家请睁眼，请选择你要查验的对象: {}").format(
                ", ".join(alive_players)
            )
            self.manager.broadcast_to_player(
                "SEER",
                self.server.send_message(
                    "系统",
                    seer_prompt,
                    "speech",
                ),
            )
            
            # 让预言家进行选择
            for player in self.state["players"]:
                if player["role"] == "SEER" and player["alive"]:
                    response = self.manager.let_player_act(
                        player["name"],
                        seer_prompt
                    )
                    # 解析预言家的选择
                    player_obj = next((p for p in self.manager.players_object if p.name == player["name"]), None)
                    seer_target = None
                    
                    if player_obj and response and "content" in response:
                        target = player_obj.parse_action(response["content"], 'check')
                        if target and target in alive_players:
                            seer_target = target
                    
                    # 如果没有成功解析到目标，默认选择第一个玩家
                    if not seer_target and alive_players:
                        seer_target = alive_players[0]
                        
                    if seer_target:
                        target_role = next((p["role"] for p in self.manager.players_state if p["name"] == seer_target), None)
                        is_werewolf = "是" if target_role == "WEREWOLF" else "不是"
                        seer_result = GAME_PROMPTS.get("seer_result", "你查验的玩家 {} {}狼人").format(
                            seer_target, is_werewolf
                        )
                        self.manager.broadcast_to_player(
                            "SEER",
                            self.server.send_message(
                                "系统",
                                seer_result,
                                "speech",
                            ),
                        )
            
            # 女巫行动阶段
            witch_prompt = GAME_PROMPTS.get("witch_action", "女巫请睁眼，今晚 {} 玩家被杀，你要使用解药救他吗？或者使用毒药杀死其他人？").format(
                werewolf_target if werewolf_target else "没有"
            )
            self.manager.broadcast_to_player(
                "WITCH",
                self.server.send_message(
                    "系统",
                    witch_prompt,
                    "speech",
                ),
            )
            
            # 让女巫进行选择
            witch_heal_target = None
            witch_poison_target = None
            
            for player in self.state["players"]:
                if player["role"] == "WITCH" and player["alive"]:
                    response = self.manager.let_player_act(
                        player["name"],
                        witch_prompt
                    )
                    # 解析女巫的选择
                    player_obj = next((p for p in self.manager.players_object if p.name == player["name"]), None)
                    
                    if player_obj and response and "content" in response:
                        # 检查是否使用解药
                        if player_obj.has_heal:
                            heal_target = player_obj.parse_action(response["content"], 'heal')
                            if heal_target and heal_target in [werewolf_target]:  # 只能救被狼人杀的人
                                witch_heal_target = heal_target
                                
                        # 检查是否使用毒药
                        if player_obj.has_poison:
                            poison_target = player_obj.parse_action(response["content"], 'poison')
                            if poison_target and poison_target in alive_players:
                                witch_poison_target = poison_target
                    
                    # 通知女巫使用结果
                    result_message = ""
                    if witch_heal_target:
                        result_message += f"你成功使用解药救活了 {witch_heal_target}。"
                    if witch_poison_target:
                        result_message += f"你成功使用毒药毒死了 {witch_poison_target}。"
                    if result_message:
                        self.manager.broadcast_to_player(
                            "WITCH",
                            self.server.send_message(
                                "系统",
                                result_message,
                                "speech",
                            ),
                        )
            
            # 处理夜晚结果
            death_players = []
            
            # 处理狼人击杀
            if werewolf_target and witch_heal_target != werewolf_target:
                # 如果狼人击杀了目标且女巫没有救人
                death_players.append(werewolf_target)
            
            # 处理女巫毒药
            if witch_poison_target:
                death_players.append(witch_poison_target)
            
            # 更新被杀玩家状态
            for death_player in death_players:
                for player in self.manager.players_state:
                    if player["name"] == death_player:
                        player["alive"] = False
                        break
            
            # 通知所有玩家夜晚结果
            if death_players:
                death_message = GAME_PROMPTS.get("night_result", "天亮了，昨晚 {} 玩家被杀").format(
                    "、".join(death_players)
                )
                self.manager.broadcast_to_player(
                    "ALL",
                    self.server.send_message(
                        "系统",
                        death_message,
                        "speech",
                    ),
                )
            else:
                # 如果没有人被杀（平安夜）
                no_death_message = GAME_PROMPTS.get("no_death", "天亮了，昨晚是平安夜，没有人被杀")
                self.manager.broadcast_to_player(
                    "ALL",
                    self.server.send_message(
                        "系统",
                        no_death_message,
                        "speech",
                    ),
                )
        except Exception as e:
            self.server.send_message(
                "系统", GAME_PROMPTS["night_phase_error"].format(str(e)), "error"
            )

    def day_phase(self):
        """
        白天阶段. 发言, 投票
        """

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
        """
        投票阶段
        """

        try:
            self.state["phase"] = GAME_PHASES["vote"]
            day_number = self.state["night"]
            alive_players = []
            for player in self.manager.players_state:
                if player["alive"]:
                    alive_players.append(player["name"])
                    
            # 重置所有玩家的投票状态
            for player in self.manager.players_state:
                player["voted"] = -1
                
            # 发送投票开始消息
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
            
            # 让每个存活的玩家进行投票
            votes = {}  # 用于统计每个玩家获得的票数
            for player_name in alive_players:
                # 初始化票数统计
                votes[player_name] = 0
                
            # 让每个存活的玩家进行投票
            for player_name in alive_players:
                response = self.manager.let_player_act(
                    player_name,
                    GAME_PROMPTS["vote_start"]
                )
                
                # 解析投票目标
                player_obj = next((p for p in self.manager.players_object if p.name == player_name), None)
                if player_obj and response and "content" in response:
                    vote_target = player_obj.parse_action(response["content"], 'vote')
                    
                    # 如果成功解析到投票目标且目标是存活玩家
                    if vote_target and vote_target in alive_players:
                        # 更新玩家的投票状态
                        for player in self.manager.players_state:
                            if player["name"] == player_name:
                                player["voted"] = vote_target
                                votes[vote_target] += 1
                                break
            
            # 统计投票结果
            vote_summary = []
            for player_name in alive_players:
                vote_summary.append(f"{player_name}: {votes[player_name]}票")
            
            # 发送投票统计结果
            self.manager.broadcast_to_player(
                "ALL",
                self.server.send_message(
                    "系统",
                    GAME_PROMPTS["vote_summary"].format(", ".join(vote_summary)),
                    "speech",
                ),
            )
            
            # 找出得票最多的玩家
            max_votes = max(votes.values()) if votes else 0
            most_voted = [name for name, vote_count in votes.items() if vote_count == max_votes]
            
            # 如果有平局
            if len(most_voted) > 1 or max_votes == 0:
                self.manager.broadcast_to_player(
                    "ALL",
                    self.server.send_message(
                        "系统",
                        GAME_PROMPTS["vote_tie"],
                        "speech",
                    ),
                )
            else:
                # 处理投票出局
                voted_out = most_voted[0]
                
                # 更新被投出玩家的状态
                for player in self.manager.players_state:
                    if player["name"] == voted_out:
                        player["alive"] = False
                        break
                
                # 通知所有玩家投票结果
                self.manager.broadcast_to_player(
                    "ALL",
                    self.server.send_message(
                        "系统",
                        GAME_PROMPTS["vote_result"].format(voted_out),
                        "speech",
                    ),
                )
                
                # 公布被投出玩家的身份
                voted_role = next((p["role"] for p in self.manager.players_state if p["name"] == voted_out), None)
                self.manager.broadcast_to_player(
                    "ALL",
                    self.server.send_message(
                        "系统",
                        f"{voted_out} 的身份是 {voted_role}",
                        "speech",
                    ),
                )
            
            # 检查游戏是否结束
            self.check_game_end()
        except Exception as e:
            self.server.send_message(
                "系统", GAME_PROMPTS["vote_phase_error"].format(str(e)), "error"
            )

    def check_game_end(self):
        """
        检查游戏是否结束
        """

        try:
            alive_werewolves = 0
            alive_villagers = 0
            for player in self.manager.players_state:
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
        """
        游戏主循环
        """

        try:
            self.game_init()
            self.game_start()
            while True:
                self.night_phase()
                self.day_phase()
                if (
                    self.state["phase"] == GAME_PHASES["villagers_win"]
                    or self.state["phase"] == GAME_PHASES["werewolves_win"]
                ):
                    break
        except Exception as e:
            self.server.send_message(
                "系统", GAME_PROMPTS["main_loop_error"].format(str(e)), "error"
            )
