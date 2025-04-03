from config import playerList, CHARACTERS, API_KEY, API_URL, LOCAL_RULES
from openai import OpenAI
import json
import random


client = OpenAI(api_key=API_KEY, base_url=API_URL)
prompt_start = (
    f"你有六个玩家：{playerList}，他们的角色分别是：{CHARACTERS}。"
    + """
    你要：
    - 将角色随机分配给每个玩家。
    - 给每个玩家随机设定一个初始指数p (p的范围在0.0到1.0之间)
    EXAMPLE JSON OUTPUT:
    [
        { "name": 玩家名1, "role": 角色, "p": 指数 },
        ...
    ]
    """
)
prompt_rules = (
    f"你在一场狼人杀游戏中。本场游戏的角色配置为：{CHARACTERS}"
    + """
    你要：
    - 整理狼人杀游戏的规则。
    - 将规则转化为纯文本格式。
    - 将"\n"换成"<br>"。
    EXAMPLE JSON OUTPUT:
    { "role": "assistant", "content": 游戏规则 }
    """
)


def get_ai_response(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=False,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


class Manager:
    def __init__(self, game):
        self.game = game

    def init_players(self):
        players_info = get_ai_response(prompt_start)
        return json.loads(players_info)

    def local_init_players(self):
        roles = random.sample(CHARACTERS, len(CHARACTERS))
        players = []
        for i, name in enumerate(playerList):
            players.append(
                {"name": name, "role": roles[i], "p": round(random.random(), 2)}
            )
        return {"players": players}

    def aware_game_rules(self):
        game_rules = get_ai_response(prompt_rules)
        return json.loads(game_rules)

    def local_aware_game_rules(self):
        return {"role": "assistant", "content": LOCAL_RULES}


if __name__ == "__main__":
    print(Manager.local_init_players())
    print(Manager.local_aware_game_rules())
