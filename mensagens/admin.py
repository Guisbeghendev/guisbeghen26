import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import SalaChat, MensagemChat


@admin.register(SalaChat)
class SalaChatAdmin(admin.ModelAdmin):
    list_display = ('nome_exibicao', 'grupo', 'criado_em')
    search_fields = ('nome_exibicao', 'grupo__nome')
    readonly_fields = ('criado_em',)


@admin.register(MensagemChat)
class MensagemChatAdmin(admin.ModelAdmin):
    list_display = ('sala', 'timestamp', 'remetente', 'conteudo_curto')
    date_hierarchy = 'timestamp'
    list_filter = (
        'sala',
        ('timestamp', admin.DateFieldListFilter),
        'remetente',
    )
    search_fields = ('conteudo', 'remetente__username')
    readonly_fields = ('timestamp',)
    ordering = ('sala', '-timestamp')
    actions = ['exportar_para_csv']

    def conteudo_curto(self, obj):
        return obj.conteudo[:50]

    conteudo_curto.short_description = 'Conteúdo'

    @admin.action(description="Exportar mensagens selecionadas para CSV")
    def exportar_para_csv(self, request, queryset):
        # Define charset como utf-8-sig para compatibilidade com Excel Windows
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="relatorio_mensagens.csv"'

        # Usa delimitador ';' para abrir corretamente em colunas no Excel BR
        writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Sala', 'Data/Hora', 'Remetente', 'Mensagem'])

        for msg in queryset:
            # Remove quebras de linha para não quebrar a estrutura do CSV
            conteudo_limpo = msg.conteudo.replace('\r', '').replace('\n', ' ')

            writer.writerow([
                msg.sala.nome_exibicao,
                msg.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                msg.remetente.username,
                conteudo_limpo
            ])

        return response