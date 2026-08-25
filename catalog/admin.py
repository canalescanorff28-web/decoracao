from io import BytesIO

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from PIL import Image, UnidentifiedImageError
from .models import Decoration, SiteSettings


class DecorationAdminForm(forms.ModelForm):
    image_upload = forms.FileField(
        required=False,
        label="Enviar nova foto",
        help_text="JPG, PNG ou WEBP. Até 8 MB; o sistema otimiza automaticamente antes de salvar no banco."
    )
    clear_uploaded_image = forms.BooleanField(
        required=False,
        label="Remover foto enviada anteriormente"
    )

    class Meta:
        model = Decoration
        fields = "__all__"

    def clean_image_upload(self):
        upload = self.cleaned_data.get("image_upload")
        if not upload:
            return upload

        if upload.size > 8 * 1024 * 1024:
            raise forms.ValidationError("A imagem original deve ter no máximo 8 MB.")

        try:
            image = Image.open(upload)
            image.verify()
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise forms.ValidationError("Use JPG, PNG ou WEBP.")
        except (UnidentifiedImageError, OSError):
            raise forms.ValidationError("O arquivo enviado não é uma imagem válida.")
        finally:
            upload.seek(0)

        return upload

    @staticmethod
    def _optimized_image(upload):
        image = Image.open(upload)
        image.load()

        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert(
                "RGBA" if "transparency" in image.info else "RGB"
            )

        image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)

        output = BytesIO()
        image.save(
            output,
            format="WEBP",
            quality=86,
            method=6,
        )
        return output.getvalue(), "image/webp"

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get("clear_uploaded_image"):
            instance.image_blob = None
            instance.image_mime = ""

        upload = self.cleaned_data.get("image_upload")
        if upload:
            blob, mime = self._optimized_image(upload)
            instance.image_blob = blob
            instance.image_mime = mime

        if commit:
            instance.save()
            self.save_m2m()

        return instance


@admin.register(Decoration)
class DecorationAdmin(admin.ModelAdmin):
    form = DecorationAdminForm
    list_display = ("preview", "title", "category", "price", "active", "featured", "display_order")
    list_filter = ("category", "active", "featured")
    search_fields = ("title", "description")
    list_editable = ("price", "active", "featured", "display_order")
    readonly_fields = ("image_preview", "updated_at")
    fieldsets = (
        ("Inspiração", {"fields": ("title", "slug", "category", "description", "price", "active", "featured", "display_order", "updated_at")}),
        ("Foto", {"fields": ("image_preview", "image_upload", "clear_uploaded_image")}),
        ("Imagem avançada / legado", {"fields": ("image_url", "image_path"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).defer("image_blob")

    @admin.display(description="Foto")
    def preview(self, obj):
        return format_html('<img src="{}" style="width:70px;height:52px;object-fit:cover;border-radius:8px" alt="">', obj.image_src)

    @admin.display(description="Prévia atual")
    def image_preview(self, obj):
        if not obj or not obj.pk:
            return "Salve a inspiração para visualizar a foto."
        return format_html('<img src="{}" style="max-width:520px;max-height:320px;object-fit:contain;border-radius:14px;border:1px solid #ddd" alt="">', obj.image_src)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("business_name", "decorator_one_name", "decorator_two_name", "decorator_one_whatsapp", "decorator_two_whatsapp", "enabled")
    fieldsets = (
        ("Identidade", {"fields": ("business_name", "decorator_one_name", "decorator_two_name", "owners", "hero_title")}),
        ("Atendimento e redes sociais", {"fields": ("decorator_one_whatsapp", "decorator_two_whatsapp", "instagram_one", "instagram_two")}),
        ("Publicação", {"fields": ("enabled",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "Aline Nayane & Érika Carina • Administração"
admin.site.site_title = "Decoração • Admin"
admin.site.index_title = "Gerencie inspirações, solicitações e atendimento"
