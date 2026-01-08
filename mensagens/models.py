from django.db import models
from django.conf import settings
from users.models import GrupoAudiencia

class SalaChat(models.Model):
    grupo = models.OneToOneField(GrupoAudiencia, on_delete=models.CASCADE, related_name='sala_chat')
    nome_exibicao = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.nome_exibicao}"

class MensagemChat(models.Model):
    sala = models.ForeignKey(SalaChat, on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conteudo = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.remetente.username}: {self.conteudo[:20]}"

class VisualizacaoMensagem(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sala = models.ForeignKey(SalaChat, on_delete=models.CASCADE)
    ultima_visualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'sala')