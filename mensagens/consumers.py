import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SalaChat, MensagemChat

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sala_id = self.scope['url_route']['kwargs']['sala_id']
        self.room_group_name = f'chat_{self.sala_id}'

        if await self.user_tem_acesso(self.sala_id):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            # Notifica entrada e atualiza lista
            await self.atualizar_usuarios()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Notifica saída e atualiza lista
        await self.atualizar_usuarios()

    async def receive(self, text_data):
        data = json.loads(text_data)
        mensagem = data['mensagem']

        await self.salvar_mensagem(self.sala_id, mensagem)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'mensagem': mensagem,
                'user': self.scope['user'].username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_list(self, event):
        await self.send(text_data=json.dumps(event))

    async def atualizar_usuarios(self):
        usuarios = await self.get_usuarios_sala(self.sala_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list',
                'usuarios': usuarios
            }
        )

    @database_sync_to_async
    def get_usuarios_sala(self, sala_id):
        try:
            sala = SalaChat.objects.get(id=sala_id)
            # Ajustado para usar o related_name 'usuarios_audiencia' do seu modelo User
            return list(sala.grupo.usuarios_audiencia.values_list('username', flat=True))
        except SalaChat.DoesNotExist:
            return []

    @database_sync_to_async
    def user_tem_acesso(self, sala_id):
        user = self.scope['user']
        if not user.is_authenticated: return False
        try:
            sala = SalaChat.objects.get(id=sala_id)
            return user.grupos_audiencia.filter(id=sala.grupo.id).exists()
        except SalaChat.DoesNotExist:
            return False

    @database_sync_to_async
    def salvar_mensagem(self, sala_id, conteudo):
        sala = SalaChat.objects.get(id=sala_id)
        MensagemChat.objects.create(
            sala=sala,
            remetente=self.scope['user'],
            conteudo=conteudo
        )