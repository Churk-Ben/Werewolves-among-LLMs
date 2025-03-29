import random
from game_logic import Role, GamePhase
from deepseek_api import call_deepseek_api, generate_werewolf_prompt, generate_seer_prompt, \
    generate_witch_prompt, generate_day_discussion_prompt, generate_voting_prompt

class AIPlayer:
    def __init__(self, name, game):
        self.name = name
        self.game = game
        self.role = None
        self.thoughts = []

    def think(self, phase):
        """生成AI玩家的思考过程"""
        game_state = {
            'alive_players': [p.name for p in self.game.get_alive_players() if p.name != self.name],
            'day_count': self.game.day_count,
            'phase': phase.value,
            'night_events': getattr(self.game, 'night_events', []),
            'suspicious_points': getattr(self.game, 'suspicious_points', []),
            'wolf_target': getattr(self.game, 'wolf_target', None)
        }
        
        role_info = {
            'role': self.role.value,
            'day_count': self.game.day_count,
            'phase': phase.value
        }
        
        if phase == GamePhase.NIGHT:
            if self.role == Role.WEREWOLF:
                prompt = generate_werewolf_prompt(game_state)
            elif self.role == Role.SEER:
                prompt = generate_seer_prompt(game_state)
            elif self.role == Role.WITCH:
                prompt = generate_witch_prompt(game_state)
            else:
                return ""
        elif phase == GamePhase.DAY:
            prompt = generate_day_discussion_prompt(game_state)
        elif phase == GamePhase.VOTING:
            prompt = generate_voting_prompt(game_state)
        else:
            return ""
        
        thought = call_deepseek_api(prompt, role_info)
        if thought:
            self.thoughts.append(thought)
            return thought
        return ""
        


    def make_decision(self, phase):
        """根据思考做出决策"""
        game_state = {
            'alive_players': [p.name for p in self.game.get_alive_players() if p.name != self.name],
            'day_count': self.game.day_count,
            'phase': phase.value,
            'night_events': getattr(self.game, 'night_events', []),
            'suspicious_points': getattr(self.game, 'suspicious_points', []),
            'wolf_target': getattr(self.game, 'wolf_target', None)
        }
        
        role_info = {
            'role': self.role.value,
            'day_count': self.game.day_count,
            'phase': phase.value
        }
        
        decision_prompt = f"根据你的思考，请直接回复你要选择的目标玩家名称（或者使用药水时回复'使用'或'不使用'）。请只回复目标名称或使用决定，不要包含其他内容。"
        
        if phase == GamePhase.NIGHT:
            if self.role == Role.WEREWOLF:
                prompt = generate_werewolf_prompt(game_state) + decision_prompt
            elif self.role == Role.SEER:
                prompt = generate_seer_prompt(game_state) + decision_prompt
            elif self.role == Role.WITCH:
                prompt = generate_witch_prompt(game_state) + decision_prompt
            else:
                return None
        elif phase == GamePhase.VOTING:
            prompt = generate_voting_prompt(game_state) + decision_prompt
        else:
            return None
        
        decision = call_deepseek_api(prompt, role_info)
        if not decision:
            # 如果API调用失败，使用备用决策逻辑
            if self.role == Role.WEREWOLF:
                return self._decide_werewolf_target()
            elif self.role == Role.SEER:
                return self._decide_seer_target()
            elif self.role == Role.WITCH:
                return self._decide_witch_action()
            elif phase == GamePhase.VOTING:
                return self._decide_vote_target()
            return None
            
        # 处理决策结果
        decision = decision.strip().lower()
        if self.role == Role.WITCH:
            return decision in ['使用', 'yes', 'true']
        else:
            # 确保返回的是存活玩家的名字
            alive_players = game_state['alive_players']
            # 首先尝试完全匹配
            for player_name in alive_players:
                if player_name.lower() == decision:
                    return player_name
            # 如果没有完全匹配，尝试部分匹配
            for player_name in alive_players:
                if player_name.lower() in decision:
                    return player_name
            # 如果仍然没有匹配，使用备用决策逻辑
            if self.role == Role.WEREWOLF:
                return self._decide_werewolf_target()
            elif self.role == Role.SEER:
                return self._decide_seer_target()
            elif phase == GamePhase.VOTING:
                return self._decide_vote_target()
        return None

    def _think_as_werewolf(self):
        alive_players = [p for p in self.game.get_alive_players() if p.name != self.name]
        thoughts = [
            f"现在是第{self.game.day_count}天的夜晚。",
            "作为狼人，我需要选择一个目标。",
            "让我分析一下各个玩家："
        ]
        for player in alive_players:
            thoughts.append(f"- {player.name}看起来是个不错的目标。")
        return "\n".join(thoughts)

    def _think_as_seer(self):
        alive_players = [p for p in self.game.get_alive_players() if p.name != self.name]
        thoughts = [
            f"第{self.game.day_count}天夜晚，作为预言家，",
            "我需要选择一个玩家查看身份。",
            "让我思考一下："
        ]
        for player in alive_players:
            thoughts.append(f"- {player.name}的行为有些可疑。")
        return "\n".join(thoughts)

    def _think_as_witch(self):
        thoughts = [
            f"第{self.game.day_count}天夜晚，",
            "作为女巫，我需要决定是否使用药水。",
            "让我仔细考虑一下..."
        ]
        return "\n".join(thoughts)

    def _think_during_day(self):
        thoughts = [
            f"第{self.game.day_count}天白天。",
            "我需要仔细观察其他玩家的发言，",
            "并思考如何为自己辩护。"
        ]
        return "\n".join(thoughts)

    def _think_during_voting(self):
        alive_players = [p for p in self.game.get_alive_players() if p.name != self.name]
        thoughts = [
            "投票阶段开始了，",
            "我需要决定投票给谁。",
            "让我分析一下每个人："
        ]
        for player in alive_players:
            thoughts.append(f"- {player.name}似乎很可疑。")
        return "\n".join(thoughts)

    def _decide_werewolf_target(self):
        alive_players = [p for p in self.game.get_alive_players() if p.name != self.name]
        return random.choice(alive_players).name if alive_players else None

    def _decide_seer_target(self):
        alive_players = [p for p in self.game.get_alive_players() if p.name != self.name]
        return random.choice(alive_players).name if alive_players else None

    def _decide_witch_action(self):
        # 随机决定是否使用药水
        return random.choice([True, False])

    def _decide_vote_target(self):
        alive_players = [p for p in self.game.get_alive_players() if p.name != self.name]
        return random.choice(alive_players).name if alive_players else None