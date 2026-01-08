from django.urls import path
from . import views

app_name = 'mensagens'

urlpatterns = [
    path('', views.lista_salas, name='lista_salas'),
    path('<int:sala_id>/', views.detalhe_sala, name='detalhe_sala'),
]