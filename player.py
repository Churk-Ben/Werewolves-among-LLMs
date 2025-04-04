from config import API_KEY, API_URL, DEFAULT_MODEL
from openai import OpenAI

prompt_think = "现在轮到你了。结合场上形势和历史对话，仅阐述你的思考，先不要做出行动。"
prompt_act = "根据你之前的思考，你现在可以行动，可以用括号展示出你的小动作。"


class Player:
    def __init__(self, manager, name, role, p):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.manager = manager
        self.name = name
        self.role = role
        self.top_p = p
        self.history = [
            {
                "role": "system",
                "content": f"你是一个狼人杀玩家，你叫{self.name}，身份是{self.role}",
            },
        ]

    def listen(self, message):
        """存储同房间他人的 speech 消息和自己的所有 ( speech & thought ) 消息"""
        if message["room"] == self.role or message["room"] == "ALL":
            if message["type"] == "speech" or message["player"] == self.name:
                self.history.append(message)

    def think(self):
        """分析场上所有消息并生成思考 ( thought )"""
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.history
            + [
                {"role": "user", "content": prompt_think},
            ],
            stream=True,
            top_p=self.top_p,
        )
        return response

    def act(self):
        """根据思考结果执行行动(发言或投票)(speech)"""
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.history
            + [
                {"role": "user", "content": prompt_act},
            ],
            stream=True,
            top_p=self.top_p,
        )
        return response
