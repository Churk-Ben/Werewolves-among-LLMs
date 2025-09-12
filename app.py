import os
from server.Server import GameServer
from game.Game import WerewolfGame
from yaml import safe_load


def load_config(dotenv_path=".env", config_path="config.yaml"):
    # 变更kimi为中国站
    os.environ["MOONSHOT_API_BASE"] = "https://api.moonshot.cn/v1"

    if not os.path.exists(dotenv_path):
        return {}

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

    with open(config_path, "r", encoding="utf-8") as f:
        config = safe_load(f)
        return config


def main():
    web_config = load_config()["web"]
    if web_config["enable"]:
        server = GameServer()
        server.run(host=web_config["host"], port=web_config["port"])

    else:
        game = WerewolfGame()
        game.run()


if __name__ == "__main__":
    main()
