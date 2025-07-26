# 游戏阶段提示词配置
GAME_PROMPTS = {
    # 游戏初始化阶段
    "welcome": "欢迎来到狼人杀.",
    "initializing": "游戏正在初始化...",
    # 游戏阶段提示
    "night_start": "天黑请闭眼.",
    "day_start": "天亮了.",
    "day_phase": "白天阶段, 请发言.",
    "vote_phase": "第{}天投票环节, 存活玩家: {}. 请投票选择你认为是狼人的玩家.",
    # 夜晚角色行动提示
    "werewolf_action": "狼人请睁眼，请选择你要击杀的对象: {}",
    "seer_action": "预言家请睁眼，请选择你要查验的对象: {}",
    "seer_result": "你查验的玩家 {} {}狼人",
    "witch_action": "女巫请睁眼，今晚 {} 玩家被杀，你要使用解药救他吗？或者使用毒药杀死其他人？",
    "night_result": "天亮了，昨晚 {} 玩家被杀",
    "no_death": "天亮了，昨晚是平安夜，没有人被杀",
    # 投票相关提示
    "vote_start": "投票开始，请各位玩家依次发表投票.",
    "vote_result": "投票结果：{} 被投出局.",
    "vote_tie": "投票结果出现平局，没有人被投出局.",
    "vote_summary": "投票统计：{}",
    # 游戏结束提示
    "villagers_win": "游戏结束！所有狼人都已出局，好人阵营胜利！",
    "werewolves_win": "游戏结束！狼人数量已经大于等于好人数量，狼人阵营胜利！",
    # 错误提示
    "unknown_command": "未知指令: {}",
    "init_error": "玩家初始化异常: {}",
    "ai_response_error": "AI响应异常: {}",
    "parse_order_error": "指令解析异常: {}",
    "game_init_error": "游戏初始化异常: {}",
    "night_phase_error": "夜晚阶段异常: {}",
    "day_phase_error": "白天阶段异常: {}",
    "vote_phase_error": "投票阶段异常: {}",
    "game_end_error": "结算阶段异常: {}",
    "main_loop_error": "主循环异常: {}",
    # 游戏信息提示
    "player_list": "本场玩家列表: {}",
    "role_list": "本场已分配身份: {}",
    "werewolf_list": "本场狼人是: {}.",
}

# 游戏状态提示词配置
GAME_PHASES = {
    "welcome": "欢迎来到狼人杀.",
    "initializing": "游戏正在初始化...",
    "night": "第{}夜",
    "day": "天亮了",
    "vote": "投票阶段",
    "villagers_win": "游戏结束 - 好人胜利",
    "werewolves_win": "游戏结束 - 狼人胜利",
}

# 角色提示词配置
PLAYER_PROMPTS = {
    # 玩家初始化提示
    "initial_message": "你是一个狼人杀玩家，你叫{}，身份是{}."
    "在白天来临前,你没见过任何其他玩家.在接下来的游戏中,请不要在计划外暴露自己的身份."
    "你的输出只包含对话和**你想要展示给所有人**的动作.注意伪装.",
    "death_message": "@death_message",
}
