import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import TopicoSuporte, MensagemSuporte


class SuporteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.uuid = self.scope['url_route']['kwargs']['uuid']
        self.room_group_name = f'suporte_{self.uuid}'

        if await self.user_tem_acesso(self.uuid):
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        tipo = data.get('type')

        if tipo == 'chat_message':
            mensagem = data['mensagem']
            await self.salvar_mensagem(self.uuid, mensagem)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'suporte_message',
                    'mensagem': mensagem,
                    'user': self.scope['user'].username
                }
            )

        elif tipo == 'change_status':
            novo_status = data.get('status')
            if await self.is_staff():
                await self.atualizar_status(self.uuid, novo_status)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'status_update',
                        'status': novo_status
                    }
                )

    async def suporte_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def status_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def user_tem_acesso(self, uuid):
        user = self.scope['user']
        if not user.is_authenticated: return False
        try:
            chamado = TopicoSuporte.objects.get(uuid=uuid)
            return user.is_staff or user.profile.is_admin_projeto or chamado.usuario == user
        except TopicoSuporte.DoesNotExist:
            return False

    @database_sync_to_async
    def is_staff(self):
        user = self.scope['user']
        return user.is_staff or user.profile.is_admin_projeto

    @database_sync_to_async
    def salvar_mensagem(self, uuid, conteudo):
        chamado = TopicoSuporte.objects.get(uuid=uuid)
        # Salva a mensagem (lida=False por padrão)
        MensagemSuporte.objects.create(
            topico=chamado,
            remetente=self.scope['user'],
            conteudo=conteudo
        )
        # Atualiza o campo atualizado_em para subir na lista
        chamado.save()

    @database_sync_to_async
    def atualizar_status(self, uuid, novo_status):
        TopicoSuporte.objects.filter(uuid=uuid).update(status=novo_status)