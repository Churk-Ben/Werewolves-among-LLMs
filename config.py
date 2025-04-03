# API配置
API_URL = "https://api.deepseek.com"
API_KEY = "sk-4e5351b24ef34d75bd2e489f1ff73e4a"  # 替换为你的实际API密钥

# API请求配置
DEFAULT_MODEL = "deepseek-chat"

# 角色配置
CHARACTERS = ["WEREWOLF", "WEREWOLF", "VILLAGER", "VILLAGER", "SEER", "WITCH"]
playerList = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]

# 本地游戏规则
LOCAL_RULES = """
<head>
    <style>
        .section {
            margin-bottom: 30px;
            line-height: 2em;
        }
        .section:last-child {
            margin-bottom: 0;
        }
        .section h1 {
            text-align: center;
        }
        .section h2 {
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
        .section ul,
        .section ol {
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="section">
        <h2>一、角色及技能</h2>
        <p><strong>1. 狼人（2人）</strong></p>
        <ul>
            <li>每晚共同选择击杀一名玩家。</li>
            <li>白天伪装成好人，通过发言误导投票。</li>
        </ul>

        <p><strong>2. 村民（2人）</strong></p>
        <ul>
            <li>无特殊技能，白天通过发言和分析找出狼人。</li>
            <li>需避免被狼人杀害或好人误投。</li>
        </ul>

        <p><strong>3. 预言家（1人）</strong></p>
        <ul>
            <li>每晚可查验一名玩家的身份（狼人或好人）。</li>
            <li>需谨慎暴露身份，避免被狼人针对。</li>
        </ul>

        <p><strong>4. 女巫（1人）</strong></p>
        <ul>
            <li>拥有一瓶<strong>解药</strong>（可救活当晚被狼杀的玩家）和一瓶<strong>毒药</strong>（可毒杀一名玩家）。</li>
            <li>解药和毒药<strong>不可同一夜使用</strong>，且全程只能各用一次。</li>
            <li>女巫<strong>不可自救</strong>（若首夜被狼杀，只能用解药救自己）。</li>
        </ul>
    </div>

    <div class="section">
        <h2>二、游戏流程（昼夜交替）</h2>
        <p><strong>首夜行动顺序</strong></p>
        <ol>
            <li><strong>狼人睁眼</strong> → 选择击杀目标（可自刀或空刀，但需统一意见）。</li>
            <li><strong>预言家睁眼</strong> → 指向一名玩家，法官告知其身份（狼/好人）。</li>
            <li><strong>女巫睁眼</strong> → 法官告知当晚死亡情况，女巫选择是否使用解药/毒药（首夜可自救）。</li>
        </ol>

        <p><strong>白天流程</strong></p>
        <ol>
            <li><strong>公布死亡</strong>：法官宣布昨夜死亡玩家（可能无死亡或多人死亡）。</li>
            <li><strong>发言环节</strong>：从死亡玩家左侧开始顺时针发言，或随机顺序。</li>
            <li><strong>投票放逐</strong>：所有存活玩家投票，得票最高者出局（平票则无人出局）。</li>
        </ol>

        <p><strong>后续夜晚</strong></p>
        <ul>
            <li>女巫用完解药后，不再得知狼人击杀目标。</li>
        </ul>
    </div>

    <div class="section">
        <h2>三、胜负条件</h2>
        <ul>
            <li><strong>狼人胜利</strong>：狼人存活数 ≥ 好人存活数（如2狼 vs 2好人）。</li>
            <li><strong>好人胜利</strong>：所有狼人被放逐或毒杀。</li>
        </ul>
    </div>

    <div class="section">
        <h2>四、特殊规则（平衡性调整）</h2>
        <p><strong>1. 女巫限制</strong></p>
        <ul>
            <li>若首夜狼人空刀，女巫不可使用解药（避免无意义救人）。</li>
            <li>解药必须在得知死亡后立即使用，不可留存。</li>
        </ul>

        <p><strong>2. 预言家保护</strong></p>
        <ul>
            <li>首夜预言家验人结果若为狼人，法官可允许其第二天白天额外发言10秒（可选规则）。</li>
        </ul>

        <p><strong>3. 狼人策略</strong></p>
        <ul>
            <li>允许狼人白天自爆（立即进入黑夜，跳过投票）。</li>
        </ul>
    </div>

    <div class="section">
        <h2>五、可选变体规则</h2>
        <ul>
            <li><strong>屠边模式</strong>：狼人需击杀所有神职（预言家+女巫）或所有村民。</li>
            <li><strong>警长模式</strong>：第一天白天竞选警长，警长拥有1.5票归票权。</li>
        </ul>
    </div>

    <div class="section">
        <h2>六、游戏示例</h2>
        <ul>
            <li><strong>首夜</strong>：狼杀1号（民），女巫用解药救活，无人死亡。白天投票出局3号（狼）。</li>
            <li><strong>第二夜</strong>：狼杀预言家，女巫毒杀另一狼，好人胜利。</li>
        </ul>
    </div>
</body>
"""
