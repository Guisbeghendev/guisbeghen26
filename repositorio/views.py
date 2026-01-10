from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Galeria, Midia, MarcaDagua, Categoria
from .forms import GaleriaForm, MarcaDaguaForm
from .tasks import processar_imagem_task


def is_fotografo(user):
    return user.is_authenticated and (
            getattr(user.profile, 'is_fotografo', False) or
            user.is_staff or
            getattr(user.profile, 'is_admin_projeto', False)
    )


@login_required
@user_passes_test(is_fotografo)
def painel_gestao_view(request):
    galerias = Galeria.objects.filter(fotografo=request.user)
    return render(request, 'repositorio/painel_gestao.html', {'galerias': galerias})


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
        # Captura metadados do lote enviados pelo frontend (Dropzone/XHR)
        total = int(request.POST.get('total_files', 1))
        indice = int(request.POST.get('current_index', 1))
        opacidade = int(request.POST.get('opacidade', 50))

        midia = Midia.objects.create(
            galeria=galeria,
            arquivo_original=arquivo,
            status_processamento='pendente'
        )

        # Disparo manual para controle de progresso (substitui o signal)
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

    midias = galeria.midias.all().order_by('-criado_em')
    return render(request, 'repositorio/upload_midia.html', {
        'galeria': galeria,
        'midias': midias
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
    marcas = MarcaDagua.objects.filter(fotografo=request.user)
    return render(request, 'repositorio/lista_marcas.html', {'marcas': marcas})


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