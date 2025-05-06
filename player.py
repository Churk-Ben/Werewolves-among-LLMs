from openai import OpenAI
from config import API_KEY, API_URL, DEFAULT_MODEL
from prompts import PLAYER_PROMPTS, GAME_PROMPTS


class Player:
    def __init__(self, manager, name, role, p):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.manager = manager
        self.name = name
        self.role = role
        self.top_p = p
        self.reset_history()

    def reset_history(self):
        """
        重置玩家的历史记录，清空记忆
        """

        initial_message = PLAYER_PROMPTS["initial_message"].format(self.name, self.role)
        self.history = [
            {
                "role": "system",
                "content": initial_message,
            },
        ]

    def listen(self, message):
        """
        存储同房间他人和自己的消息
        """

        if not message or "player" not in message or "content" not in message:
            return
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
        """
        执行行动(发言或投票)(speech)
        """

        try:
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
            message = self.manager.game.server.send_stream(
                self.name, response, "speech"
            )
            return message
        except Exception as e:
            self.manager.game.server.send_message(
                self.name, GAME_PROMPTS["ai_response_error"].format(str(e)), "error"
            )
