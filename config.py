# 大模型配置
try:
    import os
    from dotenv import load_dotenv

    load_dotenv()
    API_KEY = os.getenv("API_KEY")
except:
    API_KEY = "YOUR_API_KEY"  # 先前版本的api_key截至pre release前已失效, 请在此处填写您申请的API_KEY

API_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

# 角色配置
CHARACTERS = ["WEREWOLF", "WEREWOLF", "VILLAGER", "VILLAGER", "SEER", "WITCH"]
playerList = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
