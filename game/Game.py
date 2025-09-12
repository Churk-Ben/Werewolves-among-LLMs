import random
import yaml
import time
from typing import List, Dict, Optional
from game.logger import GameLogger
from game.models import Role, DeathReason
from game.player import Player
from game.ui import h1, h2, prompt_for_choice


class WerewolfGame:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.roles: Dict[str, int] = {}
        self.all_player_names: List[str] = []
        self.killed_player: Optional[str] = None
        self.last_guarded: Optional[str] = None
        self.witch_save_used = False
        self.witch_poison_used = False
        self.day_number = 0

        ## 游戏日志
        self.logger = GameLogger()

    # 工具方法
    def _get_alive_players(self, roles: Optional[List[Role]] = None) -> List[str]:
        """获取存活的玩家列表,可根据角色筛选"""
        alive_players = []
        role_values = []
        if roles:
            for r in roles:
                role_values.append(r.value)

        for name, p in self.players.items():
            if p.is_alive:
                if roles is None or p.role in role_values:
                    alive_players.append(name)
        return alive_players

    def _get_player_by_role(self, role: Role) -> Optional[Player]:
        """根据角色获取玩家对象"""
        for p in self.players.values():
            if p.role == role.value and p.is_alive:
                return p
        return None

    def _cancel(self):
        """取消游戏"""
        self.logger.log_public_event(
            f"游戏已取消.",
            self.all_player_names,
        )
        self.logger.close()
        self.players.clear()
        self.roles.clear()
        self.all_player_names.clear()
        self.killed_player = None
        self.last_guarded = None
        self.witch_save_used = False
        self.witch_poison_used = False
        self.day_number = 0

    # 游戏初始化
    def setup_game(self):
        """初始化游戏"""
        ## 加载游戏配置
        ### 后台逻辑
        try:
            with open("config.yaml", "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                player_count = len(config["players"])
                player_names = [player["name"] for player in config["players"]]
                self.all_player_names = player_names

        except (FileNotFoundError, KeyError, ValueError):
            print("#! 配置文件有错, 请检查配置文件.")

        except Exception as e:
            print(f"#! 未知错误: {str(e)}")

        if player_count == 6:
            self.roles = {
                Role.WEREWOLF.value: 2,
                Role.VILLAGER.value: 2,
                Role.SEER.value: 1,
                Role.WITCH.value: 1,
            }

        else:
            self.roles = {
                Role.WEREWOLF.value: max(1, player_count // 4),
                Role.SEER.value: 1,
                Role.WITCH.value: 1,
                Role.HUNTER.value: 1,
                Role.GUARD.value: 1,
            }
            self.roles[Role.VILLAGER.value] = player_count - sum(self.roles.values())

        ### 前台打印
        h2("#@ 本局游戏角色配置")
        role_config = []
        for role, count in self.roles.items():
            if count > 0:
                role_config.append(f"{role.capitalize()} {count}人")
        print("#@ " + ", ".join(role_config))

        ### 更新日志
        self.logger.log_public_event(
            f"本局玩家人数: {player_count}",
            self.all_player_names,
        )
        self.logger.log_public_event(
            f"角色卡配置: {role_config}",
            self.all_player_names,
        )
        self.logger.log_public_event(
            f"玩家 {player_names} 已加入游戏.",
            self.all_player_names,
        )

        ## 随机分发角色卡
        ### 后台逻辑
        role_list = []
        for role, count in self.roles.items():
            for _ in range(count):
                role_list.append(role)
        random.shuffle(role_list)

        for name, role in zip(player_names, role_list):
            player = Player(name, role)
            player.set_logger(self.logger)
            self.players[name] = player

        werewolves = self._get_alive_players([Role.WEREWOLF])

        ### 前台打印
        h1("#@ 角色分配完成, 正在分发身份牌...")
        for name, player in self.players.items():
            # 通知并打印
            time.sleep(0.3)
            print(f"\n{name}, 你的身份是: {player.role.capitalize()}")
            if player.role == Role.WEREWOLF.value:
                teammates = []
                for w in werewolves:
                    if w != name:
                        teammates.append(w)
                if teammates:
                    print(f"你的狼人同伴是: {', '.join(teammates)}")
                else:
                    print("你是唯一的狼人")

        ### 更新日志
        self.logger.log_public_event(
            "角色分配完成, 正在分发身份牌...",
            self.all_player_names,
        )

        for name, player in self.players.items():
            self.logger.log_event(
                f"你的身份是: {player.role.capitalize()}",
                [player.name],
            )

            if player.role == Role.WEREWOLF.value:
                teammates = []
                for w in werewolves:
                    if w != name:
                        teammates.append(w)
                if teammates:
                    self.logger.log_event(
                        f"你的狼人同伴是: {', '.join(teammates)}",
                        [player.name],
                    )
                else:
                    self.logger.log_event(
                        "你是唯一的狼人",
                        [player.name],
                    )

        ## 游戏开始
        h1("#: 游戏开始. 天黑, 请闭眼.")
        self.logger.log_public_event(
            "游戏开始. 天黑, 请闭眼.",
            self.all_player_names,
        )

    # 夜晚阶段
    def night_phase(self):
        """夜晚阶段"""
        self.day_number += 1
        h1(f"#@ 第 {self.day_number} 天夜晚降临")
        self.logger.log_public_event(
            f"第 {self.day_number} 天夜晚降临",
            self.all_player_names,
        )
        self.killed_player = None
        for p in self.players.values():
            p.is_guarded = False
        alive_players = self._get_alive_players()

        ## 1. 守卫行动
        guard = self._get_player_by_role(Role.GUARD)
        if guard:
            ### 获取输入
            h2("#@ 守卫请睁眼")
            prompt = f"守卫, 请选择你要守护的玩家 (不能连续两晚守护同一个人): "
            self.logger.log_event(
                "守卫请睁眼" + prompt,
                [guard.name],
            )

            valid_targets = []
            for p in alive_players:
                if p != self.last_guarded:
                    valid_targets.append(p)
            target = prompt_for_choice(guard, prompt, valid_targets)

            ### 后台逻辑
            self.players[target].is_guarded = True
            self.last_guarded = target

            ### 前台反馈和日志更新
            h2("#@ 守卫请闭眼")
            self.logger.log_event(
                f"你守护了 {target}",
                [guard.name],
            )
            self.logger.log_public_event(
                f"守卫行动了",
                self.all_player_names,
            )

        ## 2. 狼人行动
        werewolves = self._get_alive_players([Role.WEREWOLF])
        if werewolves:
            h2("#@ 狼人请睁眼")
            print(f"#@ 现在的狼人有: {', '.join(werewolves)}")
            self.logger.log_event(
                "狼人请睁眼" + f"现在的狼人有: {', '.join(werewolves)}",
                werewolves,
            )

            ### 交流阶段
            # 当狼人数为1时，跳过讨论环节直接进入投票
            if len(werewolves) == 1:
                print("#@ 独狼无需讨论，直接进入投票阶段")
                self.logger.log_event(
                    "独狼无需讨论，直接进入投票阶段",
                    werewolves,
                )
            else:
                h2("#@ 狼人请开始讨论")
                print("#@ 请轮流发言, 输入 '0' 表示准备好投票")
                self.logger.log_event(
                    "狼人请开始讨论, 输入 '0' 表示发言结束, 准备投票",
                    werewolves,
                )
                ready_to_vote = set()
                discussion_rounds = 0
                max_discussion_rounds = 5  # 最多5轮讨论

                while (
                    len(ready_to_vote) < len(werewolves)
                    and discussion_rounds < max_discussion_rounds
                ):
                    discussion_rounds += 1
                    for wolf in werewolves:
                        if wolf in ready_to_vote:
                            continue
                        wolf_player = self.players[wolf]
                        action = wolf_player.speak(
                            f"{wolf}, 请发言或输入 '0' 准备投票: "
                        )
                        if action == "0":
                            ready_to_vote.add(wolf)
                            print(
                                f"#@ ({wolf} 已准备好投票 {len(ready_to_vote)}/{len(werewolves)})"
                            )
                            self.logger.log_event(
                                f"({wolf} 已准备好投票 {len(ready_to_vote)}/{len(werewolves)})",
                                werewolves,
                            )
                        elif action:
                            print(f"#: [狼人频道] {wolf} 发言: {action}")
                            self.logger.log_event(
                                f"[狼人频道] {wolf} 发言: {action}",
                                werewolves,
                            )

                # 如果达到最大讨论轮次，强制进入投票阶段
                if discussion_rounds >= max_discussion_rounds and len(
                    ready_to_vote
                ) < len(werewolves):
                    print(
                        f"#@ 讨论已达到最大轮次({max_discussion_rounds}轮)，强制进入投票阶段"
                    )
                    self.logger.log_event(
                        f"讨论已达到最大轮次({max_discussion_rounds}轮)，强制进入投票阶段",
                        werewolves,
                    )
                    ready_to_vote = set(werewolves)  # 强制所有狼人准备投票

            ### 投票阶段
            h2("#@ 狼人请投票")
            self.logger.log_event(
                "狼人请投票",
                werewolves,
            )
            while True:
                votes = {name: 0 for name in alive_players}
                for wolf_name in werewolves:
                    wolf_player = self.players[wolf_name]
                    prompt = f"{wolf_name}, 请投票选择要击杀的目标: "
                    target = prompt_for_choice(wolf_player, prompt, alive_players)
                    votes[target] += 1

                max_votes = 0
                kill_targets = []
                if votes:
                    max_votes = max(votes.values())
                    if max_votes > 0:
                        kill_targets = []
                        for name, count in votes.items():
                            if count == max_votes:
                                kill_targets.append(name)

                if len(kill_targets) == 1:
                    self.killed_player = kill_targets[0]
                    print(f"#@ 狼人达成一致, 选择了击杀 {self.killed_player}")
                    self.logger.log_event(
                        f"狼人投票决定击杀 {self.killed_player}",
                        werewolves,
                    )
                    break
                else:
                    print("#@ 狼人投票出现平票, 请重新商议并投票")
                    self.logger.log_event(
                        "狼人投票出现平票, 请重新商议并投票",
                        werewolves,
                    )

            ### 前台反馈和日志更新
            h2(f"#@ 狼人请闭眼")
            self.logger.log_event(
                f"你击杀了 {self.killed_player}",
                werewolves,
            )
            self.logger.log_public_event(
                f"狼人行动了",
                self.all_player_names,
            )

        ## 3. 预言家行动
        seer_player = self._get_player_by_role(Role.SEER)
        if seer_player:
            ### 获取输入
            h2("#@ 预言家请睁眼")
            prompt = "预言家, 请选择要查验的玩家: "
            self.logger.log_event(
                "预言家请睁眼. 请选择要你要查验的玩家: ",
                [seer_player.name],
            )
            target = prompt_for_choice(seer_player, prompt, alive_players)

            ### 后台逻辑
            role = self.players[target].role
            identity = "狼人" if role == Role.WEREWOLF.value else "好人"
            print(f"#@ 查验结果: {target} 的身份是 {identity}")

            ### 前台反馈和日志更新
            h2("#@ 预言家请闭眼")
            self.logger.log_event(
                f"你查验了 {target} 的身份, 结果为 {identity}",
                [seer_player.name],
            )
            self.logger.log_public_event(
                f"预言家行动了",
                self.all_player_names,
            )

        ## 4. 女巫行动
        witch_player = self._get_player_by_role(Role.WITCH)
        if witch_player:
            ### 获取输入
            h2("#@ 女巫请睁眼")
            self.logger.log_event(
                "女巫请睁眼",
                [witch_player.name],
            )

            #### 处理守护和击杀
            if self.killed_player and self.players[self.killed_player].is_guarded:
                print(f"#@ 今晚是个平安夜, {self.killed_player} 被守护了")
                self.logger.log_public_event(
                    f"今晚是个平安夜, {self.killed_player} 被守护了",
                    self.all_player_names,
                )
                actual_killed = None
            else:
                if self.killed_player:
                    print(f"#@ 今晚 {self.killed_player} 被杀害了")
                    self.logger.log_event(
                        f"今晚 {self.killed_player} 被杀害了",
                        [witch_player.name],
                    )
                actual_killed = self.killed_player

            ### 使用解药
            if not self.witch_save_used and actual_killed:
                prompt = f"女巫, 你要使用解药吗? "
                if prompt_for_choice(witch_player, prompt, ["y", "n"]) == "y":
                    actual_killed = None
                    self.witch_save_used = True
                    print(f"#@ 你使用解药救了 {self.killed_player}")
                    self.logger.log_event(
                        f"你使用解药救了 {self.killed_player}",
                        [witch_player.name],
                    )
                    self.logger.log_public_event(
                        f"女巫使用了解药",
                        self.all_player_names,
                    )

            ### 使用毒药
            if not self.witch_poison_used:
                prompt = "女巫, 你要使用毒药吗? "
                if prompt_for_choice(witch_player, prompt, ["y", "n"]) == "y":
                    poison_prompt = "请选择要毒杀的玩家: "
                    target = prompt_for_choice(
                        witch_player, poison_prompt, alive_players
                    )
                    if actual_killed is None:
                        actual_killed = target
                    else:
                        self.handle_death(target, DeathReason.POISONED_BY_WITCH)
                    self.witch_poison_used = True
                    print(f"#@ 你使用毒药毒了 {target} ")
                    self.logger.log_event(
                        f"你使用毒药毒了 {target}",
                        [witch_player.name],
                    )
                    self.logger.log_public_event(
                        f"女巫使用了毒药",
                        self.all_player_names,
                    )
            self.killed_player = actual_killed

            ### 前台反馈和日志更新
            h2("#@ 女巫请闭眼")
            self.logger.log_public_event(
                f"女巫行动了",
                self.all_player_names,
            )

    def handle_death(self, player_name: str, reason: DeathReason):
        """处理玩家死亡"""
        if player_name and self.players[player_name].is_alive:
            self.players[player_name].is_alive = False
            print(f"#! {player_name} 死了, 原因是{reason.value}")
            self.logger.log_public_event(
                f"{player_name} 死了, 原因是 {reason.value}",
                self.all_player_names,
            )

            # 判断是否可以发表遗言
            # 只有在首夜死亡、被投票出局或被猎人带走时才能发表遗言
            is_first_night_death = self.day_number == 1 and reason in [
                DeathReason.KILLED_BY_WEREWOLF,
                DeathReason.POISONED_BY_WITCH,
            ]
            can_have_last_words = (
                reason in [DeathReason.VOTED_OUT, DeathReason.SHOT_BY_HUNTER]
                or is_first_night_death
            )

            if can_have_last_words:
                player = self.players[player_name]
                last_words = player.speak(f"{player_name}, 请发表你的遗言: ")
                if last_words:
                    print(f"#: [遗言] {player_name} 发言: {last_words}")
                    self.logger.log_public_event(
                        f"[遗言] {player_name} 发言: {last_words}",
                        self.all_player_names,
                    )
                else:
                    print(f"#@ {player_name} 选择保持沉默, 没有留下遗言")
                    self.logger.log_public_event(
                        f"{player_name} 选择保持沉默, 没有留下遗言",
                        self.all_player_names,
                    )

            # 检查猎人技能
            if self.players[player_name].role == Role.HUNTER.value:
                self.handle_hunter_shot(player_name)

    def handle_hunter_shot(self, hunter_name: str):
        """处理猎人开枪"""
        print(f"#@ {hunter_name} 是猎人, 可以在临死前开枪带走一人")
        self.logger.log_public_event(
            f"{hunter_name} 是猎人, 可以在临死前开枪带走一人",
            self.all_player_names,
        )
        alive_players_for_shot = []
        for p in self._get_alive_players():
            if p != hunter_name:
                alive_players_for_shot.append(p)
        hunter_player = self.players[hunter_name]
        prompt = f"{hunter_name}, 请选择你要带走的玩家: "
        target = prompt_for_choice(
            hunter_player, prompt, alive_players_for_shot, allow_skip=True
        )

        if target == "skip":
            print("#@ 猎人放弃了开枪")
            self.logger.log_public_event(
                "猎人放弃了开枪",
                self.all_player_names,
            )
        else:
            self.logger.log_public_event(
                f"猎人 {hunter_name} 开枪带走了 {target}",
                self.all_player_names,
            )
            self.handle_death(target, DeathReason.SHOT_BY_HUNTER)

    # 白天阶段
    def day_phase(self):
        """白天阶段"""
        h1("#: 天亮了.")
        h2(f"#@ 现在是第 {self.day_number} 天白天")
        self.logger.log_public_event(
            f"天亮了. 现在是第 {self.day_number} 天白天",
            self.all_player_names,
        )

        if self.killed_player is None:
            print("#@ 昨晚是平安夜, 没有人死亡")
            self.logger.log_public_event(
                "昨晚是平安夜, 没有人死亡",
                self.all_player_names,
            )
        elif self.players[self.killed_player].is_guarded:
            print(f"#@ 昨晚是平安夜, {self.killed_player} 被守护了")
            self.logger.log_public_event(
                f"昨晚是平安夜, {self.killed_player} 被守护了",
                self.all_player_names,
            )
        else:
            self.handle_death(self.killed_player, DeathReason.KILLED_BY_WEREWOLF)

        alive_players = self._get_alive_players()
        h2("#@ 发言阶段")
        print(f"#@ 存活玩家: {', '.join(alive_players)}")
        self.logger.log_public_event(
            f"存活玩家: {', '.join(alive_players)}",
            self.all_player_names,
        )
        for player_name in alive_players:
            player = self.players[player_name]
            speech = player.speak(f"{player_name} 请发言 (按回车键结束发言): ")
            if speech:
                print(f"#: {player_name} 发言: {speech}")
                self.logger.log_public_event(
                    f"{player_name} 发言: {speech}",
                    self.all_player_names,
                )
            else:
                print(f"#@ {player_name} 选择过麦")
                self.logger.log_public_event(
                    f"{player_name} 选择过麦",
                    self.all_player_names,
                )

        h2("#@ 投票阶段")
        votes = {name: 0 for name in alive_players}
        vote_records = {}
        for voter_name in alive_players:
            voter_player = self.players[voter_name]
            prompt = f"{voter_name}, 请投票选择要驱逐的玩家: "
            target = prompt_for_choice(
                voter_player, prompt, alive_players, allow_skip=True
            )
            vote_records[voter_name] = target
            if target != "skip":
                votes[target] += 1

        for voter, target in vote_records.items():
            if target != "skip":
                self.logger.log_public_event(
                    f"{voter} 投票给了 {target}",
                    self.all_player_names,
                )
            else:
                self.logger.log_public_event(
                    f"{voter} 弃票了",
                    self.all_player_names,
                )

        h2("#! 计票结果")
        vote_results = ""
        for name, count in votes.items():
            if count > 0:
                vote_results += f"{name}: {count} 票\n"
                self.logger.log_public_event(
                    f"{name}: {count} 票",
                    self.all_player_names,
                )
        print("#: " + vote_results)

        max_votes = 0
        voted_out_players = []
        if votes:
            max_votes = max(votes.values())
            if max_votes > 0:
                voted_out_players = []
                for name, count in votes.items():
                    if count == max_votes:
                        voted_out_players.append(name)

        if len(voted_out_players) == 1:
            voted_player = voted_out_players[0]
            self.handle_death(voted_player, DeathReason.VOTED_OUT)
        else:
            print(f"投票结果为平票或无人投票, 本轮无人被驱逐")
            self.logger.log_public_event(
                f"投票结果为平票或无人投票, 本轮无人被驱逐",
                self.all_player_names,
            )

    def check_game_over(self) -> bool:
        """检查游戏是否结束"""
        alive_werewolves = len(self._get_alive_players([Role.WEREWOLF]))
        god_roles = [Role.SEER, Role.WITCH, Role.HUNTER, Role.GUARD]
        alive_gods = len(self._get_alive_players(god_roles))
        alive_villagers = len(self._get_alive_players([Role.VILLAGER]))

        if alive_werewolves == 0:
            print("\n好人阵营胜利! 所有狼人都被消灭了\n")
            self.logger.log_public_event(
                "游戏结束：好人胜利",
                self.all_player_names,
            )
            return True

        # 屠边局：杀光所有神或所有民
        if alive_gods == 0 or alive_villagers == 0:
            print("\n狼人阵营胜利! 成功屠边\n")
            self.logger.log_public_event(
                "游戏结束：狼人胜利",
                self.all_player_names,
            )
            return True

        return False

    def run(self):
        """运行游戏主循环"""

        self.setup_game()

        while True:
            if self.check_game_over():
                break
            self.night_phase()
            if self.check_game_over():
                break
            self.day_phase()

        h1("游戏结束, 最终身份公布")
        final_status_str = ""
        for name, player in self.players.items():
            status = "存活" if player.is_alive else "死亡"
            final_status_log = f"- {name}: {player.role.capitalize()} ({status}) <br>"
            final_status_str = final_status_str + final_status_log + "\n"
            self.logger.log_public_event(
                final_status_log,
                self.all_player_names,
            )
        print(final_status_str)
