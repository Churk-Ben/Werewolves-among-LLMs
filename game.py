from manager import Manager


class Game:
    def __init__(self, server):
        self.server = server
        self.manager = Manager(self)
        self.rules = self.manager.get_game_rules()
        self.state = {
            "phase": "欢迎来到狼人杀！",
            "players": [],
        }
        self.history = [
            {"role": "system", "content": "You are a helpful assistant"},
        ]

    def parse_order(self, order):  # 之后会用ai分析指令
        match True:
            case _ if "0" in order:
                msg = self.game_start()
            case _ if "1" in order:
                msg = self.game_end()
            case _ if "2" in order:
                msg = self.change()
            case _ if "3" in order:
                msg = self.chat(order)
            case _ if "5" in order:
                msg = self.fresh_state()
            case _:
                msg = self.default()
        if msg:
            self.server.send_message("System", msg, "thought")

    def game_start(self):
        self.state["players"] = self.manager.init_players()["players"]
        self.server.send_message(
            "System",
            "下面宣读本场游戏规则...<br><br>" + self.rules,
            "speech",
        )

    def game_end(self):
        return "Game ended"

    def change(self):
        import random

        self.state["players"][0]["alive"] = random.choice([True, False])
        self.state["players"][1]["alive"] = random.choice([True, False])
        self.state["players"][2]["alive"] = random.choice([True, False])
        self.state["players"][3]["alive"] = random.choice([True, False])
        return "Change randomly"

    def chat(self, order):
        from openai import OpenAI

        client = OpenAI(
            api_key="sk-4e5351b24ef34d75bd2e489f1ff73e4a",
            base_url="https://api.deepseek.com",
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=self.history
            + [
                {"role": "user", "content": order},
            ],
            stream=True,
        )
        self.history.append({"role": "user", "content": order})
        temp = self.server.send_stream("助手", response, "speech")
        self.history.append({"role": "assistant", "content": temp["content"]})

    def fresh_state(self):
        self.server.fresh_state()

    def default(self):
        return "Invalid order"
