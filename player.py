from config import API_KEY, API_URL, DEFAULT_MODEL
from openai import OpenAI


class Player:
    def __init__(self, manager, name, role, p):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.manager = manager
        self.name = name
        self.role = role
        self.top_p = p
        self.reset_history()

    def reset_history(self):
        """重置玩家的历史记录，清空记忆"""
        self.history = [
            {
                "role": "system",
                "content": f"你是一个狼人杀玩家，你叫{self.name}，身份是{self.role}。",
            },
        ]

    def listen(self, message):
        """存储同房间他人和自己的消息"""
        if message["player"] == self.name:
            self.history.append(
                {
                    "role": "assistant",
                    "name": message["player"],
                    "content": message["content"],
                }
            )
        else:
            self.history.append(
                {
                    "role": "user",
                    "name": message["player"],
                    "content": message["content"],
                }
            )

    def act(self, prompt):
        """根据思考结果执行行动(发言或投票)(speech)"""
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.history
            + [
                {
                    "role": "user",
                    "name": "Judger",
                    "content": prompt,
                },
            ],
            stream=True,
            top_p=self.top_p,
        )
        self.manager.game.server.send_stream(self.name, response, "speech")
