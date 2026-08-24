from django.db import models


class SiteSettings(models.Model):
    business_name = models.CharField(max_length=120, default="Aline & Erika Decorações")
    owners = models.CharField(max_length=180, default="Aline Naiane & Erika Carina")
    decorator_one_name = models.CharField(max_length=100, default="Aline Naiane")
    decorator_two_name = models.CharField(max_length=100, default="Erika Carina")
    hero_title = models.CharField(
        max_length=220,
        default="Cenários que transformam celebrações em memórias inesquecíveis."
    )
    owner_whatsapp = models.CharField(
        max_length=30,
        blank=True,
        default="5598996127032",
        help_text="Número que receberá os pedidos. Ex.: 5598999999999"
    )
    instagram_one = models.CharField(max_length=100, default="@aline.naiane.35", blank=True)
    instagram_two = models.CharField(max_length=100, default="@erikacarin_decor", blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuração do site"
        verbose_name_plural = "Configurações do site"

    def __str__(self):
        return self.business_name

    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Decoration(models.Model):
    CATEGORY_CHOICES = [
        ("INFANTIL", "Infantil"),
        ("ADULTO", "Adulto"),
        ("EVENTOS", "Eventos"),
    ]
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Caminho dentro de static. Ex.: catalog/images/pagina-03-1.jpeg"
    )
    image_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title
