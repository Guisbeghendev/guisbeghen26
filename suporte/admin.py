from django.contrib import admin
from .models import TopicoSuporte, MensagemSuporte


class MensagemSuporteInline(admin.TabularInline):
    model = MensagemSuporte
    extra = 1
    fields = ('remetente', 'conteudo', 'arquivo_anexo', 'criado_em')
    readonly_fields = ('criado_em',)


@admin.register(TopicoSuporte)
class TopicoSuporteAdmin(admin.ModelAdmin):
    list_display = ('assunto', 'usuario', 'status', 'prioridade', 'criado_em', 'atualizado_em')
    list_filter = ('status', 'prioridade', 'criado_em')
    search_fields = ('assunto', 'usuario__username', 'uuid')
    readonly_fields = ('uuid', 'criado_em', 'atualizado_em')
    inlines = [MensagemSuporteInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('uuid', 'usuario', 'assunto')
        }),
        ('Controle de Fluxo', {
            'fields': ('status', 'prioridade')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
        }),
    )


@admin.register(MensagemSuporte)
class MensagemSuporteAdmin(admin.ModelAdmin):
    list_display = ('topico', 'remetente', 'criado_em')
    list_filter = ('criado_em', 'remetente')
    search_fields = ('conteudo', 'topico__assunto')