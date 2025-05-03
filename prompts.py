# 游戏阶段提示词配置
GAME_PROMPTS = {
    # 游戏初始化阶段
    "welcome": "欢迎来到狼人杀.",
    "initializing": "游戏正在初始化...",
    # 游戏阶段提示
    "night_start": "天黑请闭眨.",
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
