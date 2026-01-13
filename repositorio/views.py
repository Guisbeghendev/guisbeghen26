from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from .models import Galeria, Midia, MarcaDagua, Categoria, ConfiguracaoHome
from .forms import GaleriaForm, MarcaDaguaForm, ConfiguracaoHomeForm
from .tasks import processar_imagem_task
from galerias.utils import gerar_url_assinada_s3


def is_fotografo(user):
    return user.is_authenticated and (
            getattr(user.profile, 'is_fotografo', False) or
            user.is_staff or
            getattr(user.profile, 'is_admin_projeto', False)
    )


@login_required
@user_passes_test(is_fotografo)
def painel_gestao_view(request):
    galerias_qs = Galeria.objects.filter(fotografo=request.user).select_related('capa', 'categoria')

    galerias_com_capa = []
    for g in galerias_qs:
        url_capa = None
        if g.capa:
            path = g.capa.thumbnail.name if g.capa.thumbnail else g.capa.arquivo_processado.name
            url_capa = gerar_url_assinada_s3(path)

        galerias_com_capa.append({
            'instancia': g,
            'url_capa': url_capa
        })

    return render(request, 'repositorio/painel_gestao.html', {'galerias': galerias_com_capa})


@login_required
@user_passes_test(is_fotografo)
def criar_galeria_view(request):
    if request.method == 'POST':
        form = GaleriaForm(request.POST, user=request.user)
        if form.is_valid():
            galeria = form.save(commit=False)
            galeria.fotografo = request.user
            galeria.save()
            form.save_m2m()
            messages.success(request, "Galeria criada! Agora você pode enviar as fotos.")
            return redirect('repositorio:upload_midia', slug=galeria.slug)
    else:
        form = GaleriaForm(user=request.user)
    return render(request, 'repositorio/form_galeria.html', {'form': form, 'titulo': 'Nova Galeria'})


@csrf_exempt
@login_required
@user_passes_test(is_fotografo)
def upload_midia_view(request, slug):
    galeria = get_object_or_404(Galeria, slug=slug, fotografo=request.user)

    if request.method == 'POST' and request.FILES.get('file'):
        arquivo = request.FILES.get('file')
        total = int(request.POST.get('total_files', 1))
        indice = int(request.POST.get('current_index', 1))
        opacidade = int(request.POST.get('opacidade', 50))

        midia = Midia.objects.create(
            galeria=galeria,
            arquivo_original=arquivo,
            status_processamento='pendente'
        )

        marca_id = galeria.marca_dagua_padrao.id if galeria.marca_dagua_padrao else None
        processar_imagem_task.delay(
            midia_id=midia.id,
            marca_dagua_id=marca_id,
            total_arquivos=total,
            indice_atual=indice,
            opacidade=opacidade
        )

        return JsonResponse({
            'status': 'success',
            'midia_id': midia.id,
            'filename': arquivo.name
        })

    midias_qs = galeria.midias.all().order_by('-criado_em')
    midias_com_url = []
    for m in midias_qs:
        url_thumb = None
        if m.thumbnail:
            url_thumb = gerar_url_assinada_s3(m.thumbnail.name)
        elif m.arquivo_processado:
            url_thumb = gerar_url_assinada_s3(m.arquivo_processado.name)

        midias_com_url.append({
            'instancia': m,
            'url_thumb': url_thumb
        })

    return render(request, 'repositorio/upload_midia.html', {
        'galeria': galeria,
        'midias': midias_com_url
    })


@login_required
@user_passes_test(is_fotografo)
def editar_galeria_view(request, slug):
    galeria = get_object_or_404(Galeria, slug=slug, fotografo=request.user)
    if request.method == 'POST':
        form = GaleriaForm(request.POST, instance=galeria, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Galeria atualizada com sucesso.")
            return redirect('repositorio:painel_gestao')
    else:
        form = GaleriaForm(instance=galeria, user=request.user)
    return render(request, 'repositorio/form_galeria.html',
                  {'form': form, 'galeria': galeria, 'titulo': 'Editar Galeria'})


@login_required
@user_passes_test(is_fotografo)
def definir_capa_view(request, pk):
    midia = get_object_or_404(Midia, pk=pk, galeria__fotografo=request.user)
    galeria = midia.galeria
    galeria.capa = midia
    galeria.save()
    messages.success(request, "Capa da galeria definida.")
    return redirect('repositorio:upload_midia', slug=galeria.slug)


@login_required
@user_passes_test(is_fotografo)
def excluir_midia_view(request, pk):
    midia = get_object_or_404(Midia, pk=pk, galeria__fotografo=request.user)
    slug = midia.galeria.slug
    midia.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'deleted'})
    return redirect('repositorio:upload_midia', slug=slug)


