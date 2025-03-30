from config import API_KEY, API_URL, DEFAULT_MODEL
from openai import OpenAI


class Player:
    shared_messages = []

    def __init__(self, name, role, p):
        self.name = name
        self.role = role
        self.top_p = p
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.messages = []

    def think(self, messages):
        pass

    def act(self, messages):
        pass
