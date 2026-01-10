from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Midia

@receiver(post_save, sender=Midia)
def disparar_processamento_midia(sender, instance, created, **kwargs):
    """
    Sinal mantido para logs ou integridade, mas o disparo do Celery
    foi movido para a View para controle da barra de progresso.
    """
    pass