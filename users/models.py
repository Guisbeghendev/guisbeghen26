from django.contrib.auth.models import AbstractUser
from django.db import models

class GrupoAudiencia(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Grupo de Audiência"
        verbose_name_plural = "Grupos de Audiência"

class User(AbstractUser):
    email = models.EmailField(unique=True)
    grupos_audiencia = models.ManyToManyField(
        GrupoAudiencia,
        blank=True,
        related_name="usuarios_audiencia"
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Flags de Negócio
    is_fotografo = models.BooleanField(default=False)
    is_admin_projeto = models.BooleanField(default=False)

    # Dados de Perfil
    nome = models.CharField(max_length=100, blank=True)
    sobrenome = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='profiles/', null=True, blank=True)
    biografia = models.TextField(blank=True)
    contato = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    origem_contato = models.TextField(blank=True)

    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"