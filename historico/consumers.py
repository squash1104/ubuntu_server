import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class HistoricoConsumer(AsyncWebsocketConsumer):
    """
    Consumer para atualização em tempo real do histórico.
    Todos os usuários autenticados se conectam a um canal único 'historico_updates'.
    """

    async def connect(self):
        """Quando um cliente conecta ao WebSocket"""
        # Verifica se o usuário está autenticado
        if (
            self.scope["user"] == AnonymousUser()
            or not self.scope["user"].is_authenticated
        ):
            await self.close()
            return

        # Nome do grupo/canal para broadcasts
        self.room_group_name = "historico_updates"

        # Adiciona este canal ao grupo
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(f"Histórico WebSocket conectado: {self.scope['user'].username}")

    async def disconnect(self, close_code):
        """Quando um cliente desconecta do WebSocket"""
        # Remove este canal do grupo
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(
            f"Histórico WebSocket desconectado: {self.scope['user'].username if self.scope.get('user') else 'Unknown'}"
        )

    async def receive(self, text_data):
        """
        Recebe mensagens do cliente (não usado neste caso,
        pois apenas enviamos do servidor para o cliente)
        """
        pass

    async def historico_novo(self, event):
        """
        Recebe evento 'historico.novo' do channel layer e envia para o WebSocket
        """
        # Envia a mensagem para o WebSocket
        await self.send(
            text_data=json.dumps(
                {"type": "novo_registro", "historico": event["historico"]}
            )
        )
