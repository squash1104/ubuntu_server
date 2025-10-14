"""
Hooks para integrar o histórico com o Django Admin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .utils import registrar_criacao_usuario

# Desregistrar o UserAdmin padrão
admin.site.unregister(User)


@admin.register(User)
class UserAdminWithHistory(BaseUserAdmin):
    """
    UserAdmin customizado que registra a criação de usuários no histórico
    """

    def save_model(self, request, obj, form, change):
        """
        Sobrescreve save_model para registrar a criação no histórico
        """
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new:
            # Registra a criação do usuário no histórico
            registrar_criacao_usuario(
                usuario_criado=obj, criado_por=request.user, request=request
            )
