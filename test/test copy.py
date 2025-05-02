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
