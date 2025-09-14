import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import Message  # ✅ importe o Profile (e Message)


class GlobalChatConsumer(AsyncWebsocketConsumer):
    """Consumer global para gerenciar todos os usuários online"""

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.username = self.user.username
        self.group_name = f"global_{self.username}"

        # Adicionar ao grupo global
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Adicionar ao grupo de usuários online
        await self.channel_layer.group_add("online_users", self.channel_name)

        # Marcar usuário como online
        await self.set_user_online(True)

        # Notificar outros usuários que este usuário está online
        await self.channel_layer.group_send(
            "online_users",
            {
                "type": "user_status_change",
                "username": self.username,
                "online": True,
                "full_name": await self.get_user_full_name(),
            },
        )

        await self.accept()
        print(f"Global chat conectado: {self.username}")

    async def disconnect(self, close_code):
        # Marcar usuário como offline
        await self.set_user_online(False)

        # Notificar outros usuários que este usuário está offline
        await self.channel_layer.group_send(
            "online_users",
            {
                "type": "user_status_change",
                "username": self.username,
                "online": False,
                "full_name": await self.get_user_full_name(),
            },
        )

        # Remover dos grupos
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard("online_users", self.channel_name)

        print(f"Global chat desconectado: {self.username}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "get_online_users":
            # Enviar lista de usuários online
            online_users = await self.get_online_users()
            await self.send(
                text_data=json.dumps(
                    {"type": "online_users_list", "users": online_users}
                )
            )

        elif message_type == "typing_start":
            # Notificar que usuário está digitando
            recipient = data.get("recipient")
            if recipient:
                await self.channel_layer.group_send(
                    f"global_{recipient}",
                    {
                        "type": "typing_status",
                        "username": self.username,
                        "status": "typing_start",
                    },
                )

        elif message_type == "typing_stop":
            # Notificar que usuário parou de digitar
            recipient = data.get("recipient")
            if recipient:
                await self.channel_layer.group_send(
                    f"global_{recipient}",
                    {
                        "type": "typing_status",
                        "username": self.username,
                        "status": "typing_stop",
                    },
                )

    async def user_status_change(self, event):
        """Enviar mudança de status para o cliente"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_status_change",
                    "username": event["username"],
                    "online": event["online"],
                    "full_name": event["full_name"],
                }
            )
        )

    async def typing_status(self, event):
        """Enviar status de digitação para o cliente"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing_status",
                    "username": event["username"],
                    "status": event["status"],
                }
            )
        )

    @database_sync_to_async
    def get_user_full_name(self):
        """Obter nome completo do usuário"""
        return self.user.get_full_name() or self.user.username

    @database_sync_to_async
    def get_online_users(self):
        """Obter lista de usuários online"""
        from .models import Profile

        User = get_user_model()
        online_profiles = Profile.objects.filter(online=True).select_related("user")
        return [
            {
                "username": profile.user.username,
                "full_name": profile.user.get_full_name() or profile.user.username,
                "online": True,
            }
            for profile in online_profiles
            if profile.user != self.user
        ]

    @database_sync_to_async
    def set_user_online(self, online_status):
        """Atualiza o status online do usuário"""
        from .models import Profile

        profile, created = Profile.objects.get_or_create(user=self.user)
        profile.online = online_status
        profile.save()
        print(f"Status online atualizado: {self.username} = {online_status}")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.current_user = self.scope["user"]

        # Criar nome do grupo baseado nos dois usuários (ordenado alfabeticamente)
        if self.current_user.is_authenticated:
            users = sorted([self.current_user.username, self.username])
            self.room_group_name = f"chat_{'_'.join(users)}"
        else:
            self.room_group_name = f"chat_{self.username}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Marcar usuário como online
        await self.set_user_online(True)

        await self.accept()
        print(
            f"WebSocket conectado para {self.current_user.username} -> {self.username}"
        )

    async def disconnect(self, close_code):
        # Marcar usuário como offline
        await self.set_user_online(False)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(
            f"WebSocket desconectado para {self.current_user.username} -> {self.username}"
        )

    async def receive(self, text_data):
        print(f"Mensagem recebida no WebSocket. Grupo: {self.room_group_name}")
        data = json.loads(text_data)

        # Verificar se é mensagem de digitação
        msg_type = data.get("type")
        if msg_type in ["typing_start", "typing_stop"]:
            print(f"Enviando {msg_type} para grupo {self.room_group_name}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status",
                    "message_type": msg_type,
                    "sender": self.scope["user"].username,
                },
            )
            return

        # Mensagem normal
        message = data.get("message")
        timestamp = data.get("timestamp")
        if message:
            print(
                f"Salvando mensagem e enviando para grupo {self.room_group_name}: {message}"
            )
            await self.save_message(message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.scope["user"].username,
                    "timestamp": timestamp,
                },
            )

            # Também envia notificação para o destinatário via canal global de notify
            try:
                recipient_username = self.username
                await self.channel_layer.group_send(
                    f"notify_{recipient_username}",
                    {
                        "type": "notify_message",
                        "message": message,
                        "sender": self.scope["user"].username,
                        "timestamp": timestamp,
                    },
                )
            except Exception as e:
                print(f"Falha ao enviar notify para {self.username}: {e}")

    async def chat_message(self, event):
        # Enviar a mensagem para todos no grupo (tanto remetente quanto destinatário)
        print(
            f"Enviando mensagem via WebSocket: {event['message']} de {event['sender']}"
        )
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "timestamp": event.get("timestamp"),
                }
            )
        )

    async def typing_status(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": event["message_type"],
                    "sender": event["sender"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, message):
        user_model = get_user_model()
        try:
            # Obter o usuário real a partir do username
            sender = user_model.objects.get(username=self.scope["user"].username)
            recipient = user_model.objects.get(username=self.username)

            Message.objects.create(sender=sender, recipient=recipient, content=message)
            print(
                f"Mensagem salva: {sender.username} -> {recipient.username}: {message}"
            )
        except user_model.DoesNotExist as e:
            print(f"Erro: Usuário não encontrado - {e}")

    @database_sync_to_async
    def set_user_online(self, online_status):
        """Atualiza o status online do usuário atual"""
        from .models import Profile

        user_lazy = self.scope["user"]
        if user_lazy.is_authenticated:
            # Obter o usuário real a partir do username
            user_model = get_user_model()
            try:
                user = user_model.objects.get(username=user_lazy.username)
                profile, created = Profile.objects.get_or_create(user=user)
                profile.online = online_status
                profile.save()
                print(f"Status online atualizado: {user.username} = {online_status}")
            except user_model.DoesNotExist:
                print(
                    f"Erro: Usuário {user_lazy.username} não encontrado para atualizar status"
                )

    # ===== Helpers que tocam ORM (devem ser sync-to-async) =====

    # @database_sync_to_async
    # def mark_online(self, flag: bool):
    # Cria/atualiza Profile sem levantar DoesNotExist
    #   Profile.objects.update_or_create(user=self.user, defaults={"online": flag})


# @database_sync_to_async
# def save_message(self, sender_username, recipient_username, content):
#   from django.contrib.auth.models import User
#  sender = User.objects.get(username=sender_username)
# recipient = User.objects.get(username=sender_username)
# Message.objects.create(sender=sender, recipient=recipient, content=content)


class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return
        self.user = user
        self.group_name = f"notify_{user.username}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"Notify conectado: {user.username}")

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"Notify desconectado: {getattr(self, 'user', None)}")

    # Evento enviado do servidor
    async def notify_message(self, event):
        payload = {
            "type": "new_message",
            "message": event.get("message"),
            "sender": event.get("sender"),
            "timestamp": event.get("timestamp"),
        }
        await self.send(text_data=json.dumps(payload))
