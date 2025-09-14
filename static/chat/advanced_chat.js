/* === SISTEMA DE CHAT AVANÇADO === */

// Variáveis globais do sistema de chat
window.chatSystem = {
    openChats: new Map(), // username -> chatWindow
    unreadCounts: new Map(), // username -> count
    totalUnread: 0,
    nextZIndex: 9500,
    chatSockets: new Map(), // username -> WebSocket
    notifySocket: null,
    dragData: null,
    resizeData: null
};

// Sistema de notificações nativas do navegador
window.requestNotificationPermission = async function() {
    if ("Notification" in window && Notification.permission === "default") {
        const permission = await Notification.requestPermission();
        console.log('Permissão de notificação:', permission);
        return permission === "granted";
    }
    return Notification.permission === "granted";
};

// Mostrar notificação nativa
window.showNativeNotification = function(title, body, icon = null) {
    if ("Notification" in window && Notification.permission === "granted") {
        const notification = new Notification(title, {
            body: body,
            icon: icon || '/static/images/logo.png',
            badge: '/static/images/logo.png',
            tag: 'chat-message',
            requireInteraction: false
        });
        
        // Auto-fechar após 5 segundos
        setTimeout(() => notification.close(), 5000);
        
        // Clique na notificação foca a janela
        notification.onclick = function() {
            window.focus();
            notification.close();
        };
    }
};

