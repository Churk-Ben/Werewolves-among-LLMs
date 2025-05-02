from config import playerList, CHARACTERS
from player import Player
import random


class Manager:
    def __init__(self, game):
        self.game = game
        self.players_state = []
        self.players_object = []

    def init_players(self):
        try:
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
        except Exception as e:
            return {"players": [], "error": str(e)}

    def get_players_state(self):
        return {"players": self.players_state}

    def broadcast_to_player(self, room, message):
        if not message:
            return
        if room == "ALL":
            for player in self.players_object:
                player.listen(message)
        else:
            for player in self.players_object:
                if player.role == room:
                    player.listen(message)

    def let_player_act(self, name, prompt):
        if not prompt:
            return
        if name == "ALL":
            for player in self.players_object:
                player.act(prompt)
        else:
            for player in self.players_object:
                if player.name == name:
                    player.act(prompt)


if __name__ == "__main__":
    manager = Manager(None)
    manager.init_players()
    print(manager.players_state)
    print(manager.players_object)
