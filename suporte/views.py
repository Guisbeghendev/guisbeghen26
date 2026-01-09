from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import TopicoSuporte, MensagemSuporte


@login_required
def lista_chamados(request):
    if request.user.is_staff or request.user.profile.is_admin_projeto:
        chamados = TopicoSuporte.objects.all()
    else:
        chamados = TopicoSuporte.objects.filter(usuario=request.user)

    return render(request, 'suporte/lista_chamados.html', {
        'chamados': chamados
    })


@login_required
def novo_chamado(request):
    if request.method == 'POST':
        assunto = request.POST.get('assunto')
        prioridade = request.POST.get('prioridade', 'media')
        mensagem_inicial = request.POST.get('mensagem')

        if assunto and mensagem_inicial:
            topico = TopicoSuporte.objects.create(
                usuario=request.user,
                assunto=assunto,
                prioridade=prioridade
            )
            MensagemSuporte.objects.create(
                topico=topico,
                remetente=request.user,
                conteudo=mensagem_inicial
            )
            return redirect('suporte:detalhe_chamado', uuid=topico.uuid)

    return render(request, 'suporte/novo_chamado.html')


@login_required
def detalhe_chamado(request, uuid):
    chamado = get_object_or_404(TopicoSuporte, uuid=uuid)

    is_admin = request.user.is_staff or request.user.profile.is_admin_projeto
    if not is_admin and chamado.usuario != request.user:
        return HttpResponseForbidden("Você não tem permissão para visualizar este chamado.")

    # Marcar mensagens como lidas
    MensagemSuporte.objects.filter(
        topico=chamado,
        lida=False
    ).exclude(remetente=request.user).update(lida=True)

    mensagens = chamado.mensagens.all()

    return render(request, 'suporte/detalhe_chamado.html', {
        'chamado': chamado,
        'mensagens': mensagens,
        'is_admin': is_admin
    })