const currentUser = document.querySelector('meta[name="current-user"]').getAttribute('content');
const chatUser = document.querySelector('meta[name="chat-user"]').getAttribute('content');
const usernames = [currentUser, chatUser].sort();
const roomName = `${usernames[0]}_${usernames[1]}`;

const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/' + roomName + '/'
);

function addMessage(message, username, timestamp) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) {
        console.error("Элемент chat-messages не найден");
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${username === currentUser ? 'my-message' : 'their-message'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = message;

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

chatSocket.onopen = function(e) {
    console.log("WebSocket соединение установлено");
    console.log("Room name:", roomName);
};

chatSocket.onerror = function(e) {
    console.error("WebSocket ошибка:", e);
};

chatSocket.onclose = function(e) {
    console.log("WebSocket соединение закрыто");
};

chatSocket.onmessage = function(e) {
    console.log("Получено сообщение:", e.data);
    const data = JSON.parse(e.data);
    
    if (data.type === 'chat_history') {
        console.log("Загрузка истории сообщений:", data.messages);
        data.messages.forEach(msg => {
            addMessage(msg.message, msg.username, msg.timestamp);
        });
    } else {
        console.log("Новое сообщение:", data);
        addMessage(data.message, data.username, data.timestamp);
    }
};

const messageForm = document.querySelector('#message-form');
if (messageForm) {
    console.log("Форма сообщений найдена");
    messageForm.onsubmit = function(e) {
        e.preventDefault();
        console.log("Форма отправлена");
        const messageInput = document.querySelector('#message-text');
        if (!messageInput) {
            console.error("Поле ввода сообщения не найдено");
            return;
        }
        
        const message = messageInput.value;
        console.log("Текст сообщения:", message);

        if (message.trim()) {
            console.log("Отправка сообщения через WebSocket");
            const messageData = {
                'message': message,
                'username': currentUser,
                'timestamp': new Date().toISOString()
            };
            console.log("Данные сообщения:", messageData);
            
            try {
                chatSocket.send(JSON.stringify(messageData));
                console.log("Сообщение отправлено");
                messageInput.value = '';
            } catch (error) {
                console.error("Ошибка при отправке сообщения:", error);
            }
        }
    };
} else {
    console.error("Форма сообщений не найдена");
}