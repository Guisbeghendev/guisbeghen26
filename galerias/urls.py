from django.urls import path
from . import views

app_name = 'galerias'

urlpatterns = [
    # Nível 1: Seletor de Categorias
    path('', views.categorias_list, name='index'),

    # Nível 2: Seletor de Grupos
    path('categoria/<slug:slug>/', views.grupos_por_categoria, name='grupos_por_categoria'),

    # Nível 3: Listagem Final de Galerias (Corrigido para bater com o template)
    path('publicas/<slug:categoria_slug>/<int:grupo_id>/', views.galerias_publicas, name='galerias_publicas'),
    path('exclusivas/<slug:categoria_slug>/<int:grupo_id>/', views.galerias_exclusivas, name='galerias_exclusivas'),

    # Nível Final: O Acervo de Fotos
    path('galerias/<slug:slug>/', views.detalhe_galeria, name='detalhe_galeria'),

    # Ações
    path('curtir/<int:midia_id>/', views.toggle_curtida, name='toggle_curtida'),
]