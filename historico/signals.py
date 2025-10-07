from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .utils import registrar_login, registrar_logout


@receiver(user_logged_in)
def usuario_fez_login(sender, request, user, **kwargs):
    """Signal disparado quando um usuário faz login"""
    try:
        registrar_login(user, request)
    except Exception as e:
        # Não queremos que um erro no histórico impeça o login
        print(f"Erro ao registrar login no histórico: {e}")


@receiver(user_logged_out)
def usuario_fez_logout(sender, request, user, **kwargs):
    """Signal disparado quando um usuário faz logout"""
    try:
        if user:  # user pode ser None em alguns casos
            registrar_logout(user, request)
    except Exception as e:
        # Não queremos que um erro no histórico impeça o logout
        print(f"Erro ao registrar logout no histórico: {e}")
