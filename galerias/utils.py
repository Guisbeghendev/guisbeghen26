import boto3
from django.conf import settings
from botocore.exceptions import ClientError

def gerar_url_assinada_s3(file_path, expiration=3600):
    """
    Gera uma URL temporária assinada para acesso privado ao S3.
    """
    if not file_path:
        return None

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=boto3.session.Config(signature_version='s3v4')
    )

    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_path
            },
            ExpiresIn=expiration
        )
        return url
    except ClientError:
        return None


def usuario_tem_acesso_galeria(user, galeria):
    """
    Verifica se o usuário tem permissão para visualizar a galeria.
    """
    # 1. Acesso Público
    if galeria.acesso_publico:
        return True

    # 2. Usuário não logado não acessa conteúdo restrito
    if not user.is_authenticated:
        return False

    # 3. Staff, Fotógrafos e Admins do Projeto têm acesso total
    if user.is_superuser or user.profile.is_fotografo or user.profile.is_admin_projeto:
        return True

    # 4. Verifica interseção entre grupos do usuário e da galeria
    return galeria.grupos_audiencia.filter(id__in=user.grupos_audiencia.all()).exists()