from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import GrupoAudiencia
from .models import SalaChat

@receiver(post_save, sender=GrupoAudiencia)
def criar_sala_chat(sender, instance, created, **kwargs):
    if created:
        SalaChat.objects.create(
            grupo=instance,
            nome_exibicao=instance.nome
        )