document.addEventListener("DOMContentLoaded", () => {
    const contactsList = document.getElementById("chat-contacts");
    const messagesContainer = document.getElementById("messages");
    const contactName = document.getElementById("chat-title");
    const inputField = document.getElementById("messageInput");
    const sendBtn = document.getElementById("send-message");

    let currentContact = null;
    let socket = null;

    // 🔹 Buscar contatos reais do servidor
    async function loadContacts() {
        try {
            const resp = await fetch("/chat/contatos_status/");
            const contatos = await resp.json();
            renderContacts(contatos);
        } catch (err) {
            console.error("Erro ao carregar contatos:", err);
        }
    }

    // 🔹 Renderizar lista de contatos
    function renderContacts(contatos) {
        contactsList.innerHTML = "";
        contatos.forEach(c => {
            const li = document.createElement("li");
            li.classList.add("contact-item", "p-2", "border-bottom");
            li.dataset.username = c.username;

            li.innerHTML = `
                <span class="status-icon ${c.online ? "online" : "offline"} me-2"></span>
                <span class="contact-name">${c.full_name}</span>
            `;

            li.addEventListener("click", () => openConversation(c));
            contactsList.appendChild(li);
        });
    }

    // 🔹 Abrir conversa com um contato
    async function openConversation(contact) {
        currentContact = contact;
        contactName.textContent = contact.full_name;
        messagesContainer.innerHTML = "";

        // Carregar histórico
        try {
            const resp = await fetch(`/chat/historico/${contact.username}/`);
            const mensagens = await resp.json();

            mensagens.forEach(m => {
                appendMessage(m.message, m.is_own ? "sent" : "received", formatTimestamp(m.timestamp));
            });
        } catch (err) {
            console.error("Erro ao carregar mensagens:", err);
        }

        // Conectar WebSocket
        if (socket) socket.close();
        const protocol = location.protocol === "https:" ? "wss" : "ws";
        socket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${contact.username}/`);

        socket.onopen = () => {
            console.log("✅ WebSocket conectado com", contact.username);
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.message) {
                appendMessage(data.message, "received", data.timestamp);
            }
        };

        socket.onclose = () => {
            console.log("⚠️ WebSocket fechado");
        };
    }

    // 🔹 Enviar mensagem
    function sendMessage() {
        const msg = inputField.value.trim();
        if (!msg || !socket || socket.readyState !== WebSocket.OPEN) return;

        const payload = JSON.stringify({
            message: msg,
            timestamp: new Date().toISOString(),
        });

        socket.send(payload);
        appendMessage(msg, "sent", formatTimestamp(new Date().toISOString()));
        inputField.value = "";
    }

    // 🔹 Exibir mensagem na tela
    function appendMessage(text, type = "sent", timestamp = null) {
        const msgContainer = document.createElement("div");
        msgContainer.classList.add("message-container", type, "mb-2");

        msgContainer.innerHTML = `
            <div class="message-content p-2 rounded ${type === "sent" ? "bg-primary text-white" : "bg-light"}">
                <span class="message-text d-block">${text}</span>
                <div class="message-timestamp small text-muted text-end">${timestamp || ""}</div>
            </div>
        `;

        messagesContainer.appendChild(msgContainer);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // 🔹 Formatar timestamp para exibição
    function formatTimestamp(ts) {
        try {
            const date = new Date(ts);
            return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
        } catch {
            return "";
        }
    }

    // Eventos
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }
    if (inputField) {
        inputField.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Inicializar
    if (contactsList) loadContacts();
});