@login_required
@user_passes_test(is_fotografo)
def lista_marcas_view(request):
    marcas_qs = MarcaDagua.objects.filter(fotografo=request.user)
    marcas_com_url = []
    for m in marcas_qs:
        url_assinada = None
        if m.imagem:
            # A alteração é trocar str(m.imagem) por m.imagem.name
            # O atributo .name retorna o caminho relativo exato exigido pelo S3
            url_assinada = gerar_url_assinada_s3(m.imagem.name)
        marcas_com_url.append({
            'instancia': m,
            'url_assinada': url_assinada
        })
    return render(request, 'repositorio/lista_marcas.html', {'marcas': marcas_com_url})


@login_required
@user_passes_test(is_fotografo)
def nova_marca_view(request):
    if request.method == 'POST':
        form = MarcaDaguaForm(request.POST, request.FILES)
        if form.is_valid():
            marca = form.save(commit=False)
            marca.fotografo = request.user
            marca.save()
            return redirect('repositorio:lista_marcas')
    else:
        form = MarcaDaguaForm()
    return render(request, 'repositorio/form_marca.html', {'form': form})


@login_required
@user_passes_test(is_fotografo)
def excluir_galeria_view(request, slug):
    galeria = get_object_or_404(Galeria, slug=slug, fotografo=request.user)
    galeria.delete()
    messages.success(request, "Galeria excluída permanentemente.")
    return redirect('repositorio:painel_gestao')


@login_required
@user_passes_test(is_fotografo)
def alterar_status_galeria_view(request, slug, novo_status):
    galeria = get_object_or_404(Galeria, slug=slug, fotografo=request.user)
    status_permitidos = [choice[0] for choice in Galeria.STATUS_CHOICES]
    if novo_status in status_permitidos:
        galeria.status = novo_status
        galeria.save()
        messages.success(request, f"Galeria {galeria.get_status_display()} com sucesso.")
    return redirect('repositorio:painel_gestao')


@login_required
@user_passes_test(is_fotografo)
def ranking_curtidas_view(request):
    midias_query = Midia.objects.filter(status_processamento='disponivel')
    galerias_filtro = Galeria.objects.filter(fotografo=request.user)

    if not request.user.is_superuser:
        midias_query = midias_query.filter(galeria__fotografo=request.user)

    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    galeria_id = request.GET.get('galeria_id')

    filtro_likes = Q()
    if data_inicio:
        filtro_likes &= Q(curtidas_recebidas__criado_em__date__gte=data_inicio)
    if data_fim:
        filtro_likes &= Q(curtidas_recebidas__criado_em__date__lte=data_fim)

    if galeria_id:
        midias_query = midias_query.filter(galeria_id=galeria_id)

    midias = midias_query.annotate(total_likes=Count('curtidas_recebidas', filter=filtro_likes)) \
        .filter(total_likes__gt=0) \
        .order_by('-total_likes')

    for midia in midias:
        if midia.thumbnail:
            midia.url_thumb = gerar_url_assinada_s3(midia.thumbnail.name)

    return render(request, 'repositorio/curtidas_ranking.html', {
        'midias': midias,
        'galerias_filtro': galerias_filtro
    })


@login_required
@user_passes_test(is_fotografo)
def gestao_home_view(request):
    config = ConfiguracaoHome.objects.first()
    if request.method == 'POST':
        form = ConfiguracaoHomeForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Destaque da Home atualizado!")
            return redirect('repositorio:painel_gestao')
    else:
        form = ConfiguracaoHomeForm(instance=config)

    return render(request, 'repositorio/form_home_hero.html', {'form': form})