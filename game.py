from manager import Manager


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
            "werewolves": [],    # 狼人列表，用于让狼人互相知晓
            "day_voted": None,   # 白天投票出局的玩家
        }

    def parse_order(self, order):  # 之后会用ai分析指令
        # 检查是否是开始游戏指令
        if "开始游戏" in order or "0" in order:
            self.game_start()
            # 游戏开始时已经进入第零夜，不需要再调用night_phase
            return

        # 检查是否是自动流程指令
        if "自动" in order or "auto" in order:
            self.auto_game_flow()
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
                self.server.send_message("系统", "未解析的指令", "thought")

    def auto_game_flow(self):
        """自动执行游戏流程，从当前阶段开始自动进行到游戏结束"""
        # 检查游戏是否已经开始
        if self.state["phase"] == "欢迎来到狼人杀！":
            self.game_start()
        
        # 循环执行游戏流程，直到游戏结束
        while not ("游戏结束" in self.state["phase"]):
            current_phase = self.state["phase"]
            
            # 根据当前阶段决定下一步
            if "天亮了" in current_phase or "游戏开始" in current_phase:
                self.day_phase()
            elif "白天发言阶段" in current_phase:
                self.vote_phase()
            elif "投票阶段" in current_phase or "投票结束" in current_phase:
                self.night_phase()
            else:
                # 如果是夜晚阶段，等待夜晚结束
                if "夜" in current_phase and "天亮了" not in current_phase:
                    # 夜晚阶段已经在night_phase中处理完成
                    # 这里只是为了防止循环卡住
                    break
                    
            # 添加一个短暂延迟，避免过快循环
            import time
            time.sleep(1)
        
        # 游戏结束提示
        self.server.send_message(
            "系统",
            "游戏已自动执行完毕！",
            "speech",
        )

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
        # 初始化游戏，分配角色（这会创建新的Player对象，清空AI玩家的记忆）
        self.game_init()
        
        # 宣读游戏规则
        temp = self.server.send_message(
            "系统",
            "下面宣读本场游戏规则...<br><br>" + self.rules,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
        
        # 通知每个玩家他们的角色
        for player in self.state["players"]:
            role_message = f"你的角色是：{player['role']}"
            role_info = self.server.send_message(
                "系统",
                role_message,
                "thought",
                room=player["role"]
            )
            # 单独通知每个玩家
            for p in self.manager.players_object:
                if p.name == player["name"]:
                    p.listen(role_info)
        
        # 游戏开始后直接进入第零夜
        self.night_phase()

    def night_phase(self):
        """夜晚阶段，包括狼人行动、预言家查验、女巫救人/毒人"""
        # 游戏开始时是第零夜，之后每次调用night_phase递增
        self.state["current_night"] += 1
        night_number = self.state["current_night"]
        night_display = "零" if night_number == 0 else str(night_number)
        self.state["phase"] = f"第{night_display}夜"
        
        # 1. 狼人行动
        self.werewolf_act()
        
        # 2. 预言家查验
        self.seer_act()
        
        # 3. 女巫救人/毒人
        self.witch_act()
        
        # 夜晚结束，准备进入白天
        self.state["phase"] = "天亮了"
        # 公布夜晚死亡情况
        if self.state["killed_player"] is not None:
            death_message = f"昨夜{self.state['killed_player']}被杀死了。"
            # 更新玩家状态
            for player in self.state["players"]:
                if player["name"] == self.state["killed_player"]:
                    player["alive"] = False
        else:
            death_message = "昨晚是平安夜，没有人被杀死。"
            
        temp = self.server.send_message(
            "系统",
            death_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
    
    def werewolf_act(self):
        """狼人行动阶段"""
        self.state["phase"] = "天黑请闭眼，狼人请睁眼。"
        
        # 发送系统消息给所有玩家
        night_number = self.state['current_night']
        night_display = "零" if night_number == 0 else str(night_number)
        night_start_message = f"天黑请闭眼，狼人请睁眼。现在是第{night_display}夜。"
        temp = self.server.send_message(
            "系统",
            night_start_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
        
        # 确保狼人列表是最新的
        self.state["werewolves"] = []
        for player in self.state["players"]:
            if player["role"] == "WEREWOLF" and player["alive"]:
                self.state["werewolves"].append(player["name"])
        
        # 先让狼人知道彼此的身份
        if len(self.state["werewolves"]) > 1:
            werewolf_info = f"你的同伴狼人是: {', '.join(self.state['werewolves'])}。请与你的同伴协商选择一个击杀目标。"
        else:
            werewolf_info = "你是唯一的狼人。请选择一个击杀目标。"
            
        werewolf_info_message = self.server.send_message(
            "系统", 
            werewolf_info, 
            "thought", 
            room="WEREWOLF"
        )
        self.manager.broadcast_to_player(
            "WEREWOLF",
            werewolf_info_message,
        )
        
        # 让狼人选择击杀目标
        # 获取存活的非狼人玩家列表
        alive_non_werewolves = []
        for player in self.state["players"]:
            if player["role"] != "WEREWOLF" and player["alive"]:
                alive_non_werewolves.append(player["name"])
                
        night_number = self.state['current_night']
        night_display = "零" if night_number == 0 else str(night_number)
        werewolf_prompt = f"现在是第{night_display}夜，请选择你们要击杀的人，可选目标: {', '.join(alive_non_werewolves)}。请明确指出目标玩家的名字，格式为'我选择击杀XXX'。"
        system_message = self.server.send_message(
            "系统", 
            werewolf_prompt, 
            "thought", 
            room="WEREWOLF"
        )
        # 广播系统消息给所有狼人
        self.manager.broadcast_to_player(
            "WEREWOLF",
            system_message,
        )
        # 让狼人行动并广播他们的行动给所有狼人
        self.manager.let_player_act(
            "WEREWOLF",
            werewolf_prompt,
        )
        
        # 这里应该有狼人选择的逻辑，暂时模拟一下
        # 实际应该从狼人的回复中解析出目标玩家
        # 简化处理：假设狼人选择了第一个非狼人玩家
        for player in self.state["players"]:
            if player["role"] != "WEREWOLF" and player["alive"]:
                self.state["killed_player"] = player["name"]
                break
    
    def seer_act(self):
        """预言家行动阶段"""
        self.state["phase"] = "狼人请闭眼，预言家请睁眼。"
        
        # 发送系统消息给所有玩家
        night_number = self.state['current_night']
        night_display = "零" if night_number == 0 else str(night_number)
        seer_phase_message = f"狼人请闭眼，预言家请睁眼。现在是第{night_display}夜。"
        temp = self.server.send_message(
            "系统",
            seer_phase_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
        
        # 检查是否有预言家存活
        seer_alive = False
        for player in self.state["players"]:
            if player["role"] == "SEER" and player["alive"]:
                seer_alive = True
                break
                
        if not seer_alive:
            return  # 如果预言家已死亡，跳过此阶段
        
        # 获取可查验的玩家列表（排除已查验的玩家）
        checkable_players = []
        for player in self.state["players"]:
            if player["alive"] and player["name"] not in self.state["seer_checked"]:
                checkable_players.append(player["name"])
        
        # 让预言家选择查验目标
        night_number = self.state['current_night']
        night_display = "零" if night_number == 0 else str(night_number)
        seer_prompt = f"现在是第{night_display}夜，请选择你要查验的人，可选目标: {', '.join(checkable_players)}。请明确指出目标玩家的名字，格式为'我选择查验XXX'。"
        system_message = self.server.send_message(
            "系统", 
            seer_prompt, 
            "thought", 
            room="SEER"
        )
        self.manager.broadcast_to_player(
            "SEER",
            system_message,
        )
        
        # 让预言家行动
        self.manager.let_player_act(
            "SEER",
            seer_prompt,
        )
        
        # 这里应该有预言家选择的逻辑，暂时模拟一下
        # 实际应该从预言家的回复中解析出目标玩家
        # 简化处理：假设预言家选择了第一个活着的玩家
        checked_player = None
        for player in self.state["players"]:
            if player["alive"] and player["name"] not in self.state["seer_checked"]:
                checked_player = player
                self.state["seer_checked"].append(player["name"])
                break
                
        if checked_player:
            # 告知预言家查验结果
            is_werewolf = "是狼人" if checked_player["role"] == "WEREWOLF" else "不是狼人"
            result_message = f"{checked_player['name']}{is_werewolf}"
            result = self.server.send_message(
                "系统", 
                result_message, 
                "thought", 
                room="SEER"
            )
            self.manager.broadcast_to_player(
                "SEER",
                result,
            )
    
    def witch_act(self):
        """女巫行动阶段"""
        self.state["phase"] = "预言家请闭眼，女巫请睁眼。"
        
        # 发送系统消息给所有玩家
        night_number = self.state['current_night']
        night_display = "零" if night_number == 0 else str(night_number)
        witch_phase_message = f"预言家请闭眼，女巫请睁眼。现在是第{night_display}夜。"
        temp = self.server.send_message(
            "系统",
            witch_phase_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
        
        # 检查是否有女巫存活
        witch_alive = False
        for player in self.state["players"]:
            if player["role"] == "WITCH" and player["alive"]:
                witch_alive = True
                break
                
        # 如果女巫已死亡，或者解药和毒药都已用完，跳过此阶段
        if not witch_alive or (self.state["witch_saved"] and self.state["witch_poisoned"]):
            return
        
        # 告知女巫今晚谁死了
        if self.state["killed_player"] is not None:
            death_info = f"今晚{self.state['killed_player']}被杀死了。"
        else:
            death_info = "今晚是平安夜，没有人被杀死。"
            
        # 根据女巫的药水状态提供选项
        if not self.state["witch_saved"] and self.state["killed_player"] is not None:
            death_info += f"你有一瓶解药，是否要使用？请回答'我选择救{self.state['killed_player']}'或'我选择不救'。"
        elif not self.state["witch_poisoned"]:
            # 获取可毒杀的玩家列表
            poisonable_players = []
            for player in self.state["players"]:
                if player["alive"] and player["role"] != "WITCH":
                    poisonable_players.append(player["name"])
            
            death_info += f"你有一瓶毒药，是否要使用？如果使用，请指明毒杀的目标，格式为'我选择毒杀XXX'。可选目标: {', '.join(poisonable_players)}"
        else:
            death_info += "你的药水已经用完了，无法行动。"
        
        system_message = self.server.send_message(
            "系统", 
            death_info, 
            "thought", 
            room="WITCH"
        )
        self.manager.broadcast_to_player(
            "WITCH",
            system_message,
        )
        
        # 让女巫行动
        self.manager.let_player_act(
            "WITCH",
            "请做出你的选择",
        )
        
        # 这里应该有女巫选择的逻辑，暂时模拟一下
        # 实际应该从女巫的回复中解析出是否救人或毒人
        # 简化处理：假设女巫第一晚使用解药，之后使用毒药
        if not self.state["witch_saved"] and self.state["killed_player"] is not None:
            # 使用解药
            self.state["witch_saved"] = True
            self.state["killed_player"] = None  # 救活被杀的人
        elif not self.state["witch_poisoned"]:
            # 使用毒药
            self.state["witch_poisoned"] = True
            # 假设毒杀第一个非女巫的活着的玩家
            for player in self.state["players"]:
                if player["role"] != "WITCH" and player["alive"] and player["name"] != self.state["killed_player"]:
                    # 如果killed_player已经有值，说明有人被狼人杀死，现在又有人被毒死
                    if self.state["killed_player"] is None:
                        self.state["killed_player"] = player["name"]
                    else:
                        # 额外记录被毒死的人
                        player["alive"] = False
                    break
                    
    def day_phase(self):
        """白天发言阶段"""
        self.state["phase"] = "白天发言阶段"
        
        # 发送系统消息，开始白天发言
        # 显示当前存活玩家情况
        alive_players = [player["name"] for player in self.state["players"] if player["alive"]]
        # 天数应该是夜晚数+1，因为第零夜后是第一天
        day_number = self.state['current_night']
        day_message = f"现在是第{day_number}天白天时间，存活玩家: {', '.join(alive_players)}。请各位玩家依次发言，分析昨天的情況，找出狼人。"
        temp = self.server.send_message(
            "系统",
            day_message,
            "speech",
        )
        self.manager.broadcast_to_player(
            "ALL",
            temp,
        )
        
        # 让所有存活玩家依次发言
        alive_players = [player for player in self.state["players"] if player["alive"]]
        for i, player in enumerate(alive_players):
            # 提示当前玩家发言
            day_number = self.state['current_night']
            player_prompt = f"现在是第{day_number}天，轮到{player['name']}发言，发言顺序{i+1}/{len(alive_players)}"
            speak_message = self.server.send_message(
                "系统",
                player_prompt,
                "speech",
            )
            self.manager.broadcast_to_player(
                "ALL",
                speak_message,
            )
            
            # 让玩家发言
            self.manager.let_player_act(
                "ALL",
                "请分析场上局势，表达你的看法，可以质疑其他玩家或为自己辩护。"
            )
            
            # 给玩家一些时间思考
            thinking_message = "其他玩家正在思考中..."
            think_msg = self.server.send_message(
                "系统",
                thinking_message,
                "thought",
            )
            self.manager.broadcast_to_player(
                "ALL",
                think_msg,
            )
            
    def vote_phase(self):
        """投票阶段"""
        self.state["phase"] = "投票阶段"
        
        # 获取存活玩家列表
        alive_players = [player["name"] for player in self.state["players"] if player["alive"]]
        
        # 发送系统消息，开始投票
        day_number = self.state['current_night']
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
        day_number = self.state['current_night']
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
