import secrets
from django.db import models
from catalog.models import Decoration


def generate_code():
    return "DEC-" + secrets.token_hex(5).upper()


class Order(models.Model):
    STATUS_CHOICES = [
        ("RECEBIDO", "Recebido"),
        ("ANALISE", "Em análise"),
        ("CONFIRMADO", "Confirmado"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    ]
    EVENT_TYPE_CHOICES = [
        ("ANIVERSARIO", "Aniversário"),
        ("CHÁ", "Chá / Revelação / Bebê"),
        ("CASAMENTO", "Casamento / Bodas"),
        ("CORPORATIVO", "Evento corporativo"),
        ("OUTRO", "Outro"),
    ]

    code = models.CharField(max_length=20, unique=True, default=generate_code, editable=False)
    customer_name = models.CharField(max_length=120, verbose_name="Cliente")
    customer_whatsapp = models.CharField(max_length=30, verbose_name="WhatsApp")

    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES, blank=True, verbose_name="Tipo de evento")
    event_theme = models.CharField(max_length=180, blank=True, verbose_name="Tema real da festa")
    celebrant_name = models.CharField(max_length=120, blank=True, verbose_name="Nome do aniversariante / homenageado")
    celebrant_age = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Idade")
    event_date = models.DateField(null=True, blank=True, verbose_name="Data do evento", db_index=True)

    # Campo legado/resumo: continua existindo para compatibilidade com pedidos antigos.
    event_location = models.CharField(max_length=500, blank=True, verbose_name="Resumo do local do evento")

    event_venue = models.CharField(max_length=120, blank=True, verbose_name="Nome / tipo do local")
    event_city = models.CharField(max_length=120, blank=True, verbose_name="Cidade")
    event_state = models.CharField(max_length=80, blank=True, verbose_name="Estado / UF")
    event_neighborhood = models.CharField(max_length=120, blank=True, verbose_name="Bairro")
    event_street = models.CharField(max_length=180, blank=True, verbose_name="Rua / Avenida")
    event_number = models.CharField(max_length=40, blank=True, verbose_name="Número")
    event_complement = models.CharField(max_length=120, blank=True, verbose_name="Complemento")
    event_reference = models.CharField(max_length=180, blank=True, verbose_name="Ponto de referência")
    event_postcode = models.CharField(max_length=20, blank=True, verbose_name="CEP")
    event_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, editable=False)
    event_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, editable=False)

    guest_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Quantidade de convidados")

    keep_choices = models.JSONField(default=list, blank=True, verbose_name="Itens que deseja manter")
    change_choices = models.JSONField(default=list, blank=True, verbose_name="Itens que deseja adaptar")

    keep_details = models.TextField(blank=True, verbose_name="O que quer manter da inspiração")
    change_details = models.TextField(blank=True, verbose_name="O que quer adaptar / mudar")
    notes = models.TextField(blank=True, verbose_name="Outras observações")

    consent_whatsapp = models.BooleanField(default=False, verbose_name="Autorizou contato via WhatsApp")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RECEBIDO", db_index=True)
    total_reference = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total de referência")

    # Mantidos por compatibilidade com versões anteriores; o modo final usa wa.me gratuito.
    owner_notified = models.BooleanField(default=False)
    customer_notified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Solicitação"
        verbose_name_plural = "Solicitações"

    def __str__(self):
        return f"{self.code} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    decoration = models.ForeignKey(Decoration, on_delete=models.PROTECT)
    title_snapshot = models.CharField(max_length=180)
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Inspiração escolhida"
        verbose_name_plural = "Inspirações escolhidas"

    def __str__(self):
        return f"{self.order.code} - {self.title_snapshot}"
