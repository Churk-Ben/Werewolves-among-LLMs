from config import playerList, CHARACTERS
from player import Player
import random


class Manager:
    def __init__(self, game):
        self.game = game
        self.players_state = []
        self.players_object = []

    def init_players(self):
        random.shuffle(CHARACTERS)
        self.players_state = []
        self.players_object = []
        roles = random.sample(CHARACTERS, len(CHARACTERS))
        for i, name in enumerate(playerList):
            p = round(random.random(), 2)
            player = Player(self, name, roles[i], p)

            self.players_object.append(player)
            self.players_state.append(
                {
                    "name": name,
                    "role": roles[i],
                    "alive": True,
                    "voted": -1,
                    "p": p,
                }
            )
        return {"players": self.players_state}

    def get_players_state(self):
        return {"players": self.players_state}

    def _execute_player_action(self, room, action_type, data):
        """通用的玩家行动执行方法
        Args:
            room: 目标房间("ALL"或特定角色)
            action_type: 行动类型("listen"或"act")
            data: 传递给行动方法的数据(message或prompt)
        """
        target_players = [p for p in self.players_object if room == "ALL" or p.role == room]
        for player in target_players:
            if action_type == "listen":
                player.listen(data)
            elif action_type == "act":
                player.act(data)

    def broadcast_to_player(self, room, message):
        self._execute_player_action(room, "listen", message)

    def let_player_act(self, room, prompt):
        self._execute_player_action(room, "act", prompt)


if __name__ == "__main__":
    manager = Manager(None)
    manager.init_players()
    print(manager.players_state)
    print(manager.players_object)
