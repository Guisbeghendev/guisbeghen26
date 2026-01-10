from django.db import models
from django.conf import settings
from repositorio.models import Midia

class Curtida(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='curtidas'
    )
    foto = models.ForeignKey(
        Midia,
        on_delete=models.CASCADE,
        related_name='curtidas_recebidas'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'foto'], name='unique_curtida_usuario_foto')
        ]
        verbose_name = 'Curtida'
        verbose_name_plural = 'Curtidas'

    def __str__(self):
        return f"{self.usuario.username} curtiu {self.foto.id}"