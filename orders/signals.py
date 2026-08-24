from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order
from .whatsapp import send_text, customer_status

@receiver(pre_save, sender=Order)
def remember_old_status(sender, instance, **kwargs):
    instance._old_status = None
    if instance.pk:
        try:
            instance._old_status = sender.objects.only("status").get(pk=instance.pk).status
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def send_status_update(sender, instance, created, **kwargs):
    if created:
        return
    if getattr(instance, "_old_status", None) and instance._old_status != instance.status:
        if instance.consent_whatsapp:
            send_text(instance.customer_whatsapp, customer_status(instance))
