import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Midia, MarcaDagua
from galerias.utils import gerar_url_assinada_s3


@shared_task(bind=True)
def processar_imagem_task(self, midia_id, marca_dagua_id=None, total_arquivos=1, indice_atual=1, opacidade=50, rotacao=0):
    try:
        midia = Midia.objects.select_related('galeria').get(id=midia_id)
        midia.status_processamento = 'processando'
        midia.save(update_fields=['status_processamento'])

        if rotacao != 0:
            with midia.arquivo_original.open('rb') as f_orig:
                with Image.open(f_orig) as img_to_rotate:
                    img_rotated = img_to_rotate.rotate(rotacao, expand=True)
                    buffer_rot = BytesIO()
                    img_rotated.save(buffer_rot, format='JPEG', quality=95)
                    filename = os.path.basename(midia.arquivo_original.name)
                    midia.arquivo_original.save(filename, ContentFile(buffer_rot.getvalue()), save=False)

        with midia.arquivo_original.open('rb') as f_orig:
            with Image.open(f_orig) as img_original:
                if img_original.mode != 'RGB':
                    img_original = img_original.convert('RGB')

                img_proc = img_original.copy()

                if marca_dagua_id:
                    try:
                        marca_obj = MarcaDagua.objects.get(id=marca_dagua_id)
                        with marca_obj.imagem.open('rb') as f_marca:
                            with Image.open(f_marca) as watermark:
                                if watermark.mode != 'RGBA':
                                    watermark = watermark.convert('RGBA')

                                alpha = watermark.getchannel('A')
                                novo_alpha = alpha.point(lambda i: i * (float(opacidade) / 100))
                                watermark.putalpha(novo_alpha)

                                w_width, w_height = watermark.size
                                base_width = img_proc.size[0]
                                new_w_width = int(base_width * 0.2)
                                new_w_height = int((new_w_width * w_height) / w_width)
                                watermark = watermark.resize((new_w_width, new_w_height), Image.Resampling.LANCZOS)

                                pos_x = img_proc.size[0] - watermark.size[0] - 20
                                pos_y = img_proc.size[1] - watermark.size[1] - 20
                                img_proc.paste(watermark, (pos_x, pos_y), watermark)
                    except:
                        pass

                buffer_proc = BytesIO()
                img_proc.save(buffer_proc, format='JPEG', quality=85, optimize=True)
                filename = os.path.basename(midia.arquivo_original.name)

                midia.arquivo_processado.save(f"proc_{filename}", ContentFile(buffer_proc.getvalue()), save=False)

                img_thumb = img_original.copy()
                img_thumb.thumbnail((400, 400), Image.Resampling.LANCZOS)
                buffer_thumb = BytesIO()
                img_thumb.save(buffer_thumb, format='JPEG', quality=75)
                midia.thumbnail.save(f"thumb_{filename}", ContentFile(buffer_thumb.getvalue()), save=False)

                midia.status_processamento = 'disponivel'
                midia.save(update_fields=['status_processamento', 'arquivo_processado', 'thumbnail', 'arquivo_original'])

                midia.refresh_from_db()

                channel_layer = get_channel_layer()
                group_name = f"galeria_{midia.galeria.slug}"
                percentual = int((indice_atual / total_arquivos) * 100)

                path_thumb = midia.thumbnail.name if midia.thumbnail else midia.arquivo_processado.name
                url_thumb_assinada = gerar_url_assinada_s3(path_thumb) if path_thumb else ""

                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "notificar_progresso",
                        "midia_id": midia.id,
                        "progresso": percentual,
                        "concluidas": indice_atual,
                        "total": total_arquivos,
                        "status": "concluido" if indice_atual == total_arquivos else "processando",
                        "url_thumb": url_thumb_assinada
                    }
                )

    except Exception as e:
        if 'midia' in locals():
            midia.status_processamento = 'erro'
            midia.save(update_fields=['status_processamento'])
        raise e