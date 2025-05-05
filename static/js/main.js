document.addEventListener("DOMContentLoaded", () => {
    const socket = io();
    const messagesDiv = document.getElementById("messages");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const playersList = document.getElementById("players");
    const gamePhase = document.getElementById("game-phase");
    
    // 添加查看玩家历史记忆的按钮
    const historyButton = document.createElement("button");
    historyButton.id = "history-button";
    historyButton.textContent = "查看玩家记忆";
    historyButton.style.marginLeft = "10px";
    historyButton.style.backgroundColor = "#1976d2";
    historyButton.style.color = "white";
    historyButton.style.border = "none";
    historyButton.style.padding = "8px 16px";
    historyButton.style.borderRadius = "8px";
    historyButton.style.cursor = "pointer";
    document.querySelector(".chat-input").appendChild(historyButton);

    // 连接成功后启用输入
    socket.on("connect", () => {
        messageInput.disabled = false;
        sendButton.disabled = false;
        historyButton.disabled = false;
    });
    
    // 绑定查看历史记忆按钮点击事件
    historyButton.addEventListener("click", () => {
        socket.emit("get_player_history");
    });
    
    // 处理接收到的玩家历史记忆
    socket.on("player_history", (playersHistory) => {
        console.log("玩家历史记忆:", playersHistory);
        
        // 遍历每个玩家的历史记忆并输出到控制台
        for (const playerName in playersHistory) {
            console.group(`玩家 ${playerName} 的历史记忆:`);
            playersHistory[playerName].forEach((message, index) => {
                console.log(`消息 ${index + 1}:`, message);
            });
            console.groupEnd();
        }
        
        // 在界面上显示提示信息
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.classList.add("system");
        
        const messageContent = document.createElement("span");
        messageContent.textContent = "已将所有玩家的历史记忆输出到控制台，请按F12打开开发者工具查看";
        messageElement.appendChild(messageContent);
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
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
    let currentStreamingMessage = null;

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
        messageContent.innerHTML = message.content;
        messageElement.appendChild(messageContent);
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });

    // 处理流式消息开始
    socket.on("message_start", (message) => {
        if (!message?.type) return;  // 添加必要字段检查
        
        currentStreamingMessage = document.createElement("div");
        currentStreamingMessage.classList.add("message");
        currentStreamingMessage.classList.add(message.type);

        if (message.player) {
            const playerName = document.createElement("strong");
            playerName.textContent = message.player + " : ";
            currentStreamingMessage.appendChild(playerName);
        }

        const messageContent = document.createElement("span");
        currentStreamingMessage.appendChild(messageContent);
        messagesDiv.appendChild(currentStreamingMessage);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });

    // 处理流式消息块
    socket.on("message_chunk", (message) => {
        if (!currentStreamingMessage || !message?.chunk) return;  // 添加检查
        
        const contentSpan = currentStreamingMessage.querySelector("span");
        if (contentSpan) {
            contentSpan.textContent += message.chunk;  // 使用textContent替代innerHTML
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    });

    // 处理流式消息结束
    socket.on("message_end", () => {
        currentStreamingMessage = null;
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
        

        
        // 显示当前天数
        if (state.current_night > 0) {
            gamePhase.textContent += ` | 第${state.current_night}天`;
        }

        // 更新玩家列表
        playersList.innerHTML = "";
        state.players.forEach((player) => {
            const li = document.createElement("li");
            li.classList.add("player-card");

            // 创建玩家基本信息容器
            const playerBasicInfo = document.createElement("div");
            playerBasicInfo.classList.add("player-basic-info");
            
            // 设置基础文本内容
            let displayText = player.name;

            // 如果是投票结束阶段且玩家有投票，显示投票结果
            if (state.phase === "投票结束" && player.voted !== -1) {
                displayText += ` (被投票数: ${player.voted})`;
            }

            playerBasicInfo.textContent = displayText;
            
            // 创建展开/折叠按钮
            const expandButton = document.createElement("span");
            expandButton.classList.add("expand-button");
            expandButton.textContent = "+";
            playerBasicInfo.appendChild(expandButton);
            
            // 创建详细信息容器
            const playerDetails = document.createElement("div");
            playerDetails.classList.add("player-details");
            playerDetails.style.display = "none";
            
            // 添加详细信息
            playerDetails.innerHTML = `
                <div>角色: ${player.role}</div>
                <div>存活: ${player.alive ? "是" : "否"}</div>
                <div>top_p值: ${player.p}</div>
            `;
            
            // 添加展开/折叠功能
            expandButton.addEventListener("click", (e) => {
                e.stopPropagation();
                if (playerDetails.style.display === "none") {
                    playerDetails.style.display = "block";
                    expandButton.textContent = "-";
                } else {
                    playerDetails.style.display = "none";
                    expandButton.textContent = "+";
                }
            });
            
            // 将基本信息和详细信息添加到列表项
            li.appendChild(playerBasicInfo);
            li.appendChild(playerDetails);

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
            else if (player.role === "WITCH") {
                li.classList.add("witch");
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
