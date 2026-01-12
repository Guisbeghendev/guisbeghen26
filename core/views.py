from django.shortcuts import render
from django.db.models import Count
from repositorio.models import Galeria, Categoria, Midia, ConfiguracaoHome
from galerias.utils import gerar_url_assinada_s3
from galerias.models import Curtida
from django.utils import timezone
from datetime import timedelta


def index(request):
    # Ajustado para gerar URLs assinadas das capas das galerias
    galerias_qs = Galeria.objects.filter(
        acesso_publico=True,
        status='publicada'
    ).select_related('capa', 'categoria').order_by('-data_evento', '-id')[:3]

    ultimas_publicas = []
    for g in galerias_qs:
        url_capa = None
        if g.capa:
            # Tenta thumbnail, se não existir usa arquivo_processado
            path = g.capa.thumbnail.name if g.capa.thumbnail else g.capa.arquivo_processado.name
            url_capa = gerar_url_assinada_s3(path)

        ultimas_publicas.append({
            'instancia': g,
            'url_capa': url_capa
        })

    categorias_carrossel = []
    categorias_com_galerias_pub = Categoria.objects.filter(
        galerias__status='publicada',
        galerias__acesso_publico=True
    ).distinct()

    for cat in categorias_com_galerias_pub:
        ultima_galeria_pub = Galeria.objects.filter(
            categoria=cat,
            status='publicada',
            acesso_publico=True
        ).order_by('-data_evento').first()

        if ultima_galeria_pub and ultima_galeria_pub.capa:
            path = ultima_galeria_pub.capa.arquivo_processado.name if ultima_galeria_pub.capa.arquivo_processado else ultima_galeria_pub.capa.thumbnail.name
            url_img = gerar_url_assinada_s3(path)

            categorias_carrossel.append({
                'nome': cat.nome,
                'slug': cat.slug,
                'url_imagem': url_img
            })

    hero_config = ConfiguracaoHome.objects.first()
    hero_url = None
    hero_arte_url = None

    if hero_config:
        if hero_config.hero_imagem:
            hero_url = gerar_url_assinada_s3(hero_config.hero_imagem.name)
        if hero_config.hero_arte_sobreposta:
            hero_arte_url = gerar_url_assinada_s3(hero_config.hero_arte_sobreposta.name)

    total_uploads = Midia.objects.filter(status_processamento='disponivel').count()
    total_galerias = Galeria.objects.filter(status='publicada').count()
    total_curtidas = Curtida.objects.count()

    seis_meses_atras = timezone.now() - timedelta(days=180)
    uploads_recentes = Midia.objects.filter(criado_em__gte=seis_meses_atras).count()
    media_mensal = round(uploads_recentes / 6) if uploads_recentes > 0 else 0

    stats = {
        'uploads': total_uploads,
        'galerias': total_galerias,
        'curtidas': total_curtidas,
        'media': media_mensal
    }

    return render(request, 'core/home.html', {
        'ultimas_publicas': ultimas_publicas,
        'categorias_carrossel': categorias_carrossel,
        'hero_url': hero_url,
        'hero_arte_url': hero_arte_url,
        'hero_config': hero_config,
        'stats': stats
    })