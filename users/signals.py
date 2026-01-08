from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile, GrupoAudiencia


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Cria a instância de Profile vinculada ao novo ID
        Profile.objects.create(user=instance)

        # Associa o novo CustomUser ao GrupoAudiencia com nome 'Free'
        grupo_free, _ = GrupoAudiencia.objects.get_or_create(nome='Free')
        instance.grupos_audiencia.add(grupo_free)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()