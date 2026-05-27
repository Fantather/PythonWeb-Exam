from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """Удаление файла при удалении инстанса пользователя."""
    if instance.avatar and instance.avatar.name:
        instance.avatar.storage.delete(instance.avatar.name)

@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    """Удаление старого файла при замене аватара."""
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if old_instance.avatar and old_instance.avatar.name != instance.avatar.name:
        old_instance.avatar.storage.delete(old_instance.avatar.name)