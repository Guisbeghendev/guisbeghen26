import os
from celery import Celery

# Define o módulo de configurações padrão do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('guisbeghen')

# Lê as configurações do settings.py com o prefixo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente tarefas em todos os apps registrados
app.autodiscover_tasks()