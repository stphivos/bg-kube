from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def on_user_logged_in(instance=None, *_, **__):
    Profile.objects.get_or_create(user=instance)
