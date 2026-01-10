from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.files.storage import storages
import uuid

# Define o storage do S3 para as mídias do repositório
repositorio_storage = storages['repositorio_s3']

class MarcaDagua(models.Model):
    fotografo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marcas_dagua'
    )
    nome = models.CharField(max_length=100)
    # Marca d'água fica no S3 pois é usada no processamento do repositório
    imagem = models.ImageField(upload_to='repositorio/watermarks/', storage=repositorio_storage)
    opacidade = models.PositiveIntegerField(default=50)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.fotografo.username}"

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    # Categorias do sistema ficam no storage local (default)
    imagem_base = models.ImageField(upload_to='repositorio/categorias/')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Galeria(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('publicada', 'Publicada'),
        ('arquivada', 'Arquivada'),
    ]

    acesso_publico = models.BooleanField(default=False)
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    fotografo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='galerias_criadas'
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='galerias')
    grupos_audiencia = models.ManyToManyField('users.GrupoAudiencia', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    marca_dagua_padrao = models.ForeignKey(
        MarcaDagua, on_delete=models.SET_NULL, null=True, blank=True
    )
    capa = models.ForeignKey(
        'Midia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='galeria_capa'
    )
    data_evento = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_evento']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.titulo)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

class Midia(models.Model):
    STATUS_PROC = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('disponivel', 'Disponível'),
        ('erro', 'Erro'),
    ]

    galeria = models.ForeignKey(Galeria, on_delete=models.CASCADE, related_name='midias')
    # Mídias utilizam o storage do S3 conforme solicitado
    arquivo_original = models.FileField(upload_to='repositorio/originais/%Y/%m/%d/', storage=repositorio_storage)
    arquivo_processado = models.FileField(upload_to='repositorio/processadas/%Y/%m/%d/', null=True, blank=True, storage=repositorio_storage)
    thumbnail = models.ImageField(upload_to='repositorio/thumbs/%Y/%m/%d/', null=True, blank=True, storage=repositorio_storage)
    status_processamento = models.CharField(max_length=20, choices=STATUS_PROC, default='pendente', db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Midia {self.id} - Galeria: {self.galeria.titulo}"