from django.contrib import admin

from .models import Colaborador, TipoColaborador


@admin.register(TipoColaborador)
class TipoColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao", "ativo", "data_cadastro")
    list_filter = ("ativo", "data_cadastro")
    search_fields = ("nome", "descricao")
    ordering = ("nome",)


admin.site.register(Colaborador)
