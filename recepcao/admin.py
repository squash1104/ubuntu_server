from django.contrib import admin

from .models import (
    Atendimento,
    AtendimentoAnexo,
    AtendimentoEvento,
    Attendente,
    Visitante,
)


@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "funcao", "municipio", "email")
    search_fields = ("nome", "telefone", "email", "municipio", "funcao")


class AtendimentoAnexoInline(admin.TabularInline):
    model = AtendimentoAnexo
    extra = 0


class AtendimentoEventoInline(admin.TabularInline):
    model = AtendimentoEvento
    extra = 0
    readonly_fields = ("timestamp", "usuario", "tipo", "detalhes")


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "visitante",
        "status",
        "recepcionista",
        "atendente",
        "pessoa_destino",
        "horario_chegada",
        "inicio_atendimento",
        "fim_atendimento",
    )
    list_filter = ("status", "recepcionista", "atendente")
    search_fields = ("visitante__nome", "pessoa_destino", "demanda_resumo")
    inlines = [AtendimentoAnexoInline, AtendimentoEventoInline]


@admin.register(AtendimentoAnexo)
class AtendimentoAnexoAdmin(admin.ModelAdmin):
    list_display = ("atendimento", "arquivo", "enviado_por", "criado_em")
    search_fields = ("atendimento__visitante__nome",)


@admin.register(AtendimentoEvento)
class AtendimentoEventoAdmin(admin.ModelAdmin):
    list_display = ("atendimento", "tipo", "timestamp", "usuario")
    list_filter = ("tipo",)
    search_fields = ("atendimento__visitante__nome", "detalhes")


# Register your models here.


@admin.register(Attendente)
class AttendenteAdmin(admin.ModelAdmin):
    list_display = ("nome", "criado_em")
    search_fields = ("nome",)
