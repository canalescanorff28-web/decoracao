from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify


class SiteSettings(models.Model):
    business_name = models.CharField(max_length=120, default="Aline Nayane & Érica Carina Decoração")
    owners = models.CharField(max_length=180, default="Aline Nayane & Érica Carina")
    decorator_one_name = models.CharField(max_length=100, default="Aline Nayane")
    decorator_two_name = models.CharField(max_length=100, default="Érica Carina")
    hero_title = models.CharField(
        max_length=220,
        default="Transformamos inspirações em cenários únicos para momentos inesquecíveis."
    )
    # Campo legado: mantido apenas para compatibilidade com versões anteriores.
    # O fluxo novo usa um WhatsApp separado para cada decoradora.
    owner_whatsapp = models.CharField(
        max_length=30,
        blank=True,
        default="",
        help_text="Campo legado. O atendimento usa os WhatsApps individuais abaixo."
    )
    decorator_one_whatsapp = models.CharField(
        max_length=30,
        blank=True,
        default="5598984669115",
        verbose_name="WhatsApp da Aline Nayane",
        help_text="Formato internacional, somente números. Ex.: 5598984669115"
    )
    decorator_two_whatsapp = models.CharField(
        max_length=30,
        blank=True,
        default="5598984673264",
        verbose_name="WhatsApp da Érika Carina",
        help_text="Formato internacional, somente números. Ex.: 5598984673264"
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

    @staticmethod
    def _instagram_url(handle):
        handle = (handle or "").strip()
        if not handle:
            return ""
        if handle.startswith("http://") or handle.startswith("https://"):
            return handle
        return f"https://instagram.com/{handle.lstrip('@')}"

    @property
    def instagram_one_url(self):
        return self._instagram_url(self.instagram_one)

    @property
    def instagram_two_url(self):
        return self._instagram_url(self.instagram_two)


class Decoration(models.Model):
    CATEGORY_CHOICES = [
        ("INFANTIL", "Infantil"),
        ("ADULTO", "Adulto"),
        ("EVENTOS", "Eventos"),
    ]
    title = models.CharField(max_length=180, verbose_name="Nome da inspiração")
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Categoria")
    description = models.TextField(blank=True, verbose_name="Descrição")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor de referência")

    # Compatibilidade com as imagens iniciais do PDF e com URLs externas.
    image_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Avançado: caminho de imagem já existente em static/."
    )
    image_url = models.URLField(blank=True, verbose_name="URL externa da imagem")

    # Upload persistente no PostgreSQL/Neon: não depende do disco temporário do Runsite.
    image_blob = models.BinaryField(blank=True, null=True, editable=False)
    image_mime = models.CharField(max_length=80, blank=True, editable=False)

    active = models.BooleanField(default=True, verbose_name="Publicada")
    featured = models.BooleanField(default=False, verbose_name="Destaque")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        ordering = ["display_order", "title"]
        verbose_name = "Inspiração"
        verbose_name_plural = "Inspirações"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "inspiracao"
            candidate = base
            index = 2
            qs = Decoration.objects.exclude(pk=self.pk)
            while qs.filter(slug=candidate).exists():
                candidate = f"{base}-{index}"
                index += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def image_src(self):
        if self.image_mime and self.pk:
            return reverse("decoration_image", args=[self.pk])
        if self.image_url:
            return self.image_url
        if self.image_path:
            return static(self.image_path)
        return static("catalog/icon-512.svg")
