from django.urls import path
from . import views

app_name = 'suporte'

urlpatterns = [
    path('', views.lista_chamados, name='lista_chamados'),
    path('novo/', views.novo_chamado, name='novo_chamado'),
    path('chamado/<uuid:uuid>/', views.detalhe_chamado, name='detalhe_chamado'),
]