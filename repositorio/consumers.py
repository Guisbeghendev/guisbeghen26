import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GaleriaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f"galeria_{self.slug}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def notificar_progresso(self, event):
        await self.send(text_data=json.dumps({
            'progresso': event['progresso'],
            'concluidas': event['concluidas'],
            'total': event['total'],
            'status': event['status']
        }))