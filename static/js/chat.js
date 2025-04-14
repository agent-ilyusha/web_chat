const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/{{ other_user.username }}/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const messagesContainer = document.getElementById('messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.sender === '{{ request.user.username }}' ? 'my-message' : 'their-message'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = data.message;

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    const now = new Date();
    timeDiv.textContent = now.getHours().toString().padStart(2, '0') + ':' +
                         now.getMinutes().toString().padStart(2, '0');

    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
};

document.querySelector('#message-form').onsubmit = function(e) {
    e.preventDefault();
    const messageInput = document.querySelector('#message-input');
    const message = messageInput.value;

    if (message.trim()) {
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        messageInput.value = '';
    }
};