import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Message

User = get_user_model()


@login_required
def messages_page(request):
    return render(request, "chat/messages_page.html")


@login_required
def test_websocket(request):
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste WebSocket</title>
    </head>
    <body>
        <h1>Teste WebSocket</h1>
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Digite sua mensagem">
        <button onclick="sendMessage()">Enviar</button>
        
        <script>
            const socket = new WebSocket('ws://localhost:8000/ws/chat/test/');
            
            socket.onopen = function(e) {
                console.log('Conectado');
            };
            
            socket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                document.getElementById('messages').innerHTML += '<p>' + data.message + '</p>';
            };
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                socket.send(JSON.stringify({
                    'message': input.value
                }));
                input.value = '';
            }
        </script>
    </body>
    </html>
    """
    return HttpResponse(content, content_type="text/html")


@login_required
def test_websocket_simple(request):
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste WebSocket Simples</title>
    </head>
    <body>
        <h1>Teste WebSocket Simples</h1>
        <div id="status">Desconectado</div>
        <div id="messages"></div>
        
        <script>
            const socket = new WebSocket('ws://localhost:8000/ws/notify/');
            
            socket.onopen = function(e) {
                document.getElementById('status').textContent = 'Conectado';
            };
            
            socket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                document.getElementById('messages').innerHTML += '<p>' + JSON.stringify(data) + '</p>';
            };
            
            socket.onclose = function(e) {
                document.getElementById('status').textContent = 'Desconectado';
            };
        </script>
    </body>
    </html>
    """
    return HttpResponse(content, content_type="text/html")


@login_required
def debug_chat(request):
    return render(request, "chat/debug.html")


@login_required
def simple_chat_test(request):
    return render(request, "chat/simple_test.html")


@login_required
def chat_complete_test(request):
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat Completo - Teste</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .chat-container { display: flex; height: 500px; border: 1px solid #ccc; }
            .contacts { width: 200px; border-right: 1px solid #ccc; padding: 10px; }
            .chat { flex: 1; display: flex; flex-direction: column; }
            .messages { flex: 1; padding: 10px; overflow-y: auto; }
            .input { padding: 10px; border-top: 1px solid #ccc; }
            .contact { padding: 5px; cursor: pointer; border-bottom: 1px solid #eee; }
            .contact:hover { background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>Chat Completo - Teste</h1>
        <div class="chat-container">
            <div class="contacts" id="contacts">
                <h3>Contatos</h3>
                <div id="contacts-list"></div>
            </div>
            <div class="chat">
                <div class="messages" id="messages"></div>
                <div class="input">
                    <input type="text" id="messageInput" placeholder="Digite sua mensagem">
                    <button onclick="sendMessage()">Enviar</button>
                </div>
            </div>
        </div>
        
        <script>
            let currentUser = null;
            let socket = null;
            
            // Carregar contatos
            fetch('/chat/contatos_status/')
                .then(response => response.json())
                .then(contacts => {
                    const contactsList = document.getElementById('contacts-list');
                    contacts.forEach(contact => {
                        const div = document.createElement('div');
                        div.className = 'contact';
                        div.textContent = contact.full_name;
                        div.onclick = () => startChat(contact);
                        contactsList.appendChild(div);
                    });
                });
            
            function startChat(contact) {
                currentUser = contact;
                document.getElementById('messages').innerHTML = '';
                
                // Conectar WebSocket
                if (socket) socket.close();
                socket = new WebSocket(`ws://localhost:8000/ws/chat/${contact.username}/`);
                
                socket.onopen = function() {
                    console.log('Conectado ao chat com', contact.username);
                };
                
                socket.onmessage = function(e) {
                    const data = JSON.parse(e.data);
                    addMessage(data.message, data.sender, false);
                };
                
                // Carregar histórico
                fetch(`/chat/historico/${contact.username}/`)
                    .then(response => response.json())
                    .then(messages => {
                        messages.forEach(msg => {
                            addMessage(msg.message, msg.sender, msg.is_own);
                        });
                    });
            }
            
            function addMessage(message, sender, isOwn) {
                const messages = document.getElementById('messages');
                const div = document.createElement('div');
                div.textContent = `${sender}: ${message}`;
                div.style.textAlign = isOwn ? 'right' : 'left';
                div.style.color = isOwn ? 'blue' : 'black';
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function sendMessage() {
                if (!socket || !currentUser) return;
                
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                socket.send(JSON.stringify({
                    'message': message,
                    'timestamp': new Date().toISOString()
                }));
                
                addMessage(message, 'Você', true);
                input.value = '';
            }
            
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HttpResponse(content, content_type="text/html")


@login_required
def fetch_messages(request, username):
    try:
        mensagens = Message.objects.filter(
            sender__username__in=[request.user.username, username],
            recipient__username__in=[request.user.username, username],
        ).order_by("timestamp")

        # Marcar mensagens recebidas como lidas
        mensagens_nao_lidas = mensagens.filter(recipient=request.user, read=False)
        mensagens_nao_lidas.update(read=True, read_at=timezone.now())

        data = [
            {
                "id": msg.id,
                "sender": msg.sender.username,  # Usar username para consistência
                "message": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "is_own": msg.sender == request.user,
                "is_read": msg.read,
                "read_at": msg.read_at.isoformat() if msg.read_at else None,
            }
            for msg in mensagens
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def lista_contatos(request):
    contatos = User.objects.exclude(id=request.user.id)
    return JsonResponse(
        [{"id": u.id, "username": u.username} for u in contatos], safe=False
    )


@login_required
def contatos_status(request):
    custom_user = get_user_model()
    contatos = custom_user.objects.exclude(id=request.user.id).select_related("profile")

    contatos_data = []
    for c in contatos:
        # Buscar a última mensagem entre o usuário atual e este contato
        last_message = (
            Message.objects.filter(
                sender__username__in=[request.user.username, c.username],
                recipient__username__in=[request.user.username, c.username],
            )
            .order_by("-timestamp")
            .first()
        )

        # Contar mensagens não lidas
        unread_count = Message.objects.filter(
            sender=c, recipient=request.user, read=False
        ).count()

        contato_data = {
            "username": c.username,
            "full_name": c.get_full_name() or c.username,
            "online": c.profile.online if hasattr(c, "profile") else False,
            "last_message": last_message.content if last_message else None,
            "last_message_time": (
                last_message.timestamp.isoformat() if last_message else None
            ),
            "unread_count": unread_count,
        }
        contatos_data.append(contato_data)

    return JsonResponse(contatos_data, safe=False)


@login_required
def mark_message_read(request):
    """Endpoint para marcar mensagem como lida"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message_id = data.get("message_id")

            if not message_id:
                return JsonResponse({"error": "message_id é obrigatório"}, status=400)

            # Marcar mensagem como lida
            message = Message.objects.filter(
                id=message_id, recipient=request.user
            ).first()

            if not message:
                return JsonResponse({"error": "Mensagem não encontrada"}, status=404)

            if not message.read:
                message.read = True
                message.read_at = timezone.now()
                message.save()

                print(
                    f"✅ Mensagem {message_id} marcada como lida por {request.user.username}"
                )

            return JsonResponse(
                {
                    "status": "success",
                    "message_id": message_id,
                    "read_at": message.read_at.isoformat() if message.read_at else None,
                }
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except Exception as e:
            print(f"❌ Erro ao marcar mensagem como lida: {e}")
            return JsonResponse({"error": "Erro interno do servidor"}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)
