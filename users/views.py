from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm
from mensagens.models import SalaChat, MensagemChat, VisualizacaoMensagem
from suporte.models import TopicoSuporte, MensagemSuporte
from repositorio.models import Galeria


def register_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso! Você foi vinculado ao grupo Free.")
            return redirect('users:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('users:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def dashboard_view(request):
    user = request.user
    tem_mensagens_novas = False
    tem_suporte_novo = False

    # Captura o termo de busca
    search_query = request.GET.get('search', '').strip()

    # --- Lógica do Chat Mensagens ---
    salas = SalaChat.objects.filter(grupo__in=user.grupos_audiencia.all())
    for sala in salas:
        visu, created = VisualizacaoMensagem.objects.get_or_create(
            usuario=user,
            sala=sala
        )
        if MensagemChat.objects.filter(
                sala=sala,
                timestamp__gt=visu.ultima_visualizacao
        ).exclude(remetente=user).exists():
            tem_mensagens_novas = True
            break

    # --- Lógica do Suporte ---
    if user.is_staff or user.profile.is_admin_projeto:
        tem_suporte_novo = MensagemSuporte.objects.filter(
            topico__status__in=['aberto', 'atendimento', 'aguardando'],
            lida=False
        ).exclude(remetente__is_staff=True).exists()
    else:
        tem_suporte_novo = MensagemSuporte.objects.filter(
            topico__usuario=user,
            topico__status__in=['aberto', 'atendimento', 'aguardando'],
            lida=False,
            remetente__is_staff=True
        ).exists()

    # --- Lógica de Galerias (Com Busca e Segurança de Grupo) ---
    galerias_queryset = Galeria.objects.filter(
        status='publicada',
        grupos_audiencia__in=user.grupos_audiencia.all()
    ).distinct()

    if search_query:
        ultimas_galerias = galerias_queryset.filter(titulo__icontains=search_query).order_by('-atualizado_em')
    else:
        ultimas_galerias = galerias_queryset.order_by('-atualizado_em')[:3]

    return render(request, 'users/dashboard.html', {
        'tem_mensagens_novas': tem_mensagens_novas,
        'tem_suporte_novo': tem_suporte_novo,
        'ultimas_galerias': ultimas_galerias,
        'search_query': search_query
    })


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'users/edit_profile.html', {'form': form})