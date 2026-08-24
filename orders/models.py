import secrets
from django.db import models
from catalog.models import Decoration

def generate_code():
    return "DEC-" + secrets.token_hex(3).upper()

class Order(models.Model):
    STATUS_CHOICES = [
        ("RECEBIDO", "Recebido"),
        ("ANALISE", "Em análise"),
        ("CONFIRMADO", "Confirmado"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    ]
    code = models.CharField(max_length=20, unique=True, default=generate_code, editable=False)
    customer_name = models.CharField(max_length=120)
    customer_whatsapp = models.CharField(max_length=30)
    event_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    consent_whatsapp = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RECEBIDO")
    total_reference = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    owner_notified = models.BooleanField(default=False)
    customer_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    decoration = models.ForeignKey(Decoration, on_delete=models.PROTECT)
    title_snapshot = models.CharField(max_length=180)
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.order.code} - {self.title_snapshot}"
