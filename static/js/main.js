// WebSocket连接
const socket = io();

// DOM元素
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const gamePhaseElement = document.getElementById('game-phase');
const playersContainer = document.getElementById('players');

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    // 启用输入框和发送按钮
    messageInput.disabled = false;
    sendButton.disabled = false;

    // 清除默认消息
    messagesContainer.innerHTML = '';

    // 添加欢迎消息
    addMessage('system', '欢迎来到狼人杀游戏！输入 "/start" 开始游戏。');
});

// WebSocket事件处理
socket.on('connect', function () {
    console.log('已连接到服务器');
    addMessage('system', '已连接到服务器');
});

socket.on('disconnect', function () {
    console.log('与服务器断开连接');
    addMessage('error', '与服务器断开连接');
});

socket.on('message', function (data) {
    addMessage(data.type, data.content, data.timestamp);
});

socket.on('game_state', function (data) {
    updateGameState(data.phase, data.players);
});

// 发送消息
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        if (message.startsWith('/')) {
            // 发送命令
            socket.emit('command', { command: message });
            addMessage('system', `执行命令: ${message}`);
        } else {
            // 普通消息（暂时不处理）
            addMessage('speech', `你: ${message}`);
        }
        messageInput.value = '';
    }
}

// 添加消息到聊天区域
function addMessage(type, content, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const timeStr = timestamp || new Date().toLocaleTimeString();
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        <div class="message-time">${timeStr}</div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 更新游戏状态
function updateGameState(phase, players) {
    // 更新游戏阶段
    if (gamePhaseElement) {
        gamePhaseElement.textContent = phase;
    }

    // 更新玩家列表
    if (players && players.length > 0) {
        updatePlayerList(players);
    }
}

// 更新玩家列表
function updatePlayerList(players) {
    playersContainer.innerHTML = '';

    players.forEach(player => {
        const playerCard = document.createElement('li');
        playerCard.className = `player-card ${getRoleClass(player.role)} ${player.status === '死亡' ? 'dead' : ''}`;

        playerCard.innerHTML = `
            <div class="player-basic-info">
                <span>${player.name}</span>
                <span class="expand-button">=</span>
            </div>
            <div class="player-details">
                <div>身份: ${player.role}</div>
                <div>状态: ${player.status}</div>
                <div>温度: ${player.temperature}</div>
            </div>
        `;

        playersContainer.appendChild(playerCard);
    });

    // 重新绑定展开按钮事件
    initializeExpandButtons();
}

// 获取角色对应的CSS类
function getRoleClass(role) {
    const roleMap = {
        '村民': 'villager',
        '狼人': 'werewolf',
        '预言家': 'seer',
        '女巫': 'witch',
        '猎人': 'hunter',
        '守卫': 'guard',
        'Villager': 'villager',
        'Werewolf': 'werewolf',
        'Seer': 'seer',
        'Witch': 'witch',
        'Hunter': 'hunter',
        'Guard': 'guard'
    };
    return roleMap[role] || 'villager';
}

// 初始化展开按钮
function initializeExpandButtons() {
    const expandButtons = document.querySelectorAll('.expand-button');
    expandButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const playerCard = e.target.closest('.player-card');
            const details = playerCard.querySelector('.player-details');

            // 切换展开状态
            if (!details.classList.contains('expanded')) {
                details.style.display = 'block';
                setTimeout(() => {
                    details.classList.add('expanded');
                }, 10);
                e.target.textContent = '-';
            } else {
                details.classList.remove('expanded');
                // 等待动画完成后再隐藏元素
                setTimeout(() => {
                    if (!details.classList.contains('expanded')) {
                        details.style.display = 'none';
                    }
                }, 300);
                e.target.textContent = '=';
            }

            e.stopPropagation();
        });
    });
}

// 事件监听器
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});