from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Profile, UserSession


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    if hasattr(instance, "profile"):
        instance.profile.save()
    else:
        # Se por algum motivo o perfil não existir, criar um
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Session)
def track_session_activity(sender, instance: Session, **kwargs):
    """Atualiza last_seen da sessão do usuário se conseguirmos recuperar o user_id."""
    try:
        data = instance.get_decoded()
        user_id = data.get("_auth_user_id")
        if not user_id:
            return
        sess, _ = UserSession.objects.get_or_create(
            user_id=int(user_id), session_key=instance.session_key
        )
        sess.last_seen_at = timezone.now()
        # Não encerramos aqui; idle será tratado por middleware/limpeza
        sess.save(update_fields=["last_seen_at"])
    except Exception:
        return
