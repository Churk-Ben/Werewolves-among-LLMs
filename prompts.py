# 游戏阶段提示词配置
GAME_PROMPTS = {
    # 游戏初始化阶段
    "welcome": "欢迎来到狼人杀.",
    "initializing": "游戏正在初始化...",
    # 游戏阶段提示
    "night_start": "天黑请闭眼.",
    "day_start": "天亮了.",
    "day_phase": "白天阶段, 请发言.",
    "vote_phase": "投票环节, 请投票.",
    # 游戏结束提示
    "villagers_win": "游戏结束！所有狼人都已出局，好人阵营胜利！",
    "werewolves_win": "游戏结束！狼人数量已经大于等于好人数量，狼人阵营胜利！",
    # 错误提示
    "unknown_command": "未知指令: {}",
    "init_error": "玩家初始化异常: {}",
    "game_init_error": "游戏初始化异常: {}",
    "night_phase_error": "夜晚阶段异常: {}",
    "day_phase_error": "白天阶段异常: {}",
    "vote_phase_error": "投票阶段异常: {}",
    "game_end_error": "结算阶段异常: {}",
    "main_loop_error": "主循环异常: {}",
    # 游戏信息提示
    "player_list": "本场玩家列表: {}",
    "role_list": "本场已分配身份: {}",
    "werewolf_info": "本场狼人是: {}.",
    "ai_response_error": "AI响应异常: {}",
    "parse_order_error": "指令解析异常: {}",
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
