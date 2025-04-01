document.addEventListener("DOMContentLoaded", () => {
    const socket = io();
    const messagesDiv = document.getElementById("messages");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const playersList = document.getElementById("players");
    const gamePhase = document.getElementById("game-phase");

    // 连接成功后启用输入
    socket.on("connect", () => {
        messageInput.disabled = false;
        sendButton.disabled = false;
    });

    // 绑定发送按钮点击事件
    sendButton.addEventListener("click", sendMessage);

    // 绑定回车键发送消息
    messageInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });


    // 处理接收到的消息
    socket.on("message", (message) => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.classList.add(message.type);

        if (message.player) {
            const playerName = document.createElement("strong");
            playerName.textContent = message.player + " : ";
            messageElement.appendChild(playerName);
        }

        const messageContent = document.createElement("span");
        messageContent.textContent = message.content;
        messageElement.appendChild(messageContent);
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });

    // 发送消息
    function sendMessage() {
        const content = messageInput.value.trim();
        if (content) {
            // 先显示用户消息
            const messageElement = document.createElement("div");
            messageElement.classList.add("message");
            messageElement.classList.add("speech");

            const playerName = document.createElement("strong");
            playerName.textContent = "法官 : ";

            const messageContent = document.createElement("span");
            messageContent.textContent = content;

            messageElement.appendChild(playerName);
            messageElement.appendChild(messageContent);
            messagesDiv.appendChild(messageElement);

            // 发送到服务器处理
            socket.emit("order", { content: content });
            messageInput.value = "";

            // 自动滚动到最新消息
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    }

    // 更新游戏状态
    socket.on("fresh_state", (state) => {
        // 更新游戏阶段
        gamePhase.textContent = `阶段: ${state.phase}`;

        // 更新玩家列表
        playersList.innerHTML = "";
        state.players.forEach((player) => {
            const li = document.createElement("li");

            // 设置基础文本内容
            let displayText = player.name;

            // 如果是投票结束阶段且玩家有投票，显示投票结果
            if (state.phase === "投票结束" && player.voted !== -1) {
                displayText += ` (被投票数: ${player.voted})`;
            }

            li.textContent = displayText;

            // 根据角色添加样式
            if (player.role === "VILLAGER") {
                li.classList.add("villager");
            }
            else if (player.role === "WEREWOLF") {
                li.classList.add("werewolf");
            }
            else if (player.role === "SEER") {
                li.classList.add("seer");
            }
            else if (player.role === "SWITCH") {
                li.classList.add("switch");
            }
            else if (player.role === "BODYGUARD") {
                li.classList.add("bodyguard");
            }

            // 根据存活状态添加样式
            if (!player.alive) {
                li.classList.add("dead");
            }

            playersList.appendChild(li);
        });
    });

});
