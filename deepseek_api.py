import requests
import json
from config import API_KEY, API_BASE_URL, MODEL_NAME, MAX_TOKENS, TEMPERATURE

def call_deepseek_api(prompt, role_info=None):
    """调用Deepseek API获取AI的回应
    
    Args:
        prompt (str): 主要提示词
        role_info (dict, optional): 角色相关信息，包含角色类型、游戏状态等
    
    Returns:
        str: AI的回应
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 构建系统提示词
    system_prompt = "你正在参与一场狼人杀游戏。"
    if role_info:
        system_prompt += f"你的角色是{role_info['role']}，"
        system_prompt += f"现在是游戏的第{role_info['day_count']}天，{role_info['phase']}阶段。"
        system_prompt += "请根据角色特点和游戏阶段做出合适的反应。"
    
    data = {
        'model': MODEL_NAME,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': MAX_TOKENS,
        'temperature': TEMPERATURE
    }
    
    try:
        response = requests.post(f'{API_BASE_URL}/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API调用错误: {str(e)}")
        return None

def generate_werewolf_prompt(game_state):
    """生成狼人角色的提示词"""
    return f"""
作为狼人，你的目标是消灭好人阵营。每天晚上你可以选择一名玩家进行袭击。
目前存活的玩家有：{game_state['alive_players']}。

请注意以下几点：
1. 优先考虑对方的身份和威胁程度（如预言家可能会查验你的身份）
2. 分析玩家的行为和发言，找出可能的特殊身份
3. 避免过于明显的选择，以免暴露自己
4. 与其他狼人配合（如果有的话）

根据当前游戏状态，你会选择袭击谁？请给出详细的思考过程。
"""

def generate_seer_prompt(game_state):
    """生成预言家角色的提示词"""
    return f"""
作为预言家，你是好人阵营的重要角色。每晚你可以查看一名玩家的真实身份（是否为狼人）。
目前存活的玩家有：{game_state['alive_players']}。

请注意以下几点：
1. 分析玩家的行为和发言，找出可疑的对象
2. 考虑查验结果对局势的影响
3. 在白天时要谨慎透露自己的身份和查验结果
4. 优先查验最可疑或最有影响力的玩家

根据当前游戏状态，你会查验谁？请给出详细的思考过程。
"""

def generate_witch_prompt(game_state):
    """生成女巫角色的提示词"""
    return f"""
作为女巫，你拥有一瓶解药和一瓶毒药，每种药水只能使用一次。今晚狼人袭击了{game_state['wolf_target']}。

请注意以下几点：
1. 解药：可以救活被狼人袭击的玩家，但要考虑该玩家的价值
2. 毒药：可以毒死一名玩家，但要谨慎使用，避免误杀好人
3. 不要轻易暴露自己的身份
4. 药水使用的时机很重要，不要过早用掉

根据当前游戏局势，你要使用药水吗？请给出详细的思考过程。
"""

def generate_day_discussion_prompt(game_state):
    """生成白天讨论阶段的提示词"""
    return f"""
现在是白天讨论阶段。昨晚发生了以下事件：{game_state['night_events']}。

请注意以下几点：
1. 根据你的角色身份（好人/狼人）选择合适的发言策略
2. 分析昨晚的事件，找出可疑之处
3. 注意其他玩家的反应和发言
4. 适当为自己辩护，但不要过于刻意
5. 如果你有特殊身份，要谨慎透露信息

请根据当前局势，给出你的发言和思考过程。
"""

def generate_voting_prompt(game_state):
    """生成投票阶段的提示词"""
    return f"""
投票阶段开始了。
目前存活的玩家有：{game_state['alive_players']}。
在讨论中发现的可疑点：{game_state['suspicious_points']}。

请注意以下几点：
1. 分析每个玩家在讨论阶段的表现
2. 结合之前的游戏信息（如预言家的验人结果）
3. 考虑投票的影响（是否会帮助自己的阵营）
4. 注意其他玩家的投票倾向

你会投票给谁？请给出详细的思考过程。
"""