from server.Server import GameServer
from game.Game import WerewolfGame
from yaml import safe_load

with open("config.yaml", "r", encoding="utf-8") as f:
    config = safe_load(f)
    web_config = config["web"]


def main():
    if web_config["enable"]:
        server = GameServer()
        server.run(host=web_config["host"], port=web_config["port"])

    else:
        game = WerewolfGame()
        game.run()


if __name__ == "__main__":
    main()
