from config import API_KEY, API_URL, DEFAULT_MODEL
from openai import OpenAI

client = OpenAI(api_key=API_KEY, base_url=API_URL)
prompt_start = (
    f"你有六个玩家：，他们的角色分别是：。"
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
    f"你在一场狼人杀游戏中。本场游戏的角色配置为："
    + """
    你要：
    - 整理狼人杀游戏的规则。
    - 将规则转化为纯文本格式。
    - 将"\n"换成"<br>"。
    EXAMPLE JSON OUTPUT:
    { "role": "assistant", "content": 游戏规则 }
    """
)
prompt_think = "I am thinking..."


# def get_ai_response(prompt, history, model=DEFAULT_MODEL):
#     response = client.chat.completions.create(
#         model=model,
#         messages=history
#         + [
#             {"role": "user", "content": prompt},
#         ],
#         stream=True,
#         response_format={"type": "json_object"},
#     )
#     return response.choices[0].message.content


class Player:
    def __init__(self, manager, name, role, p):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.manager = manager
        self.name = name
        self.role = role
        self.top_p = p
        self.history = []

    def listen(self, message):
        """存储他人的public消息和自己的所有(public&private)消息"""
        if message["type"] == "public" or message["player"] == self.name:
            self.history.append(message)

    def think(self, message):
        """分析场上所有消息并生成思考(private)"""
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.history
            + [
                {"role": "system", "content": f"你是一个狼人杀玩家，角色是{self.role}"},
                {"role": "user", "content": message},
            ],
            stream=True,
            top_p=self.top_p,
        )

        # 流式处理思考过程
        thought = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                thought += delta.content
                # 流式传输思考过程
                self.manager.game.server.send_message(
                    self.name,
                    {"type": "thought", "content": delta.content},
                    "player_thought",
                )

        return thought

    def act(self, thought):
        """根据思考结果执行行动(发言或投票)"""
        # 发言行动
        self.manager.game.server.send_message(
            self.name, {"type": "speak", "content": thought}, "player_action"
        )

        # 简单投票逻辑(示例)
        if "投票" in thought:
            vote_target = thought.split("投票给")[1].strip()
            self.manager.game.state["players"][vote_target]["voted"] = self.name
