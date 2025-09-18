/**
 * Sistema de Chat Dedicado - Versão Refatorada
 * Gerencia conexões WebSocket para chat entre dois usuários específicos
 */

class DedicatedChat {
    constructor() {
        this.socket = null;
        this.currentUser = null;
        this.targetUser = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.reconnectTimeout = null;
        this.isManualClose = false;
        this.typingTimeout = null;
        this.isTyping = false;
        
        // Bind methods
        this.connect = this.connect.bind(this);
        this.disconnect = this.disconnect.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
        this.handleTyping = this.handleTyping.bind(this);
        this.handleSeen = this.handleSeen.bind(this);
        
        console.log('🚀 Sistema de Chat Dedicado inicializado');
    }

    /**
     * Conectar ao chat com um usuário específico
     */
    async connect(targetUsername) {
        try {
            console.log(`🔌 Conectando ao chat com: ${targetUsername}`);
            
            // Limpar conexão anterior
            this.disconnect();
            
            this.targetUser = targetUsername;
            this.currentUser = window.LOGGED_USER;
            
            if (!this.currentUser) {
                throw new Error('Usuário não autenticado');
            }
            
            // Construir URL do WebSocket
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/ws/chat/${targetUsername}/`;
            
            console.log(`🔌 Conectando ao WebSocket: ${wsUrl}`);
            
            // Criar conexão WebSocket
            this.socket = new WebSocket(wsUrl);
            
            // Configurar event listeners
            this.setupEventListeners();
            
        } catch (error) {
            console.error('❌ Erro ao conectar chat:', error);
            this.handleConnectionError(error);
        }
    }

    /**
     * Configurar event listeners do WebSocket
     */
    setupEventListeners() {
        if (!this.socket) return;

        this.socket.onopen = (event) => {
            console.log('✅ WebSocket do chat conectado com sucesso');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
            this.isManualClose = false;
            
            // Notificar interface
            this.onConnectionEstablished();
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 Mensagem recebida:', data);
                this.handleMessage(data);
            } catch (error) {
                console.error('❌ Erro ao processar mensagem:', error);
            }
        };

        this.socket.onerror = (error) => {
            console.error('❌ Erro no WebSocket:', error);
            this.handleConnectionError(error);
        };

        this.socket.onclose = (event) => {
            console.log('❌ WebSocket desconectado:', {
                code: event.code,
                reason: event.reason,
                wasClean: event.wasClean,
                isManualClose: this.isManualClose
            });
            
            this.isConnected = false;
            
            // Tentar reconectar se não foi fechamento manual
            if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.attemptReconnect();
            } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                console.error('❌ Máximo de tentativas de reconexão atingido');
                this.onConnectionFailed();
            }
        };
    }

    /**
     * Tentar reconectar
     */
    attemptReconnect() {
        this.reconnectAttempts++;
        console.log(`🔄 Tentativa de reconexão ${this.reconnectAttempts}/${this.maxReconnectAttempts} em ${this.reconnectDelay}ms`);
        
        this.reconnectTimeout = setTimeout(() => {
            if (this.targetUser) {
                this.connect(this.targetUser);
            }
        }, this.reconnectDelay);
        
        // Aumentar delay exponencialmente (máximo 30 segundos)
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
    }

    /**
     * Desconectar do chat
     */
    disconnect() {
        console.log('🔌 Desconectando do chat');
        
        this.isManualClose = true;
        
        // Limpar timeout de reconexão
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        
        // Fechar WebSocket
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        
        this.isConnected = false;
        this.targetUser = null;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
    }

    /**
     * Enviar mensagem
     */
    sendMessage(message) {
        if (!this.isConnected || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.error('❌ WebSocket não conectado, não é possível enviar mensagem');
            return false;
        }

        if (!message || !message.trim()) {
            console.warn('⚠️ Mensagem vazia ignorada');
            return false;
        }

        try {
            const payload = {
                type: 'message',
                message: message.trim(),
                timestamp: new Date().toISOString()
            };

            console.log('📤 Enviando mensagem:', payload);
            this.socket.send(JSON.stringify(payload));
            
            // Parar indicador de digitação
            this.stopTyping();
            
            return true;
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem:', error);
            return false;
        }
    }

    /**
     * Enviar evento de digitação
     */
    sendTypingEvent(isTyping) {
        if (!this.isConnected || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
            return;
        }

        try {
            const payload = {
                type: 'typing',
                is_typing: isTyping
            };

            this.socket.send(JSON.stringify(payload));
        } catch (error) {
            console.error('❌ Erro ao enviar evento de digitação:', error);
        }
    }

    /**
     * Enviar evento de visto
     */
    sendSeenEvent() {
        if (!this.isConnected || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
            return;
        }

        try {
            const payload = {
                type: 'seen',
                timestamp: new Date().toISOString()
            };

            this.socket.send(JSON.stringify(payload));
        } catch (error) {
            console.error('❌ Erro ao enviar evento de visto:', error);
        }
    }

    /**
     * Processar mensagens recebidas
     */
    handleMessage(data) {
        switch (data.type) {
            case 'connection_established':
                console.log('✅ Conexão estabelecida:', data.message);
                this.onConnectionEstablished();
                break;
                
            case 'message':
                console.log('📨 Nova mensagem recebida:', data);
                this.onMessageReceived(data);
                break;
                
            case 'typing':
                console.log('⌨️ Evento de digitação:', data);
                this.onTypingEvent(data);
                break;
                
            case 'seen':
                console.log('👁️ Evento de visto:', data);
                this.onSeenEvent(data);
                break;
                
            default:
                console.warn('⚠️ Tipo de mensagem desconhecido:', data.type);
        }
    }

    /**
     * Gerenciar digitação
     */
    handleTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.sendTypingEvent(true);
        }

        // Limpar timeout anterior
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }

        // Parar digitação após 2 segundos de inatividade
        this.typingTimeout = setTimeout(() => {
            this.stopTyping();
        }, 2000);
    }

    /**
     * Parar indicador de digitação
     */
    stopTyping() {
        if (this.isTyping) {
            this.isTyping = false;
            this.sendTypingEvent(false);
        }

        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
            this.typingTimeout = null;
        }
    }

    /**
     * Tratar erros de conexão
     */
    handleConnectionError(error) {
        console.error('❌ Erro de conexão:', error);
        this.isConnected = false;
        this.onConnectionError(error);
    }

    // ===== CALLBACKS (para serem sobrescritos pela interface) =====

    onConnectionEstablished() {
        console.log('🔗 Conexão estabelecida - callback padrão');
    }

    onMessageReceived(data) {
        console.log('📨 Mensagem recebida - callback padrão:', data);
    }

    onTypingEvent(data) {
        console.log('⌨️ Digitação - callback padrão:', data);
    }

    onSeenEvent(data) {
        console.log('👁️ Visto - callback padrão:', data);
    }

    onConnectionError(error) {
        console.error('❌ Erro de conexão - callback padrão:', error);
    }

    onConnectionFailed() {
        console.error('❌ Falha na conexão - callback padrão');
    }

    // ===== MÉTODOS UTILITÁRIOS =====

    isConnectedTo(targetUsername) {
        return this.isConnected && this.targetUser === targetUsername;
    }

    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            targetUser: this.targetUser,
            reconnectAttempts: this.reconnectAttempts,
            socketState: this.socket ? this.socket.readyState : null
        };
    }
}

// Instância global do chat dedicado
window.dedicatedChat = new DedicatedChat();

console.log('✅ Sistema de Chat Dedicado carregado');