// Sistema de Toast (notificações na tela)
window.showToast = function(username, fullName, message) {
    const container = document.querySelector('.toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <div class="toast-header">
            <div class="toast-avatar">${fullName.charAt(0).toUpperCase()}</div>
            <div class="toast-title">${fullName}</div>
            <div class="toast-time">${new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}</div>
        </div>
        <div class="toast-message">${message}</div>
    `;
    
    // Clique no toast abre o chat
    toast.onclick = () => {
        window.openChatWindow(username, fullName);
        toast.remove();
    };
    
    container.appendChild(toast);
    
    // Animação de entrada
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
};

// Criar uma nova janela de chat
window.createChatWindow = function(username, fullName, isOnline = true) {
    const container = document.getElementById('chat-windows-container');
    if (!container) return null;
    
    const chatWindow = document.createElement('div');
    chatWindow.className = 'chat-window active';
    chatWindow.style.zIndex = window.chatSystem.nextZIndex++;
    chatWindow.setAttribute('data-username', username);
    
    // Posição inicial (cascata) - mais compacta
    const existingChats = container.querySelectorAll('.chat-window').length;
    const offsetX = existingChats * 25;
    const offsetY = existingChats * 25;
    chatWindow.style.left = `${50 + offsetX}px`;
    chatWindow.style.top = `${50 + offsetY}px`;
    
    chatWindow.innerHTML = `
        <div class="chat-header" onmousedown="startDrag(event, this.parentElement)">
            <div class="chat-contact-info">
                <div class="status-icon ${isOnline ? 'online' : 'offline'}"></div>
                <div class="chat-contact-name">${fullName}</div>
            </div>
            <div class="chat-actions">
                <button class="chat-action-btn" onclick="minimizeChat(this.closest('.chat-window'))" title="Minimizar">
                    ➖
                </button>
                <button class="chat-action-btn" onclick="closeChat('${username}')" title="Fechar">
                    ✕
                </button>
            </div>
        </div>
        <div class="chat-messages" id="messages-${username}"></div>
        <div class="typing-indicator" id="typing-${username}" style="display: none;">
            <span id="typing-text-${username}">${fullName} está digitando</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        <div class="chat-input">
            <input type="text" class="chat-input-field" placeholder="Digite sua mensagem..." 
                   onkeydown="handleChatKey(event, '${username}')" id="input-${username}">
            <button class="chat-send-btn" onclick="sendChatMessage('${username}')" title="Enviar">
                ➤
            </button>
        </div>
        <div class="resize-handle" onmousedown="startResize(event, this.parentElement)"></div>
    `;
    
    container.appendChild(chatWindow);
    
    // Focar no chat recém-criado
    focusChat(chatWindow);
    
    // Conectar WebSocket
    connectChatSocket(username);
    
    // Carregar histórico
    loadChatHistory(username);
    
    return chatWindow;
};

// Abrir janela de chat (ou focar se já existe)
window.openChatWindow = function(username, fullName, isOnline = true) {
    let chatWindow = window.chatSystem.openChats.get(username);
    
    if (chatWindow && document.body.contains(chatWindow)) {
        // Chat já existe, apenas focar
        focusChat(chatWindow);
        chatWindow.classList.remove('minimized');
    } else {
        // Criar novo chat
        chatWindow = createChatWindow(username, fullName, isOnline);
        if (chatWindow) {
            window.chatSystem.openChats.set(username, chatWindow);
        }
    }
    
    // Esconder dock de contatos
    window.hideContactsDock();
    
    // Limpar contador de não lidas
    window.chatSystem.unreadCounts.set(username, 0);
    updateChatBadge();
    
    return chatWindow;
};

// Fechar chat
window.closeChat = function(username) {
    const chatWindow = window.chatSystem.openChats.get(username);
    if (chatWindow) {
        chatWindow.remove();
        window.chatSystem.openChats.delete(username);
        
        // Desconectar WebSocket
        const socket = window.chatSystem.chatSockets.get(username);
        if (socket) {
            socket.close();
            window.chatSystem.chatSockets.delete(username);
        }
    }
};

// Minimizar/maximizar chat
window.minimizeChat = function(chatWindow) {
    chatWindow.classList.toggle('minimized');
};

// Focar chat (trazer para frente)
window.focusChat = function(chatWindow) {
    // Remover classe active de todos os chats
    document.querySelectorAll('.chat-window').forEach(w => w.classList.remove('active'));
    
    // Adicionar classe active ao chat atual
    chatWindow.classList.add('active');
    chatWindow.style.zIndex = window.chatSystem.nextZIndex++;
    
    // Focar no input
    const input = chatWindow.querySelector('.chat-input-field');
    if (input) input.focus();
};

// Sistema de arrastar
window.startDrag = function(e, chatWindow) {
    if (e.target.closest('.chat-action-btn')) return;
    
    window.chatSystem.dragData = {
        chatWindow: chatWindow,
        startX: e.clientX - chatWindow.offsetLeft,
        startY: e.clientY - chatWindow.offsetTop
    };
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
    
    focusChat(chatWindow);
    e.preventDefault();
};

window.drag = function(e) {
    if (!window.chatSystem.dragData) return;
    
    const { chatWindow, startX, startY } = window.chatSystem.dragData;
    const newX = e.clientX - startX;
    const newY = e.clientY - startY;
    
    // Limites da tela
    const maxX = window.innerWidth - chatWindow.offsetWidth;
    const maxY = window.innerHeight - chatWindow.offsetHeight;
    
    chatWindow.style.left = `${Math.max(0, Math.min(maxX, newX))}px`;
    chatWindow.style.top = `${Math.max(0, Math.min(maxY, newY))}px`;
};

window.stopDrag = function() {
    window.chatSystem.dragData = null;
    document.removeEventListener('mousemove', drag);
    document.removeEventListener('mouseup', stopDrag);
};

// Sistema de redimensionar
window.startResize = function(e, chatWindow) {
    window.chatSystem.resizeData = {
        chatWindow: chatWindow,
        startWidth: chatWindow.offsetWidth,
        startHeight: chatWindow.offsetHeight,
        startX: e.clientX,
        startY: e.clientY
    };
    
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
    
    e.preventDefault();
    e.stopPropagation();
};

window.resize = function(e) {
    if (!window.chatSystem.resizeData) return;
    
    const { chatWindow, startWidth, startHeight, startX, startY } = window.chatSystem.resizeData;
    const newWidth = startWidth + (e.clientX - startX);
    const newHeight = startHeight + (e.clientY - startY);
    
    // Aplicar limites
    const minWidth = 300;
    const minHeight = 400;
    const maxWidth = 600;
    const maxHeight = window.innerHeight * 0.8;
    
    chatWindow.style.width = `${Math.max(minWidth, Math.min(maxWidth, newWidth))}px`;
    chatWindow.style.height = `${Math.max(minHeight, Math.min(maxHeight, newHeight))}px`;
};

window.stopResize = function() {
    window.chatSystem.resizeData = null;
    document.removeEventListener('mousemove', resize);
    document.removeEventListener('mouseup', stopResize);
};

// Conectar WebSocket para chat específico
window.connectChatSocket = function(username) {
    if (window.chatSystem.chatSockets.has(username)) return;
    
    const protocol = (location.protocol === 'https:') ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${username}/`);
    
    socket.onopen = () => {
        console.log(`WebSocket conectado para ${username}`);
        window.chatSystem.chatSockets.set(username, socket);
    };
    
    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        handleChatMessage(username, data);
    };
    
    socket.onclose = () => {
        console.log(`WebSocket desconectado para ${username}`);
        window.chatSystem.chatSockets.delete(username);
    };
    
    socket.onerror = (error) => {
        console.error(`Erro no WebSocket para ${username}:`, error);
    };
};

