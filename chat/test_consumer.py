import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TestChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket conectando...")
        await self.accept()
        print("WebSocket conectado!")

    async def disconnect(self, close_code):
        print(f"WebSocket desconectado com código: {close_code}")

    async def receive(self, text_data):
        print(f"Mensagem recebida: {text_data}")
        try:
            data = json.loads(text_data)
            message = data.get("message", "")

            # Ecoar a mensagem de volta
            await self.send(
                text_data=json.dumps(
                    {
                        "message": f"Echo: {message}",
                        "sender": "test_bot",
                        "timestamp": data.get("timestamp", ""),
                    }
                )
            )
            print(f"Mensagem enviada de volta: Echo: {message}")
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            await self.send(text_data=json.dumps({"error": str(e)}))
