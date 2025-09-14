from typing import ClassVar

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent", on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User, related_name="received", on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["timestamp"]

    def __str__(self):
        status = "[Lido]" if self.read else "[Enviado]"
        return f"{self.sender.username} -> {self.recipient.username}: {self.content[:50]}... {status}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    online = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile de: {self.user.username} (online={self.online})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


@property
def full_name(self):
    return f"{self.first_name} {self.last_name}".strip() or self.username


User.add_to_class("full_name", full_name)
