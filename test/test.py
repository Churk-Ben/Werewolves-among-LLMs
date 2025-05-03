from openai import OpenAI


class Test:
    def __init__(self, server):
        self.client = OpenAI(
            api_key="sk-4e5351b24ef34d75bd2e489f1ff73e4a",
            base_url="https://api.deepseek.com",
        )
        self.server = server

    def test_chat(self):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            stream=True,
        )

        self.server.send_stream("test", response, "speech")
