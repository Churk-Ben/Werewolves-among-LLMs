from openai import OpenAI

client = OpenAI(
    api_key="sk-4e5351b24ef34d75bd2e489f1ff73e4a", base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=True,
)

# 流式输出处理
full_content = ""
for chunk in response:
    if chunk.choices[0].delta.content:
        chunk_content = chunk.choices[0].delta.content
        full_content += chunk_content
        # 实时打印输出
        print(chunk_content, end="", flush=True)
