import uuid
from django.db import models
from django.conf import settings


class TopicoSuporte(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('atendimento', 'Em Atendimento'),
        ('aguardando', 'Aguardando Usuário'),
        ('fechado', 'Fechado'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chamados_suporte'
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    assunto = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media')

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-atualizado_em']
        verbose_name = "Tópico de Suporte"
        verbose_name_plural = "Tópicos de Suporte"

    def __str__(self):
        return f"{self.assunto} - {self.usuario.username} ({self.status})"


class MensagemSuporte(models.Model):
    topico = models.ForeignKey(
        TopicoSuporte,
        on_delete=models.CASCADE,
        related_name='mensagens'
    )
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    conteudo = models.TextField()
    arquivo_anexo = models.FileField(
        upload_to='suporte/anexos/%Y/%m/%d/',
        null=True,
        blank=True
    )
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = "Mensagem de Suporte"
        verbose_name_plural = "Mensagens de Suporte"

    def __str__(self):
        return f"Mensagem de {self.remetente.username} em {self.topico.assunto}"