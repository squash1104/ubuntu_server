from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os


class Profile(models.Model):
    """Perfil do usuário com informações adicionais"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='Foto')
    recovery_email = models.EmailField(blank=True, null=True, verbose_name='Email de Recuperação')
    full_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Nome Completo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

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
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar mantendo proporção
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Salvar a imagem redimensionada
                img.save(self.photo.path, 'JPEG', quality=85)
            except Exception as e:
                print(f"Erro ao redimensionar foto: {e}")

    @property
    def display_name(self):
        """Retorna o nome completo ou username como fallback"""
        return self.full_name or self.user.get_full_name() or self.user.username
