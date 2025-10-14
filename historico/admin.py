from django.contrib import admin
from django.utils.html import format_html

from .models import Historico


@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = [
        "data_hora",
        "usuario",
        "acao_icon",
        "tipo_objeto_icon",
        "objeto_nome",
        "descricao_resumida",
        "ip_address",
    ]
    list_filter = ["acao", "tipo_objeto", "data_hora", "usuario"]
    search_fields = [
        "objeto_nome",
        "descricao",
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
    ]
    readonly_fields = [
        "usuario",
        "acao",
        "tipo_objeto",
        "objeto_id",
        "objeto_nome",
        "descricao",
        "detalhes_antes",
        "detalhes_depois",
        "data_hora",
        "ip_address",
        "user_agent",
        "criado_em",
        "atualizado_em",
    ]
    date_hierarchy = "data_hora"
    ordering = ["-data_hora"]
    list_per_page = 50

    fieldsets = (
        (
            "Informações Básicas",
            {"fields": ("usuario", "acao", "tipo_objeto", "data_hora")},
        ),
        ("Objeto Afetado", {"fields": ("objeto_id", "objeto_nome", "descricao")}),
        (
            "Detalhes da Ação",
            {"fields": ("detalhes_antes", "detalhes_depois"), "classes": ("collapse",)},
        ),
        (
            "Metadados",
            {"fields": ("ip_address", "user_agent"), "classes": ("collapse",)},
        ),
        (
            "Auditoria",
            {"fields": ("criado_em", "atualizado_em"), "classes": ("collapse",)},
        ),
    )

    def acao_icon(self, obj):
        """Exibe ícone da ação"""
        return format_html(
            '<span class="badge bg-{}"><i class="bi {}"></i> {}</span>',
            obj.acao_color,
            obj.acao_icon,
            obj.get_acao_display(),
        )

    acao_icon.short_description = "Ação"

    def tipo_objeto_icon(self, obj):
        """Exibe ícone do tipo de objeto"""
        return format_html(
            '<i class="bi {}"></i> {}',
            obj.tipo_objeto_icon,
            obj.get_tipo_objeto_display(),
        )

    tipo_objeto_icon.short_description = "Tipo"

    def descricao_resumida(self, obj):
        """Exibe descrição resumida"""
        if len(obj.descricao) > 50:
            return obj.descricao[:50] + "..."
        return obj.descricao

    descricao_resumida.short_description = "Descrição"

    def has_add_permission(self, request):
        """Impede criação manual de registros de histórico"""
        return False

    def has_change_permission(self, request, obj=None):
        """Impede edição de registros de histórico"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Permite exclusão apenas para superusuários"""
        return request.user.is_superuser
