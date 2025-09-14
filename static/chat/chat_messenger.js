// Socket agora é gerenciado globalmente em base.html
// currentChatUser agora é gerenciado globalmente em window.currentChatUser
let typingTimer = null;
let isTyping = false;

/* --- Dock de Contatos --- */
function showContactsDock() {
  const dock = document.getElementById('contacts-dock');
  if (dock) {
    dock.style.display = 'flex';
    loadContacts();
  }
}

function hideContactsDock() {
  const dock = document.getElementById('contacts-dock');
  if (dock) {
    dock.style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Event listeners para abrir o dock de contatos
  document.getElementById('chat-toggle')?.addEventListener('click', () => {
    showContactsDock();
  });

  document.getElementById('navbar-chat-icon')?.addEventListener('click', () => {
    showContactsDock();
  });

  // Event listener para fechar o dock de contatos
  document.getElementById('close-contacts')?.addEventListener('click', () => {
    hideContactsDock();
  });

  // Event listener para fechar o chat
  document.getElementById('close-chat')?.addEventListener('click', () => {
    closeChatBox();
  });

  // Event listener para enviar mensagem com botão
  document.getElementById('send-message')?.addEventListener('click', () => {
    sendMessage();
  });

  // Event listener para enviar mensagem com Enter e detectar digitação
  document.getElementById('messageInput')?.addEventListener('keydown', (event) => {
    handleKey(event);
  });

  // Atualizar status dos contatos a cada 30 segundos
  setInterval(() => {
    const dock = document.getElementById('contacts-dock');
    if (dock && dock.style.display !== 'none') {
      loadContacts();
    }
  }, 30000);
});


function loadContacts() {
  fetch('/chat/contatos_status/')
    .then(r => r.json())
    .then(data => {
      const ul = document.getElementById('contacts-ul') || document.getElementById('chat-contacts');
      if (!ul) return;
      ul.innerHTML = '';
      data.forEach(u => {
        const li = document.createElement('li');
        li.onclick = () => startChat(u.username, u.full_name, u.online);
        
        const dot = document.createElement('span');
        dot.className = 'status-icon ' + (u.online ? 'online' : 'offline');

        const name = document.createElement('span');
        name.textContent = u.full_name;

        li.appendChild(dot);
        li.appendChild(name);
        ul.appendChild(li);
      });
    });
}

/* --- Chat --- */
function appendMessage(sender, message, isOwnMessage = false) {
    const messagesDiv = document.getElementById("messages");

    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message");

    if (isOwnMessage) {
        msgDiv.classList.add("sent");
    } else {
        msgDiv.classList.add("received");
    }

    msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function startChat(username, fullName, isOnline) {
  console.log('Abrindo chat com:', username);
  document.getElementById('chat-title').textContent = fullName;
  const statusIcon = document.getElementById('chat-status');
  if (statusIcon) {
    statusIcon.className = "status-icon " + (isOnline ? "online" : "offline");
  }

  document.getElementById('chat-box').style.display = 'flex';
  window.currentChatUser = username;  // ✅ Usar variável global

  if (window.clearUnreadFor) {
    window.clearUnreadFor(username);
  }

  const messagesEl = document.getElementById('messages');
  messagesEl.innerHTML = '';
  fetch(`/chat/historico/${username}/`)
    .then(res => res.json())
    .then(items => {
      items.forEach(m => {
        if (window.addMessageBubble) {
          window.addMessageBubble(m.sender, m.message, m.timestamp, m.read, m.is_own);
        }
      });
      messagesEl.scrollTop = messagesEl.scrollHeight;
    });

  // Conectar WebSocket para este usuário específico
  console.log("Conectando WebSocket para chat com:", username);
  if (window.connectChatSocket) {
    window.connectChatSocket(username);
  }
}

function handleKey(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    sendMessage();
    stopTyping();
  } else {
    startTyping();
  }
}

// Função sendMessage agora é gerenciada pelo socket global em base.html

function closeChatBox() {
    document.getElementById("chat-box").style.display = "none";
    stopTyping();
}

/* --- Indicador de Digitação --- */
function startTyping() {
  if (!window.currentChatUser) return;
  
  // Usar o WebSocket específico para o usuário atual
  const socket = window.chatSockets ? window.chatSockets.get(window.currentChatUser) : null;
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  
  if (!window.isTyping) {
    window.isTyping = true;
    socket.send(JSON.stringify({
      'type': 'typing_start',
      'sender': window.LOGGED_USER,
    }));
  }
  
  // Reset timer - para de digitar após 3 segundos sem atividade
  clearTimeout(window.typingTimer);
  window.typingTimer = setTimeout(stopTyping, 3000);
}

function stopTyping() {
  if (!window.currentChatUser) return;
  
  // Usar o WebSocket específico para o usuário atual
  const socket = window.chatSockets ? window.chatSockets.get(window.currentChatUser) : null;
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  
  if (window.isTyping) {
    window.isTyping = false;
    socket.send(JSON.stringify({
      'type': 'typing_stop',
      'sender': window.LOGGED_USER,
    }));
  }
  
  clearTimeout(window.typingTimer);
}

function showTypingIndicator(username) {
  const typingDiv = document.getElementById('typing-indicator');
  if (typingDiv) {
    typingDiv.textContent = `${username} está digitando...`;
    typingDiv.style.display = 'block';
  }
}

function hideTypingIndicator() {
  const typingDiv = document.getElementById('typing-indicator');
  if (typingDiv) {
    typingDiv.style.display = 'none';
  }
}

function addMessageBubble(sender, text, tsIso, read = false, isOwn = false) {
  const messagesEl = document.getElementById('messages');
  const p = document.createElement('p');
          const when = tsIso ? ` - ${fmtTs(tsIso)}` : '';
  
  // Adicionar indicador de leitura para mensagens próprias
  let readStatus = '';
  if (isOwn) {
    readStatus = read ? ' [Lido]' : ' [Enviado]';
  }
  
  p.textContent = `${sender}: ${text}${when}${readStatus}`;
  p.classList.add(isOwn ? 'sent' : 'received');
  messagesEl.appendChild(p);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

/* --- Utilidades --- */

function fmtTs(iso) {
  try {
    const d = new Date(iso);
    const dd = d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    const hh = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    return `${dd} ${hh}`;
  } catch (e) {
    return '';
  }
}

/* --- Notificações --- */

// Usar o sistema de contadores do template base se disponível
if (!window.unreadByUser) {
    window.unreadByUser = new Map();
}
if (!window.totalUnread) {
    window.totalUnread = 0;
}
const unreadByUser = window.unreadByUser;
const totalUnread = window.totalUnread;

// Função updateBadge removida - agora usa as funções globais do base.html

// Função incUnread removida - agora usa window.incUnread do base.html

// Função clearUnreadFor removida - agora usa window.clearUnreadFor do base.html

function playNotifySound() {
  const el = document.getElementById('chat-sound');
  if (!el) return;
  el.currentTime = 0;
  el.play().catch(() => {});
}

document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    const chatBox = document.getElementById('chat-box');
    const contactsDock = document.getElementById('contacts-dock');
    if (chatBox.style.display === 'flex') {
      closeChatBox();
    } else if (contactsDock.style.display === 'flex') {
      hideContactsDock();
    }
  }
});


/* --- Exporta para uso global --- */
window.startChat = startChat;
window.sendMessage = sendMessage;
window.handleKey = handleKey;
window.closeChatBox = closeChatBox;
window.showContactsDock = showContactsDock;
window.hideContactsDock = hideContactsDock;