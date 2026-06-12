import typing

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from PIL import Image


class Profile(models.Model):
    """Perfil do usuário com informações adicionais"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(
        upload_to="profiles/", blank=True, null=True, verbose_name="Foto"
    )
    recovery_email = models.EmailField(
        blank=True, null=True, verbose_name="Email de Recuperação"
    )
    full_name = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Nome Completo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    force_password_change = models.BooleanField(
        default=False,
        verbose_name="Forçar troca de senha no próximo login",
        help_text="Se ativo, redirecionado para redefinir a senha ao fazer login",
    )

    acesso_aniversariantes = models.BooleanField(
        default=False, verbose_name="Acesso a Aniversariantes"
    )
    acesso_mensagens = models.BooleanField(
        default=False, verbose_name="Acesso a Mensagens"
    )
    acesso_historico = models.BooleanField(
        default=False, verbose_name="Acesso a Histórico"
    )

    class Meta:
        db_table = "user_profiles"
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Redimensionar foto se existir
        if self.photo:
            self.resize_photo()

    def resize_photo(self):
        """Redimensiona a foto para 200x200 pixels"""
        if self.photo:
            try:
                img = Image.open(self.photo.path)

                # Converter para RGB se necessário
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Redimensionar mantendo proporção
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)

                # Salvar a imagem redimensionada
                img.save(self.photo.path, "JPEG", quality=85)
            except Exception as e:
                print(f"Erro ao redimensionar foto: {e}")

    @property
    def display_name(self):
        """Retorna o nome completo ou username como fallback"""
        return self.full_name or self.user.get_full_name() or self.user.username


class UserSession(models.Model):
    """Rastreamento de sessões dos usuários para estatísticas de tempo/sessões."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=64, db_index=True)
    start_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    end_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes: typing.ClassVar = [
            models.Index(fields=["user", "start_at"]),
            models.Index(fields=["user", "end_at"]),
        ]

    @property
    def duration_seconds(self) -> int:
        end = self.end_at or timezone.now()
        return max(0, int((end - self.start_at).total_seconds()))
