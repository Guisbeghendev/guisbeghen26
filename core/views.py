from django.shortcuts import render
from repositorio.models import Galeria, Categoria
from galerias.utils import gerar_url_assinada_s3


def index(request):
    # --- BLOCO EXISTENTE (INTOCADO) ---
    ultimas_publicas = Galeria.objects.filter(
        acesso_publico=True,
        status='publicada'
    ).order_by('-data_evento', '-id')[:3]
    # ---------------------------------

    # ACRESCENTANDO: Busca de categorias com galerias públicas
    categorias_carrossel = []
    categorias_com_galerias_pub = Categoria.objects.filter(
        galerias__status='publicada',
        galerias__acesso_publico=True
    ).distinct()

    for cat in categorias_com_galerias_pub:
        # Pega a galeria pública mais recente desta categoria para a capa do carrossel
        ultima_galeria_pub = Galeria.objects.filter(
            categoria=cat,
            status='publicada',
            acesso_publico=True
        ).order_by('-data_evento').first()

        if ultima_galeria_pub and ultima_galeria_pub.capa:
            # Define qual arquivo usar (processado ou thumbnail)
            path = ultima_galeria_pub.capa.arquivo_processado.name if ultima_galeria_pub.capa.arquivo_processado else ultima_galeria_pub.capa.thumbnail.name
            url_img = gerar_url_assinada_s3(path)

            categorias_carrossel.append({
                'nome': cat.nome,
                'slug': cat.slug,
                'url_imagem': url_img
            })

    return render(request, 'core/home.html', {
        'ultimas_publicas': ultimas_publicas,
        'categorias_carrossel': categorias_carrossel
    })