// Processar mensagem recebida
window.handleChatMessage = function(username, data) {
    if (data.type === 'typing_start') {
        showTypingIndicator(username, data.sender);
        return;
    }
    
    if (data.type === 'typing_stop') {
        hideTypingIndicator(username);
        return;
    }
    
    if (data.message) {
        addMessageToChat(username, data.message, data.sender, data.timestamp);
    }
};

// Adicionar mensagem ao chat com novos estilos
window.addMessageToChat = function(username, message, sender, timestamp) {
    const messagesContainer = document.getElementById(`messages-${username}`);
    if (!messagesContainer) return;
    
    const isOwn = sender === window.currentUser;
    const messageElement = document.createElement('div');
    messageElement.className = `message-container ${isOwn ? 'sent' : 'received'}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.textContent = message;
    
    messageContent.appendChild(messageText);
    
    if (timestamp) {
        const timestampElement = document.createElement('div');
        timestampElement.className = 'message-timestamp';
        timestampElement.textContent = new Date(timestamp).toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        messageContent.appendChild(timestampElement);
    }
    
    messageElement.appendChild(messageContent);
    messagesContainer.appendChild(messageElement);
    
    // Scroll para a última mensagem
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Adicionar animação de entrada
    messageElement.style.opacity = '0';
    messageElement.style.transform = 'translateY(10px)';
    setTimeout(() => {
        messageElement.style.transition = 'all 0.3s ease';
        messageElement.style.opacity = '1';
        messageElement.style.transform = 'translateY(0)';
    }, 10);
};

// Enviar mensagem
window.sendChatMessage = function(username) {
    const input = document.getElementById(`input-${username}`);
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    const socket = window.chatSystem.chatSockets.get(username);
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            message: message,
            timestamp: new Date().toISOString(),
            sender: window.LOGGED_USER
        }));
        
        input.value = '';
        stopTypingIndicator(username);
    }
};

// Manipular teclas do chat
window.handleChatKey = function(event, username) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendChatMessage(username);
    } else {
        startTypingIndicator(username);
    }
};

// Indicador de digitação
let typingTimers = new Map();

window.startTypingIndicator = function(username) {
    const socket = window.chatSystem.chatSockets.get(username);
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'typing_start',
            sender: window.LOGGED_USER
        }));
        
        // Auto-parar após 3 segundos
        if (typingTimers.has(username)) {
            clearTimeout(typingTimers.get(username));
        }
        
        const timer = setTimeout(() => stopTypingIndicator(username), 3000);
        typingTimers.set(username, timer);
    }
};

window.stopTypingIndicator = function(username) {
    const socket = window.chatSystem.chatSockets.get(username);
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'typing_stop',
            sender: window.LOGGED_USER
        }));
    }
    
    if (typingTimers.has(username)) {
        clearTimeout(typingTimers.get(username));
        typingTimers.delete(username);
    }
};

window.showTypingIndicator = function(username, sender) {
    const indicator = document.getElementById(`typing-${username}`);
    const text = document.getElementById(`typing-text-${username}`);
    if (indicator && text) {
        text.textContent = `${sender} está digitando`;
        indicator.style.display = 'block';
    }
};

window.hideTypingIndicator = function(username) {
    const indicator = document.getElementById(`typing-${username}`);
    if (indicator) {
        indicator.style.display = 'none';
    }
};

// Carregar histórico do chat
window.loadChatHistory = function(username) {
    fetch(`/chat/historico/${username}/`)
        .then(response => response.json())
        .then(messages => {
            messages.forEach(msg => {
                addMessageToChat(username, msg.message, msg.sender, msg.timestamp);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar histórico:', error);
        });
};

// Atualizar badge do botão principal
window.updateChatBadge = function() {
    const badge = document.getElementById('chat-badge');
    const button = document.getElementById('chat-toggle');
    
    let total = 0;
    window.chatSystem.unreadCounts.forEach(count => total += count);
    window.chatSystem.totalUnread = total;
    
    if (total > 0) {
        badge.textContent = total > 99 ? '99+' : total;
        badge.style.display = 'inline-block';
        button.classList.add('notify');
    } else {
        badge.style.display = 'none';
        button.classList.remove('notify');
    }
};

// Carregar lista de contatos
window.loadContacts = function() {
    fetch('/chat/contatos_status/')
        .then(response => response.json())
        .then(contacts => {
            const ul = document.getElementById('contacts-ul');
            if (!ul) return;
            
            ul.innerHTML = '';
            contacts.forEach(contact => {
                const li = document.createElement('li');
                li.onclick = () => openChatWindow(contact.username, contact.full_name, contact.online);
                
                const unreadCount = window.chatSystem.unreadCounts.get(contact.username) || 0;
                
                li.innerHTML = `
                    <div class="status-icon ${contact.online ? 'online' : 'offline'}"></div>
                    <div class="contact-name">${contact.full_name}</div>
                    ${unreadCount > 0 ? `<div class="contact-notification">${unreadCount > 99 ? '99+' : unreadCount}</div>` : ''}
                `;
                
                ul.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar contatos:', error);
        });
};

// Conectar socket de notificações globais
window.connectNotifySocket = function() {
    if (window.chatSystem.notifySocket) return;
    
    const protocol = (location.protocol === 'https:') ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/notify/`);
    
    socket.onopen = () => {
        console.log('Socket de notificações conectado');
        window.chatSystem.notifySocket = socket;
    };
    
    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'new_message') {
            handleNewMessageNotification(data.sender, data.message);
        }
    };
    
    socket.onclose = () => {
        console.log('Socket de notificações desconectado');
        window.chatSystem.notifySocket = null;
        // Reconectar após 3 segundos
        setTimeout(connectNotifySocket, 3000);
    };
};

