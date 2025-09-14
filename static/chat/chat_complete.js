/* === SISTEMA DE CHAT COMPLETO COM WEBSOCKETS === */

console.log('🚀 Chat completo carregado');

// Sistema de chat completo
window.chatSystem = {
    openChats: new Map(),
    unreadCounts: new Map(),
    totalUnread: 0,
    nextZIndex: 9500,
    globalSocket: null,
    chatSockets: new Map(),
    notifySocket: null,
    typingTimers: new Map(),
    currentUser: null,
    isDragging: false,
    dragOffset: { x: 0, y: 0 },
    isResizing: false,
    resizeStart: { x: 0, y: 0, width: 0, height: 0 }
};

// Inicializar WebSockets
window.initChatWebSockets = function() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    
    // WebSocket global para status de usuários
    window.chatSystem.globalSocket = new WebSocket(`${protocol}//${host}/ws/global/`);
    
    window.chatSystem.globalSocket.onopen = function() {
        console.log('✅ WebSocket global conectado');
        // Solicitar lista de usuários online
        window.chatSystem.globalSocket.send(JSON.stringify({
            type: 'get_online_users'
        }));
    };
    
    window.chatSystem.globalSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleGlobalMessage(data);
    };
    
    // WebSocket para notificações
    window.chatSystem.notifySocket = new WebSocket(`${protocol}//${host}/ws/notify/`);
    
    window.chatSystem.notifySocket.onopen = function() {
        console.log('✅ WebSocket de notificações conectado');
    };
    
    window.chatSystem.notifySocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleNotificationMessage(data);
    };
    
    // Definir usuário atual
    window.chatSystem.currentUser = window.currentUser || 'anonymous';
};

// Função para mostrar/esconder dock de contatos
window.showContactsDock = function() {
    console.log('📱 Mostrando dock de contatos');
    const dock = document.getElementById('contacts-dock');
    if (dock) {
        dock.style.display = 'flex';
        loadContactsFromServer();
        console.log('✅ Dock exibido');
    } else {
        console.log('❌ Dock não encontrado');
    }
};

window.hideContactsDock = function() {
    console.log('📱 Escondendo dock de contatos');
    const dock = document.getElementById('contacts-dock');
    if (dock) {
        dock.style.display = 'none';
        console.log('✅ Dock escondido');
    }
};

// Função para carregar contatos do servidor
window.loadContactsFromServer = function() {
    fetch('/chat/contatos_status/')
        .then(response => response.json())
        .then(contatos => {
            console.log('👥 Contatos carregados:', contatos);
            renderContactsList(contatos);
        })
        .catch(error => {
            console.error('❌ Erro ao carregar contatos:', error);
            // Fallback para contatos mock
            loadMockContacts();
        });
};

// Função para renderizar lista de contatos
window.renderContactsList = function(contatos) {
    const contactsList = document.getElementById('contacts-ul');
    if (!contactsList) return;
    
    contactsList.innerHTML = '';
    
    contatos.forEach(contact => {
        const li = document.createElement('li');
        li.className = 'contact-item';
        li.setAttribute('data-username', contact.username);
        
        const unreadCount = window.chatSystem.unreadCounts.get(contact.username) || 0;
        
        li.innerHTML = `
            <div class="contact-info" onclick="startChat('${contact.username}', '${contact.full_name}', ${contact.online})">
                <div class="status-icon ${contact.online ? 'online' : 'offline'}"></div>
                <span class="contact-name">${contact.full_name}</span>
                ${unreadCount > 0 ? `<span class="contact-notification">${unreadCount > 99 ? '99+' : unreadCount}</span>` : ''}
            </div>
        `;
        
        contactsList.appendChild(li);
    });
    
    console.log('✅ Lista de contatos renderizada');
};

// Função para carregar contatos mock (fallback)
window.loadMockContacts = function() {
    const mockContacts = [
        { username: 'usuario1', full_name: 'João Silva', online: true },
        { username: 'usuario2', full_name: 'Maria Santos', online: false },
        { username: 'usuario3', full_name: 'Pedro Costa', online: true }
    ];
    renderContactsList(mockContacts);
};

