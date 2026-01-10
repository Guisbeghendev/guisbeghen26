from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('historia/', include('historia.urls')),
    path('contato/', include('contato.urls')),
    path('perfil/', include('perfil.urls')),
    path('mensagens/', include('mensagens.urls')),
    path('suporte/', include('suporte.urls', namespace='suporte')),
    path('repositorio/', include('repositorio.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Suporte ao armazenamento híbrido (Local para ativos, S3 para Repositório)
    if settings.STORAGES['default']['BACKEND'] == 'django.core.files.storage.FileSystemStorage':
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)