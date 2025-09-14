from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(user_logged_in)
def marcar_online(sender, user, request, **kwargs):
    perfil, _ = Profile.objects.get_or_create(user=user)
    perfil.online = True
    perfil.save()


@receiver(user_logged_out)
def marcar_offline(sender, user, request, **kwargs):
    perfil, _ = Profile.objects.get_or_create(user=user)
    perfil.online = False
    perfil.save()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
