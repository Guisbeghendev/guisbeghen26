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
            'midia_id': event.get('midia_id'),
            'progresso': event.get('progresso'),
            'concluidas': event.get('concluidas'),
            'total': event.get('total'),
            'status': event.get('status'),
            'url_thumb': event.get('url_thumb')
        }))