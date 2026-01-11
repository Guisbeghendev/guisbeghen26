from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from repositorio.models import Categoria, Galeria, Midia
from .models import Curtida
from .utils import gerar_url_assinada_s3, usuario_tem_acesso_galeria


def categorias_list(request):
    trilha = request.GET.get('trilha', 'publica')

    if trilha == 'exclusiva':
        if request.user.is_authenticated:
            user_profile = getattr(request.user, 'profile', None)
            is_staff = request.user.is_superuser or \
                       (user_profile and user_profile.is_fotografo) or \
                       (user_profile and user_profile.is_admin_projeto)

            if is_staff:
                categorias = Categoria.objects.filter(
                    galerias__status='publicada'
                ).distinct()
            else:
                categorias = Categoria.objects.filter(
                    galerias__status='publicada',
                    galerias__grupos_audiencia__in=request.user.grupos_audiencia.all()
                ).distinct()
        else:
            categorias = Categoria.objects.none()
    else:
        categorias = Categoria.objects.filter(
            galerias__status='publicada',
            galerias__acesso_publico=True
        ).distinct()

    return render(request, 'galerias/index.html', {
        'categorias': categorias,
        'trilha': trilha
    })


def grupos_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    trilha = request.GET.get('trilha', 'publica')
    from users.models import GrupoAudiencia

    if trilha == 'exclusiva' and request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)
        is_staff = request.user.is_superuser or \
                   (user_profile and user_profile.is_fotografo) or \
                   (user_profile and user_profile.is_admin_projeto)

        if is_staff:
            grupos = GrupoAudiencia.objects.filter(
                galeria__categoria=categoria,
                galeria__status='publicada'
            ).distinct()
        else:
            grupos = GrupoAudiencia.objects.filter(
                galeria__categoria=categoria,
                galeria__status='publicada',
                id__in=request.user.grupos_audiencia.values_list('id', flat=True)
            ).distinct()
    else:
        grupos = GrupoAudiencia.objects.filter(
            galeria__categoria=categoria,
            galeria__status='publicada',
            galeria__acesso_publico=True
        ).distinct()

    return render(request, 'galerias/grupos_list.html', {
        'categoria': categoria,
        'grupos': grupos,
        'trilha': trilha
    })


def galerias_publicas(request, categoria_slug=None, grupo_id=None):
    galerias_qs = Galeria.objects.filter(status='publicada', acesso_publico=True)

    if categoria_slug:
        galerias_qs = galerias_qs.filter(categoria__slug=categoria_slug)
    if grupo_id:
        galerias_qs = galerias_qs.filter(grupos_audiencia__id=grupo_id)

    # Resolve o QuerySet antes de iterar para garantir unicidade e carregar a capa
    galerias = galerias_qs.select_related('capa').distinct()

    for galeria in galerias:
        if galeria.capa and galeria.capa.arquivo_processado:
            galeria.url_capa = gerar_url_assinada_s3(galeria.capa.arquivo_processado.name)
        elif galeria.capa and galeria.capa.thumbnail:
            galeria.url_capa = gerar_url_assinada_s3(galeria.capa.thumbnail.name)
        else:
            galeria.url_capa = None

    return render(request, 'galerias/publicas.html', {
        'galerias': galerias,
        'trilha': 'publica'
    })


@login_required
def galerias_exclusivas(request, categoria_slug=None, grupo_id=None):
    user_profile = getattr(request.user, 'profile', None)
    is_staff = request.user.is_superuser or \
               (user_profile and user_profile.is_fotografo) or \
               (user_profile and user_profile.is_admin_projeto)

    if is_staff:
        galerias_qs = Galeria.objects.filter(status='publicada')
    else:
        galerias_qs = Galeria.objects.filter(
            status='publicada',
            grupos_audiencia__in=request.user.grupos_audiencia.all()
        )

    if categoria_slug:
        galerias_qs = galerias_qs.filter(categoria__slug=categoria_slug)
    if grupo_id:
        galerias_qs = galerias_qs.filter(grupos_audiencia__id=grupo_id)

    # Resolve o QuerySet antes de iterar para garantir unicidade e carregar a capa
    galerias = galerias_qs.select_related('capa').distinct()

    for galeria in galerias:
        if galeria.capa and galeria.capa.arquivo_processado:
            galeria.url_capa = gerar_url_assinada_s3(galeria.capa.arquivo_processado.name)
        elif galeria.capa and galeria.capa.thumbnail:
            galeria.url_capa = gerar_url_assinada_s3(galeria.capa.thumbnail.name)
        else:
            galeria.url_capa = None

    return render(request, 'galerias/exclusivas.html', {
        'galerias': galerias,
        'trilha': 'exclusiva'
    })


def detalhe_galeria(request, slug):
    galeria = get_object_or_404(Galeria, slug=slug, status='publicada')
    trilha = request.GET.get('trilha', 'publica')

    if not usuario_tem_acesso_galeria(request.user, galeria):
        return render(request, 'core/403.html', status=403)

    midias = Midia.objects.filter(galeria=galeria, status_processamento='disponivel')

    for midia in midias:
        if midia.arquivo_processado:
            midia.url_exibicao = gerar_url_assinada_s3(midia.arquivo_processado.name)
        if midia.thumbnail:
            midia.url_thumb = gerar_url_assinada_s3(midia.thumbnail.name)

        midia.usuario_curtiu = False
        if request.user.is_authenticated:
            midia.usuario_curtiu = Curtida.objects.filter(usuario=request.user, foto=midia).exists()

    total_curtidas = Curtida.objects.filter(foto__galeria=galeria).count()

    return render(request, 'galerias/detalhe.html', {
        'galeria': galeria,
        'midias': midias,
        'total_curtidas': total_curtidas,
        'trilha': trilha
    })


@login_required
def toggle_curtida(request, midia_id):
    if request.method == 'POST':
        midia = get_object_or_404(Midia, id=midia_id)
        curtida, created = Curtida.objects.get_or_create(usuario=request.user, foto=midia)

        if not created:
            curtida.delete()
            status = 'removido'
        else:
            status = 'adicionado'

        total_foto = midia.curtidas_rece_count() if hasattr(midia, 'curtidas_recebidas') else 0
        return JsonResponse({'status': status, 'total_foto': total_foto})

    return JsonResponse({'error': 'Invalid request'}, status=400)