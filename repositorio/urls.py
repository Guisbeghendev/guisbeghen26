from django.urls import path
from . import views

app_name = 'repositorio'

urlpatterns = [
    # Painel de Gestão do Fotógrafo
    path('painel/', views.painel_gestao_view, name='painel_gestao'),

    # Gestão de Galerias
    path('galeria/nova/', views.criar_galeria_view, name='criar_galeria'),
    path('galeria/<slug:slug>/editar/', views.editar_galeria_view, name='editar_galeria'),
    path('galeria/<slug:slug>/excluir/', views.excluir_galeria_view, name='excluir_galeria'),
    path('galeria/<slug:slug>/status/<str:novo_status>/', views.alterar_status_galeria_view, name='alterar_status_galeria'),

    # Upload e Mídias
    path('galeria/<slug:slug>/upload/', views.upload_midia_view, name='upload_midia'),
    path('midia/<int:pk>/definir-capa/', views.definir_capa_view, name='definir_capa'),
    path('midia/<int:pk>/excluir/', views.excluir_midia_view, name='excluir_midia'),

    # Marcas D'água
    path('marcas/', views.lista_marcas_view, name='lista_marcas'),
    path('marcas/nova/', views.nova_marca_view, name='nova_marca'),
]