"""
Hooks para integrar o histórico com o Django Admin.
User admin com campo para forçar troca de senha no próximo login.
"""

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from user_profiles.models import Profile

from .utils import registrar_criacao_usuario

# Desregistrar o UserAdmin padrão
admin.site.unregister(User)


FORCE_PASSWORD_FIELD = forms.BooleanField(
    required=False,
    initial=True,
    label="Forçar troca de senha no próximo login",
    help_text="Se ativo, o usuário precisará redefinir a senha ao fazer login",
    widget=forms.CheckboxInput(attrs={"class": "vCheckboxLabel"}),
)


class CustomUserCreationForm(UserCreationForm):
    """Formulário de criação com checkbox para forçar troca de senha"""

    force_password_change = FORCE_PASSWORD_FIELD

    class Meta(UserCreationForm.Meta):
        fields = ("username",)


class CustomUserChangeForm(UserChangeForm):
    """Formulário de edição com checkbox para forçar troca de senha"""

    force_password_change = FORCE_PASSWORD_FIELD
    password = UserChangeForm.base_fields["password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Carrega o valor atual do profile no checkbox
        profile = getattr(self.instance, "profile", None)
        self.fields["force_password_change"].initial = (
            profile.force_password_change if profile else False
        )


@admin.register(User)
class UserAdminWithHistory(BaseUserAdmin):
    """
    UserAdmin customizado que registra a criação de usuários no histórico
    e permite forçar troca de senha no próximo login.
    """

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    add_fieldsets = (
        (None, {"fields": ("username", "password1", "password2")}),
        (
            "Opções",
            {"fields": ("force_password_change",), "classes": ("wide",)},
        ),
    )
    fieldsets = [  # noqa: RUF012
        *BaseUserAdmin.fieldsets,
        (
            "Segurança",
            {"fields": ("force_password_change",), "classes": ("wide",)},
        ),
    ]

    def save_model(self, request, obj, form, change):
        """
        Sobrescreve save_model para registrar a criação no histórico
        e salvar a flag force_password_change
        """
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        # Garante que a flag seja salva no Profile
        profile, _ = Profile.objects.get_or_create(user=obj)
        profile.force_password_change = form.cleaned_data.get(
            "force_password_change", False
        )
        profile.save(update_fields=["force_password_change"])

        if is_new:
            registrar_criacao_usuario(
                usuario_criado=obj, criado_por=request.user, request=request
            )
