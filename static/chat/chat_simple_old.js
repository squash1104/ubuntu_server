/* === SISTEMA DE CHAT SIMPLIFICADO PARA TESTE === */

console.log('🚀 Chat simples carregado');

// Sistema básico de chat
window.chatSystem = {
    openChats: new Map(),
    unreadCounts: new Map(),
    totalUnread: 0,
    nextZIndex: 9500
};

// Função para mostrar/esconder dock de contatos
window.showContactsDock = function() {
    console.log('📱 Mostrando dock de contatos');
    const dock = document.getElementById('contacts-dock');
    if (dock) {
        dock.style.display = 'flex';
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

// Função para criar janela de chat
window.createChatWindow = function(username, fullName, isOnline = true) {
    console.log(`🔧 Criando chat para: ${username} (${fullName})`);
    
    const container = document.getElementById('chat-windows-container');
    if (!container) {
        console.log('❌ Container de chat não encontrado');
        return null;
    }
    
    const chatWindow = document.createElement('div');
    chatWindow.className = 'chat-window active';
    chatWindow.style.zIndex = window.chatSystem.nextZIndex++;
    chatWindow.setAttribute('data-username', username);
    
    // Posição inicial
    const existingChats = container.querySelectorAll('.chat-window').length;
    const offsetX = existingChats * 25;
    const offsetY = existingChats * 25;
    chatWindow.style.left = `${50 + offsetX}px`;
    chatWindow.style.top = `${50 + offsetY}px`;
    
    chatWindow.innerHTML = `
        <div class="chat-header">
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
            <div style="padding: 20px; text-align: center; color: #666;">
                Chat iniciado com ${fullName}
            </div>
        </div>
        <div class="chat-input">
            <input type="text" class="chat-input-field" placeholder="Digite sua mensagem..." 
                   id="input-${username}">
            <button class="chat-send-btn" onclick="sendChatMessage('${username}')" title="Enviar">
                ➤
            </button>
        </div>
    `;
    
    container.appendChild(chatWindow);
    window.chatSystem.openChats.set(username, chatWindow);
    
    console.log('✅ Janela de chat criada com sucesso');
    return chatWindow;
};

// Função para fechar chat
window.closeChat = function(username) {
    console.log(`🔒 Fechando chat: ${username}`);
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

// Função para enviar mensagem
window.sendChatMessage = function(username) {
    const input = document.getElementById(`input-${username}`);
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    console.log(`📤 Enviando mensagem para ${username}: ${message}`);
    
    // Adicionar mensagem ao chat
    const messagesContainer = document.getElementById(`messages-${username}`);
    if (messagesContainer) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message-container sent';
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="message-text">${message}</div>
                <div class="message-timestamp">${new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}</div>
            </div>
        `;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    input.value = '';
    console.log('✅ Mensagem enviada');
};

// Função para carregar contatos (simulada)
window.loadContacts = function() {
    console.log('👥 Carregando contatos...');
    const contactsList = document.getElementById('contacts-ul');
    if (contactsList) {
        // Simular alguns contatos
        const mockContacts = [
            { username: 'usuario1', full_name: 'João Silva', is_online: true },
            { username: 'usuario2', full_name: 'Maria Santos', is_online: false },
            { username: 'usuario3', full_name: 'Pedro Costa', is_online: true }
        ];
        
        contactsList.innerHTML = '';
        mockContacts.forEach(contact => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px; padding: 8px;">
                    <div class="status-icon ${contact.is_online ? 'online' : 'offline'}"></div>
                    <span>${contact.full_name}</span>
                    <button onclick="createChatWindow('${contact.username}', '${contact.full_name}', ${contact.is_online})" 
                            style="margin-left: auto; background: #007bff; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer;">
                        Chat
                    </button>
                </div>
            `;
            contactsList.appendChild(li);
        });
        
        console.log('✅ Contatos carregados');
    }
};

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado - inicializando chat simples');
    
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
                window.loadContacts();
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
    
    console.log('✅ Chat simples inicializado');
});

console.log('📋 Chat simples carregado com sucesso');