// Função para iniciar chat
window.startChat = function(username, fullName, isOnline = true) {
    console.log(`🔧 Iniciando chat com: ${username} (${fullName})`);
    
    // Verificar se o chat já está aberto
    if (window.chatSystem.openChats.has(username)) {
        const existingChat = window.chatSystem.openChats.get(username);
        existingChat.style.zIndex = window.chatSystem.nextZIndex++;
        existingChat.style.display = 'flex';
        return;
    }
    
    // Criar janela de chat
    const chatWindow = createChatWindow(username, fullName, isOnline);
    
    // Conectar WebSocket para este chat
    connectChatWebSocket(username);
    
    // Carregar mensagens anteriores
    loadChatHistory(username);
    
    // Esconder dock de contatos
    hideContactsDock();
};

// Função para criar janela de chat
window.createChatWindow = function(username, fullName, isOnline = true) {
    const container = document.getElementById('chat-windows-container');
    if (!container) {
        console.log('❌ Container de chat não encontrado');
        return null;
    }
    
    const chatWindow = document.createElement('div');
    chatWindow.className = 'chat-window active';
    chatWindow.style.zIndex = window.chatSystem.nextZIndex++;
    chatWindow.setAttribute('data-username', username);
    
    // Posição inicial - posicionar no canto direito da tela
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    const chatWidth = 350;
    const chatHeight = 500;
    
    // Posicionar no canto direito, não no meio
    chatWindow.style.left = `${screenWidth - chatWidth - 20}px`;
    chatWindow.style.top = `${100}px`;
    
    chatWindow.innerHTML = `
        <div class="chat-header" onmousedown="startDrag(event, '${username}')">
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
        <div class="chat-messages" id="messages-${username}">
            <div class="typing-indicator" id="typing-${username}" style="display: none;">
                <span>${fullName} está digitando...</span>
            </div>
        </div>
        <div class="chat-input">
            <input type="text" class="chat-input-field" placeholder="Digite sua mensagem..." 
                   id="input-${username}" onkeydown="handleChatKeydown(event, '${username}')"
                   oninput="handleTyping(event, '${username}')">
            <button class="chat-send-btn" onclick="sendChatMessage('${username}')" title="Enviar">
                ➤
            </button>
        </div>
        <div class="chat-resize-handle" onmousedown="startResize(event, '${username}')"></div>
    `;
    
    container.appendChild(chatWindow);
    window.chatSystem.openChats.set(username, chatWindow);
    
    console.log('✅ Janela de chat criada com sucesso');
    return chatWindow;
};

// Função para conectar WebSocket do chat
window.connectChatWebSocket = function(username) {
    if (window.chatSystem.chatSockets.has(username)) {
        return; // Já conectado
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    
    const chatSocket = new WebSocket(`${protocol}//${host}/ws/chat/${username}/`);
    
    chatSocket.onopen = function() {
        console.log(`✅ WebSocket do chat conectado para ${username}`);
    };
    
    chatSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleChatMessage(data, username);
    };
    
    chatSocket.onclose = function() {
        console.log(`❌ WebSocket do chat fechado para ${username}`);
        window.chatSystem.chatSockets.delete(username);
    };
    
    window.chatSystem.chatSockets.set(username, chatSocket);
};

