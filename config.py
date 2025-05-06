import os
from dotenv import load_dotenv

load_dotenv()

# 大模型配置
API_URL = "https://api.deepseek.com"
API_KEY = os.getenv("API_KEY")  # 在.env文件中设置API_KEY或直接在此处设置API_KEY
DEFAULT_MODEL = "deepseek-chat"

# 角色配置
CHARACTERS = ["WEREWOLF", "WEREWOLF", "VILLAGER", "VILLAGER", "SEER", "WITCH"]
playerList = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
