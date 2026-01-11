from django.shortcuts import render
from repositorio.models import Galeria


def index(request):
    # Busca as 3 últimas galerias marcadas como acesso público e status publicada
    ultimas_publicas = Galeria.objects.filter(
        acesso_publico=True,
        status='publicada'
    ).order_by('-data_evento', '-id')[:3]

    return render(request, 'core/home.html', {
        'ultimas_publicas': ultimas_publicas
    })