// Função para carregar histórico do chat
window.loadChatHistory = function(username) {
    fetch(`/chat/historico/${username}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(messages => {
            const messagesContainer = document.getElementById(`messages-${username}`);
            if (!messagesContainer) return;
            
            messages.forEach(msg => {
                addMessageToChat(username, msg.message, msg.sender, msg.timestamp, msg.is_own);
            });
            
            // Marcar mensagens como lidas
            window.chatSystem.unreadCounts.set(username, 0);
            updateChatBadge();
            updateContactBadge(username, 0);
            
            // Scroll para baixo
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        })
        .catch(error => {
            console.error(`❌ Erro ao carregar histórico para ${username}:`, error);
        });
};

// Função para adicionar mensagem ao chat
window.addMessageToChat = function(username, message, sender, timestamp, isOwn = false) {
    const messagesContainer = document.getElementById(`messages-${username}`);
    if (!messagesContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message-container ${isOwn ? 'sent' : 'received'}`;
    
    const time = timestamp ? new Date(timestamp).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}) : 
                             new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
    
    messageElement.innerHTML = `
        <div class="message-content">
            <div class="message-text">${message}</div>
            <div class="message-timestamp">${time}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
};

// Função para enviar mensagem
window.sendChatMessage = function(username) {
    const input = document.getElementById(`input-${username}`);
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    console.log(`📤 Enviando mensagem para ${username}: ${message}`);
    
    // Adicionar mensagem ao chat (apenas uma vez)
    addMessageToChat(username, message, window.chatSystem.currentUser, null, true);
    
    // Enviar via WebSocket
    const chatSocket = window.chatSystem.chatSockets.get(username);
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({
            message: message,
            timestamp: new Date().toISOString()
        }));
    }
    
    // Parar indicador de digitação
    stopTyping(username);
    
    input.value = '';
    console.log('✅ Mensagem enviada');
};

// Função para lidar com teclas do chat
window.handleChatKeydown = function(event, username) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage(username);
    }
};

// Função para lidar com digitação
window.handleTyping = function(event, username) {
    if (event.target.value.length > 0) {
        startTyping(username);
    } else {
        stopTyping(username);
    }
};

// Função para iniciar indicador de digitação
window.startTyping = function(username) {
    // Limpar timer existente
    if (window.chatSystem.typingTimers.has(username)) {
        clearTimeout(window.chatSystem.typingTimers.get(username));
    }
    
    // Enviar status de digitação via WebSocket global
    if (window.chatSystem.globalSocket && window.chatSystem.globalSocket.readyState === WebSocket.OPEN) {
        window.chatSystem.globalSocket.send(JSON.stringify({
            type: 'typing_start',
            recipient: username
        }));
    }
    
    // Mostrar indicador de digitação
    const typingIndicator = document.getElementById(`typing-${username}`);
    if (typingIndicator) {
        typingIndicator.style.display = 'block';
    }
    
    // Timer para parar digitação
    const timer = setTimeout(() => {
        stopTyping(username);
    }, 3000);
    
    window.chatSystem.typingTimers.set(username, timer);
};

// Função para parar indicador de digitação
window.stopTyping = function(username) {
    // Limpar timer
    if (window.chatSystem.typingTimers.has(username)) {
        clearTimeout(window.chatSystem.typingTimers.get(username));
        window.chatSystem.typingTimers.delete(username);
    }
    
    // Enviar status de digitação via WebSocket global
    if (window.chatSystem.globalSocket && window.chatSystem.globalSocket.readyState === WebSocket.OPEN) {
        window.chatSystem.globalSocket.send(JSON.stringify({
            type: 'typing_stop',
            recipient: username
        }));
    }
    
    // Esconder indicador de digitação
    const typingIndicator = document.getElementById(`typing-${username}`);
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
};

// Função para fechar chat
window.closeChat = function(username) {
    console.log(`🔒 Fechando chat: ${username}`);
    
    // Fechar WebSocket
    const chatSocket = window.chatSystem.chatSockets.get(username);
    if (chatSocket) {
        chatSocket.close();
        window.chatSystem.chatSockets.delete(username);
    }
    
    // Remover janela
    const chatWindow = window.chatSystem.openChats.get(username);
    if (chatWindow) {
        chatWindow.remove();
        window.chatSystem.openChats.delete(username);
        console.log('✅ Chat fechado');
    }
};

// Função para minimizar chat
window.minimizeChat = function(chatWindow) {
    console.log('📱 Minimizando chat');
    if (chatWindow) {
        chatWindow.classList.toggle('minimized');
        console.log('✅ Chat minimizado');
    }
};

// Função para atualizar badge do chat
window.updateChatBadge = function() {
    const totalUnread = Array.from(window.chatSystem.unreadCounts.values()).reduce((sum, count) => sum + count, 0);
    window.chatSystem.totalUnread = totalUnread;
    
    const chatToggle = document.getElementById('chat-toggle');
    if (chatToggle) {
        if (totalUnread > 0) {
            chatToggle.classList.add('notify');
            chatToggle.setAttribute('data-count', totalUnread > 99 ? '99+' : totalUnread);
        } else {
            chatToggle.classList.remove('notify');
            chatToggle.removeAttribute('data-count');
        }
    }
};

// Função para atualizar badge de um contato específico
window.updateContactBadge = function(username, count) {
    const contactItem = document.querySelector(`[data-username="${username}"]`);
    if (contactItem) {
        let notification = contactItem.querySelector('.contact-notification');
        
        if (count > 0) {
            if (!notification) {
                notification = document.createElement('span');
                notification.className = 'contact-notification';
                contactItem.querySelector('.contact-info').appendChild(notification);
            }
            notification.textContent = count > 99 ? '99+' : count;
        } else if (notification) {
            notification.remove();
        }
    }
    
    // Atualizar contador interno
    window.chatSystem.unreadCounts.set(username, count);
    updateChatBadge();
};

// Função para lidar com mensagens globais
window.handleGlobalMessage = function(data) {
    switch (data.type) {
        case 'online_users_list':
            console.log('👥 Usuários online recebidos:', data.users);
            renderContactsList(data.users);
            break;
            
        case 'user_status_change':
            console.log(`👤 Status alterado: ${data.username} = ${data.online ? 'online' : 'offline'}`);
            updateContactStatus(data.username, data.online);
            break;
            
        case 'typing_status':
            console.log(`⌨️ Status de digitação: ${data.username} = ${data.status}`);
            if (data.status === 'typing_start') {
                showTypingIndicator(data.username);
            } else if (data.status === 'typing_stop') {
                hideTypingIndicator(data.username);
            }
            break;
    }
};

// Função para lidar com mensagens de notificação
window.handleNotificationMessage = function(data) {
    if (data.type === 'new_message') {
        console.log(`🔔 Nova mensagem de ${data.sender}: ${data.message}`);
        
        // Incrementar contador de mensagens não lidas
        const sender = data.sender;
        const currentCount = window.chatSystem.unreadCounts.get(sender) || 0;
        const newCount = currentCount + 1;
        
        // Atualizar badge do contato
        updateContactBadge(sender, newCount);
        
        // Mostrar notificação se o chat não estiver aberto
        if (!window.chatSystem.openChats.has(sender)) {
            showMessageNotification(data.sender, data.message);
        }
    }
};

// Função para lidar com mensagens do chat
window.handleChatMessage = function(data, username) {
    if (data.message) {
        console.log(`📨 Mensagem recebida de ${data.sender}: ${data.message}`);
        
        // Só adicionar mensagem se não for do usuário atual (evitar duplicação)
        if (data.sender !== window.chatSystem.currentUser) {
            addMessageToChat(username, data.message, data.sender, data.timestamp, false);
            
            // Marcar como lida
            updateContactBadge(username, 0);
        }
    }
};

// Função para atualizar status do contato
window.updateContactStatus = function(username, isOnline) {
    const contactItem = document.querySelector(`[data-username="${username}"]`);
    if (contactItem) {
        const statusIcon = contactItem.querySelector('.status-icon');
        if (statusIcon) {
            statusIcon.className = `status-icon ${isOnline ? 'online' : 'offline'}`;
        }
    }
};

// Função para mostrar indicador de digitação
window.showTypingIndicator = function(username) {
    const typingIndicator = document.getElementById(`typing-${username}`);
    if (typingIndicator) {
        typingIndicator.style.display = 'block';
    }
};

// Função para esconder indicador de digitação
window.hideTypingIndicator = function(username) {
    const typingIndicator = document.getElementById(`typing-${username}`);
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
};

// Função para mostrar notificação de mensagem
window.showMessageNotification = function(sender, message) {
    // Criar notificação toast
    const notification = document.createElement('div');
    notification.className = 'message-notification';
    notification.innerHTML = `
        <div class="notification-header">
            <strong>${sender}</strong>
        </div>
        <div class="notification-body">
            ${message.length > 50 ? message.substring(0, 50) + '...' : message}
        </div>
    `;
    
    // Adicionar ao container de notificações
    const container = document.getElementById('notifications-container') || document.body;
    container.appendChild(notification);
    
    // Remover após 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
};

// === FUNCIONALIDADES DE ARRASTAR E REDIMENSIONAR ===

// Função para iniciar arrastar
window.startDrag = function(event, username) {
    event.preventDefault();
    const chatWindow = document.querySelector(`[data-username="${username}"]`);
    if (!chatWindow) return;
    
    window.chatSystem.isDragging = true;
    window.chatSystem.dragOffset.x = event.clientX - chatWindow.offsetLeft;
    window.chatSystem.dragOffset.y = event.clientY - chatWindow.offsetTop;
    
    document.addEventListener('mousemove', function(e) {
        if (window.chatSystem.isDragging) {
            chatWindow.style.left = (e.clientX - window.chatSystem.dragOffset.x) + 'px';
            chatWindow.style.top = (e.clientY - window.chatSystem.dragOffset.y) + 'px';
        }
    });
    
    document.addEventListener('mouseup', function() {
        window.chatSystem.isDragging = false;
    }, { once: true });
};

// Função para iniciar redimensionar
window.startResize = function(event, username) {
    event.preventDefault();
    const chatWindow = document.querySelector(`[data-username="${username}"]`);
    if (!chatWindow) return;
    
    window.chatSystem.isResizing = true;
    window.chatSystem.resizeStart.x = event.clientX;
    window.chatSystem.resizeStart.y = event.clientY;
    window.chatSystem.resizeStart.width = chatWindow.offsetWidth;
    window.chatSystem.resizeStart.height = chatWindow.offsetHeight;
    
    document.addEventListener('mousemove', function(e) {
        if (window.chatSystem.isResizing) {
            const newWidth = window.chatSystem.resizeStart.width + (e.clientX - window.chatSystem.resizeStart.x);
            const newHeight = window.chatSystem.resizeStart.height + (e.clientY - window.chatSystem.resizeStart.y);
            
            // Limites mínimos
            const minWidth = 300;
            const minHeight = 400;
            
            if (newWidth >= minWidth) {
                chatWindow.style.width = newWidth + 'px';
            }
            if (newHeight >= minHeight) {
                chatWindow.style.height = newHeight + 'px';
            }
        }
    });
    
    document.addEventListener('mouseup', function() {
        window.chatSystem.isResizing = false;
    }, { once: true });
};

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado - inicializando chat completo');
    
    // Inicializar WebSockets
    initChatWebSockets();
    
    // Event listener para o botão de chat
    const chatToggle = document.getElementById('chat-toggle');
    if (chatToggle) {
        console.log('✅ Botão chat encontrado');
        chatToggle.onclick = function() {
            console.log('🖱️ Botão chat clicado');
            const dock = document.getElementById('contacts-dock');
            if (dock && dock.style.display === 'flex') {
                window.hideContactsDock();
            } else {
                window.showContactsDock();
            }
        };
    } else {
        console.log('❌ Botão chat não encontrado');
    }
    
    // Event listener para fechar contatos
    const closeContacts = document.getElementById('close-contacts');
    if (closeContacts) {
        console.log('✅ Botão fechar encontrado');
        closeContacts.onclick = window.hideContactsDock;
    } else {
        console.log('❌ Botão fechar não encontrado');
    }
    
    console.log('✅ Chat completo inicializado');
});

console.log('📋 Chat completo carregado com sucesso');
