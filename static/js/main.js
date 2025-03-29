document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const messagesDiv = document.getElementById('messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const playersList = document.getElementById('players');
    const gamePhase = document.getElementById('game-phase');

    // 连接成功后启用输入
    socket.on('connect', () => {
        messageInput.disabled = false;
        sendButton.disabled = false;
    });

    // 处理接收到的消息
    socket.on('message', (message) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(message.type);

        const playerName = document.createElement('strong');
        playerName.textContent = message.player + ': ';

        const messageContent = document.createElement('span');
        messageContent.textContent = message.content;

        messageElement.appendChild(playerName);
        messageElement.appendChild(messageContent);
        messagesDiv.appendChild(messageElement);

        // 自动滚动到最新消息
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });

    // 发送消息
    function sendMessage() {
        const content = messageInput.value.trim();
        if (content) {
            const message = {
                player: 'Player',  // 这里后续需要改为实际的玩家名称
                content: content,
                type: 'speech'  // 玩家发送的消息默认为speech类型
            };
            socket.emit('message', message);
            messageInput.value = '';
        }
    }

    // 绑定发送按钮点击事件
    sendButton.addEventListener('click', sendMessage);

    // 绑定回车键发送消息
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // 更新游戏状态
    socket.on('game_state', (state) => {
        gamePhase.textContent = state.phase;
        // 更新玩家列表
        playersList.innerHTML = '';
        state.players.forEach(player => {
            const li = document.createElement('li');
            li.textContent = player.name;
            playersList.appendChild(li);
        });
    });
});