from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import SalaChat, MensagemChat, VisualizacaoMensagem


@login_required
def lista_salas(request):
    """
    Lista apenas as salas de chat vinculadas aos grupos
    de audiência que o usuário pertence.
    """
    user_grupos = request.user.grupos_audiencia.all()
    salas = SalaChat.objects.filter(grupo__in=user_grupos)

    return render(request, 'mensagens/lista_salas.html', {
        'salas': salas
    })


@login_required
def detalhe_sala(request, sala_id):
    """
    Exibe a interface do chat e o histórico de mensagens.
    Valida se o usuário tem permissão para acessar a sala.
    """
    sala = get_object_or_404(SalaChat, id=sala_id)

    # Validação de segurança: o usuário pertence ao grupo da sala?
    if not request.user.grupos_audiencia.filter(id=sala.grupo.id).exists():
        return HttpResponseForbidden("Você não tem permissão para acessar esta sala de chat.")

    # Marca como visualizado ao entrar na sala
    VisualizacaoMensagem.objects.update_or_create(
        usuario=request.user,
        sala=sala,
        defaults={'ultima_visualizacao': timezone.now()}
    )

    # Busca as últimas 50 mensagens para o histórico inicial
    mensagens = sala.mensagens.all().order_by('timestamp')[:50]

    return render(request, 'mensagens/detalhe_sala.html', {
        'sala': sala,
        'mensagens': mensagens
    })