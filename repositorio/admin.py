from django.contrib import admin
from .models import MarcaDagua, Categoria, Galeria, Midia

@admin.register(MarcaDagua)
class MarcaDaguaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fotografo', 'opacidade', 'criado_em')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fotografo', 'categoria', 'status', 'data_evento', 'marca_dagua_padrao')
    list_filter = ('status', 'categoria', 'acesso_publico')
    search_fields = ('titulo',)
    filter_horizontal = ('grupos_audiencia',)

@admin.register(Midia)
class MidiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'galeria', 'status_processamento', 'criado_em')
    list_filter = ('status_processamento',)