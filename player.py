from config import API_KEY, API_URL, DEFAULT_MODEL
from openai import OpenAI
from model import Message


class Player:
    def __init__(self, manager, name, role, p, client: OpenAI, model=DEFAULT_MODEL):
        self.manager = manager
        self.name = name
        self.role = role
        self.client = client
        self.model = model
        self.top_p = p
        self.history = [
            {
                "role": "system",
                "content": f"现在，你身处一场狼人杀游戏，你叫{self.name}，身份是{self.role}。",
            },
        ]

    def listen(self, message: Message):
        """存储其他玩家消息"""
        self.history.append(
            {
                "role": "user",
                "name": message["player"],
                "content": message["content"],
            },
        )

    def act(self, prompt):
        """执行行动(发言或投票)"""
        # 添加用户提示到历史记录
        user_message = {
            "role": "user",
            "name": "Judger",
            "content": prompt,
        }
        self.history.append(user_message)

        # 创建流式响应
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            stream=True,
            top_p=self.top_p,
        )

        # 处理流式响应
        full_response = ""
        if self.manager:
            # 发送流式响应到服务器
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    self.manager.game.server.send_stream(self.name, chunk.choices[0].delta.content, "speech")
        else:
            # 本地测试模式
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content

        # 添加AI响应到历史记录
        self.history.append({
            "role": "assistant",
            "content": full_response,
        })


if __name__ == "__main__":
    client = OpenAI(api_key=API_KEY, base_url=API_URL)
    player = Player(None, "Alice", "WEREWOLF", 0.9, client)
    prompt = "你是狼人还是普通人？"
    player.act(prompt)
    print(player.history)
