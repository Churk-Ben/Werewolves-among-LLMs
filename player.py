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
        # 女巫技能状态
        self.has_heal = True if role == "WITCH" else False
        self.has_poison = True if role == "WITCH" else False

    def reset_history(self):
        """
        重置玩家的历史记录，清空记忆
        """

        initial_message = PLAYER_PROMPTS["initial_message"].format(self.name, self.role)
        # 为不同角色添加特殊提示
        if self.role == "WEREWOLF":
            initial_message += "\n你是狼人，你的目标是消灭所有好人。每天晚上，你可以选择一名玩家击杀。"
        elif self.role == "SEER":
            initial_message += "\n你是预言家，你的目标是找出所有狼人。每天晚上，你可以查验一名玩家的身份。"
        elif self.role == "WITCH":
            initial_message += "\n你是女巫，你的目标是帮助好人阵营获胜。你有一瓶解药和一瓶毒药，解药可以救活一名被狼人杀死的玩家，毒药可以毒死一名玩家。每种药只能使用一次。"
        elif self.role == "VILLAGER":
            initial_message += "\n你是普通村民，你的目标是和好人阵营一起找出所有狼人。"
            
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
            # 根据角色和阶段添加特殊提示
            role_specific_prompt = prompt
            if "狼人请睁眼" in prompt and self.role == "WEREWOLF":
                role_specific_prompt += "\n请明确指出你要击杀的玩家名字，格式为：'我选择击杀 [玩家名]'"
            elif "预言家请睁眼" in prompt and self.role == "SEER":
                role_specific_prompt += "\n请明确指出你要查验的玩家名字，格式为：'我选择查验 [玩家名]'"
            elif "女巫请睁眼" in prompt and self.role == "WITCH":
                options = []
                if self.has_heal:
                    options.append("使用解药")
                if self.has_poison:
                    options.append("使用毒药")
                if options:
                    role_specific_prompt += f"\n你现在拥有的药水：{', '.join(options)}。"
                    if self.has_heal:
                        role_specific_prompt += "\n如果要使用解药，请回复：'我选择使用解药救 [玩家名]'"
                    if self.has_poison:
                        role_specific_prompt += "\n如果要使用毒药，请回复：'我选择使用毒药毒死 [玩家名]'"
                    role_specific_prompt += "\n如果不使用任何药水，请回复：'我选择不使用任何药水'"
                else:
                    role_specific_prompt += "\n你已经没有任何药水了，请回复：'我没有药水可以使用'"
            
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=self.history
                + [
                    {
                        "role": "user",
                        "name": "Judger",
                        "content": role_specific_prompt,
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
            
    def parse_action(self, response_text, action_type):
        """
        解析玩家的行动
        
        action_type: 'kill', 'check', 'heal', 'poison'
        """
        if not response_text:
            return None
            
        if action_type == 'kill' and '击杀' in response_text:
            # 解析狼人击杀目标
            import re
            match = re.search(r'击杀\s*([A-Za-z]+)', response_text)
            if match:
                return match.group(1)
        elif action_type == 'check' and '查验' in response_text:
            # 解析预言家查验目标
            import re
            match = re.search(r'查验\s*([A-Za-z]+)', response_text)
            if match:
                return match.group(1)
        elif action_type == 'heal' and '解药' in response_text and '救' in response_text:
            # 解析女巫救人目标
            import re
            match = re.search(r'救\s*([A-Za-z]+)', response_text)
            if match:
                self.has_heal = False  # 使用解药
                return match.group(1)
        elif action_type == 'poison' and '毒药' in response_text and '毒死' in response_text:
            # 解析女巫毒人目标
            import re
            match = re.search(r'毒死\s*([A-Za-z]+)', response_text)
            if match:
                self.has_poison = False  # 使用毒药
                return match.group(1)
                
        return None
