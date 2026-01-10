from django.contrib import admin
from .models import Curtida

@admin.register(Curtida)
class CurtidaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'foto', 'criado_em')
    list_filter = ('criado_em',)
    search_fields = ('usuario__username', 'foto__id', 'foto__galeria__titulo')
    readonly_fields = ('criado_em',)