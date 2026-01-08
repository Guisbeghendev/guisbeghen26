from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, GrupoAudiencia


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'
    fields = (
        'nome',
        'sobrenome',
        'foto',
        'is_fotografo',
        'is_admin_projeto',
        'biografia',
        'whatsapp',
        'contato',
        'cidade',
        'estado',
        'data_nascimento',
        'origem_contato'
    )


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    filter_horizontal = ('grupos_audiencia', 'groups', 'user_permissions')
    list_display = ('username', 'email', 'get_nome_completo', 'is_staff', 'get_grupos_audiencia')

    fieldsets = UserAdmin.fieldsets + (
        ('Segmentação', {'fields': ('grupos_audiencia',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Segmentação', {'fields': ('grupos_audiencia',)}),
    )

    def get_grupos_audiencia(self, obj):
        return ", ".join([g.nome for g in obj.grupos_audiencia.all()])
    get_grupos_audiencia.short_description = 'Grupos de Audiência'

    def get_nome_completo(self, obj):
        return f"{obj.profile.nome} {obj.profile.sobrenome}".strip() or "Não preenchido"
    get_nome_completo.short_description = 'Nome Completo (Perfil)'


admin.site.register(User, CustomUserAdmin)
admin.site.register(GrupoAudiencia)