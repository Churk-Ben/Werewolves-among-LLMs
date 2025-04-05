from config import API_KEY, API_URL, DEFAULT_MODEL
from openai import OpenAI

# 优化提示词，使AI更好地理解游戏规则和当前状态
prompt_think = """现在轮到你了。请结合场上形势、历史对话和你的角色身份，仔细思考当前局势。
请分析其他玩家的发言，判断谁可能是狼人，谁可能是好人。
如果你是狼人，请考虑如何隐藏身份；如果你是好人，请思考如何找出狼人。
请仅阐述你的思考过程，先不要做出任何行动决策。"""

prompt_act = """根据你之前的思考，现在请做出你的行动决策。
如果是白天阶段，请发表你的言论，可以质疑、辩解或提供信息。
如果是投票阶段，请明确表示你要投票给谁。
如果是夜晚阶段且你有特殊技能（如狼人杀人、预言家查验、女巫救人/毒人），请明确表示你要对谁使用技能。
你可以用括号展示出你的小动作，例如：(思考中...)、(犹豫不决)等。"""

# 针对不同角色的特殊提示词
prompt_werewolf = """你是狼人，你的目标是消灭所有好人。夜晚你可以与其他狼人一起选择一名玩家击杀。
白天你需要隐藏自己的身份，误导其他玩家，避免被投票出局。
请记住，你知道谁是你的同伴狼人，但好人不知道彼此的身份。"""

prompt_villager = """你是普通村民，没有特殊技能，但你的目标是找出并消灭所有狼人。
你需要通过仔细观察和分析其他玩家的言行来判断谁可能是狼人。
请记住，狼人知道彼此的身份，而你不知道其他好人是谁。"""

prompt_seer = """你是预言家，每晚可以查验一名玩家的真实身份（是否为狼人）。
你的目标是帮助好人找出并消灭所有狼人。
你需要决定是否公开自己的身份和查验结果，这可能会帮助好人，但也会使你成为狼人的目标。"""

prompt_witch = """你是女巫，拥有一瓶解药和一瓶毒药，每种药只能使用一次。
解药可以救活当晚被狼人杀害的玩家，毒药可以杀死一名玩家。
你的目标是帮助好人找出并消灭所有狼人。
请谨慎使用你的药，它们可能在关键时刻决定游戏的胜负。"""


class Player:
    def __init__(self, manager, name, role, p):
        self.client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.manager = manager
        self.name = name
        self.role = role
        self.top_p = p
        
        # 根据角色设置不同的系统提示
        role_prompt = ""
        if role == "WEREWOLF":
            role_prompt = prompt_werewolf
        elif role == "VILLAGER":
            role_prompt = prompt_villager
        elif role == "SEER":
            role_prompt = prompt_seer
        elif role == "WITCH":
            role_prompt = prompt_witch
            
        self.history = [
            {
                "role": "system",
                "content": f"你是一个狼人杀玩家，你叫{self.name}，身份是{self.role}。\n{role_prompt}",
            },
        ]

    def listen(self, message):
        """存储同房间他人和自己的消息，区分不同类型的消息"""
        # 根据消息类型处理不同的消息格式
        if message["type"] == "thought":
            # 思考类消息，标记为系统消息以区分
            self.history.append(
                {
                    "role": "system",
                    "name": message["player"],
                    "content": f"【思考】{message['content']}",
                }
            )
        elif message["type"] == "speech":
            # 发言类消息，标记为用户消息
            self.history.append(
                {
                    "role": "user",
                    "name": message["player"],
                    "content": message["content"],
                }
            )
        else:
            # 其他类型消息，默认处理
            self.history.append(
                {
                    "role": "user",
                    "name": message["player"],
                    "content": message["content"],
                }
            )

    def think(self, prompt):
        """分析场上所有消息并生成思考 ( thought )"""
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
        return response

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
        self.manager.game.server.send_stream(
            self.name, response, "speech"
        )
