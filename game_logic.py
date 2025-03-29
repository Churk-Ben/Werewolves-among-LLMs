import random
from enum import Enum

class Role(Enum):
    WEREWOLF = "狼人"
    VILLAGER = "平民"
    WITCH = "女巫"
    SEER = "预言家"
    HUNTER = "猎人"
    GUARD = "守卫"

class GamePhase(Enum):
    WAITING = "waiting"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    ENDED = "ended"

class Player:
    def __init__(self, name, role=None):
        self.name = name
        self.role = role
        self.is_alive = True
        self.has_voted = False
        self.vote_target = None

class Game:
    def __init__(self):
        self.players = []
        self.phase = GamePhase.WAITING
        self.day_count = 0
        self.night_actions = []
        self.votes = {}
        self.winner = None

    def initialize_game(self, player_names):
        roles = [
            Role.WEREWOLF, Role.WEREWOLF,  # 2个狼人
            Role.VILLAGER, Role.VILLAGER,   # 2个平民
            Role.WITCH,                     # 1个女巫
            Role.SEER                       # 1个预言家
        ]
        random.shuffle(roles)
        
        self.players = []
        for name, role in zip(player_names, roles):
            self.players.append(Player(name, role))
        
        self.phase = GamePhase.NIGHT
        self.day_count = 1

    def get_alive_players(self):
        return [p for p in self.players if p.is_alive]

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    def check_game_end(self):
        werewolves = [p for p in self.get_alive_players() if p.role == Role.WEREWOLF]
        villagers = [p for p in self.get_alive_players() if p.role != Role.WEREWOLF]
        
        if len(werewolves) == 0:
            self.winner = "villagers"
            self.phase = GamePhase.ENDED
            return True
        elif len(werewolves) >= len(villagers):
            self.winner = "werewolves"
            self.phase = GamePhase.ENDED
            return True
        return False

    def process_night_actions(self):
        # 处理夜晚行动的结果
        self.night_events = []  # 记录夜晚发生的事件
        self.suspicious_points = []  # 记录可疑的行为
        
        # 按照角色优先级处理夜晚行动
        # 1. 狼人袭击
        werewolves = [p for p in self.get_alive_players() if p.role == Role.WEREWOLF]
        if werewolves:
            self.wolf_target = None  # 记录狼人的目标
            # 统计狼人投票
            wolf_votes = {}
            for werewolf in werewolves:
                if werewolf.vote_target:
                    if werewolf.vote_target in wolf_votes:
                        wolf_votes[werewolf.vote_target] += 1
                    else:
                        wolf_votes[werewolf.vote_target] = 1
            
            # 选择票数最多的目标
            if wolf_votes:
                max_votes = max(wolf_votes.values())
                targets = [t for t, v in wolf_votes.items() if v == max_votes]
                self.wolf_target = random.choice(targets)
                target_player = self.get_player_by_name(self.wolf_target)
                if target_player:
                    target_player.is_alive = False
                    self.night_events.append(f"{self.wolf_target}被狼人袭击")
        
        # 2. 女巫救人或毒人
        witches = [p for p in self.get_alive_players() if p.role == Role.WITCH]
        if witches:
            for witch in witches:
                if witch.vote_target is not None:  # 确保有决策
                    if isinstance(witch.vote_target, bool):  # 使用解药
                        if witch.vote_target and self.wolf_target:
                            target_player = self.get_player_by_name(self.wolf_target)
                            if target_player:
                                target_player.is_alive = True
                                self.night_events.append(f"{self.wolf_target}被女巫救活")
                                self.wolf_target = None  # 清除狼人目标，因为已被救活
                    else:  # 使用毒药
                        target_player = self.get_player_by_name(witch.vote_target)
                        if target_player and target_player.is_alive:
                            target_player.is_alive = False
                            self.night_events.append(f"{witch.vote_target}被毒死")
        
        # 3. 预言家查验
        seers = [p for p in self.get_alive_players() if p.role == Role.SEER]
        if seers:
            for seer in seers:
                if seer.vote_target:
                    target_player = self.get_player_by_name(seer.vote_target)
                    if target_player:
                        if target_player.role == Role.WEREWOLF:
                            self.suspicious_points.append(f"{seer.vote_target}被发现是狼人")
                        else:
                            self.suspicious_points.append(f"{seer.vote_target}是好人")
        
        # 重置投票状态
        for player in self.players:
            player.vote_target = None
            
        # 检查游戏是否结束
        self.check_game_end()

    def process_vote(self):
        if not self.votes:
            return None
        
        # 统计投票
        vote_count = {}
        for target in self.votes.values():
            if target in vote_count:
                vote_count[target] += 1
            else:
                vote_count[target] = 1
        
        # 找出票数最多的玩家
        max_votes = max(vote_count.values())
        eliminated = [p for p, v in vote_count.items() if v == max_votes]
        
        if len(eliminated) == 1:
            player = self.get_player_by_name(eliminated[0])
            if player:
                player.is_alive = False
                return player.name
        
        return None  # 平票或无人被投出

    def next_phase(self):
        if self.phase == GamePhase.NIGHT:
            self.process_night_actions()
            self.phase = GamePhase.DAY
        elif self.phase == GamePhase.DAY:
            self.phase = GamePhase.VOTING
        elif self.phase == GamePhase.VOTING:
            eliminated_player = self.process_vote()
            self.votes = {}
            if not self.check_game_end():
                self.phase = GamePhase.NIGHT
                self.day_count += 1
            return eliminated_player
        
        return None