// Processar notificação de nova mensagem
window.handleNewMessageNotification = function(username, message) {
    // Buscar nome completo do usuário
    fetch('/chat/contatos_status/')
        .then(response => response.json())
        .then(contacts => {
            const contact = contacts.find(c => c.username === username);
            const fullName = contact ? contact.full_name : username;
            
            // Verificar se o chat está aberto e ativo
            const chatWindow = window.chatSystem.openChats.get(username);
            const isActive = chatWindow && !chatWindow.classList.contains('minimized') && 
                           chatWindow.classList.contains('active') && !document.hidden;
            
            if (!isActive) {
                // Incrementar contador
                const current = window.chatSystem.unreadCounts.get(username) || 0;
                window.chatSystem.unreadCounts.set(username, current + 1);
                updateChatBadge();
                
                // Mostrar notificações
                showNativeNotification(`Nova mensagem de ${fullName}`, message);
                showToast(username, fullName, message);
                
                // Tocar som
                const audio = document.getElementById('chat-sound');
                if (audio) {
                    audio.currentTime = 0;
                    audio.play().catch(() => {});
                }
                
                // Atualizar lista de contatos se estiver aberta
                const dock = document.getElementById('contacts-dock');
                if (dock && dock.style.display === 'flex') {
                    loadContacts();
                }
            }
        });
};

// Inicializar sistema
document.addEventListener('DOMContentLoaded', function() {
    // Solicitar permissão para notificações
    requestNotificationPermission();
    
    // Conectar socket de notificações
    connectNotifySocket();
    
    // Event listeners
    const chatToggle = document.getElementById('chat-toggle');
    if (chatToggle) {
        chatToggle.onclick = () => {
            const dock = document.getElementById('contacts-dock');
            if (dock.style.display === 'flex') {
                window.hideContactsDock();
            } else {
                window.showContactsDock();
            }
        };
    }
    
    const closeContacts = document.getElementById('close-contacts');
    if (closeContacts) {
        closeContacts.onclick = window.hideContactsDock;
    }
    
    // Fechar dock ao clicar fora
    document.addEventListener('click', function(e) {
        const dock = document.getElementById('contacts-dock');
        const toggle = document.getElementById('chat-toggle');
        
        if (dock && dock.style.display === 'flex' && 
            !dock.contains(e.target) && !toggle.contains(e.target)) {
            window.hideContactsDock();
        }
    });
    
    // Focar chat ao clicar
    document.addEventListener('click', function(e) {
        const chatWindow = e.target.closest('.chat-window');
        if (chatWindow) {
            focusChat(chatWindow);
        }
    });
});

// Mostrar/esconder dock de contatos
window.showContactsDock = function() {
    const dock = document.getElementById('contacts-dock');
    if (dock) {
        dock.style.display = 'flex';
        loadContacts();
    }
};

window.hideContactsDock = function() {
    const dock = document.getElementById('contacts-dock');
    if (dock) {
        dock.style.display = 'none';
    }
};
