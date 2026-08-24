from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Decoration, SiteSettings


class DecorationAdminForm(forms.ModelForm):
    image_upload = forms.FileField(
        required=False,
        label="Enviar nova foto",
        help_text="JPG, PNG ou WEBP. Máximo de 4 MB. A foto fica salva no banco e não some em novos deploys."
    )
    clear_uploaded_image = forms.BooleanField(
        required=False,
        label="Remover foto enviada anteriormente"
    )

    class Meta:
        model = Decoration
        fields = "__all__"

    def clean_image_upload(self):
        file = self.cleaned_data.get("image_upload")
        if not file:
            return file
        if file.size > 4 * 1024 * 1024:
            raise forms.ValidationError("A imagem deve ter no máximo 4 MB.")
        content_type = getattr(file, "content_type", "") or ""
        if not content_type.startswith("image/"):
            raise forms.ValidationError("Envie um arquivo de imagem válido.")
        return file

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("clear_uploaded_image"):
            instance.image_blob = None
            instance.image_mime = ""
        upload = self.cleaned_data.get("image_upload")
        if upload:
            instance.image_blob = upload.read()
            instance.image_mime = getattr(upload, "content_type", "") or "image/jpeg"
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
    readonly_fields = ("image_preview",)
    fieldsets = (
        ("Inspiração", {"fields": ("title", "slug", "category", "description", "price", "active", "featured", "display_order")}),
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
    list_display = ("business_name", "decorator_one_name", "decorator_two_name", "owner_whatsapp", "enabled")
    fieldsets = (
        ("Identidade", {"fields": ("business_name", "decorator_one_name", "decorator_two_name", "owners", "hero_title")}),
        ("Atendimento e redes sociais", {"fields": ("owner_whatsapp", "instagram_one", "instagram_two")}),
        ("Publicação", {"fields": ("enabled",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "Aline Nayane & Érica Carina • Administração"
admin.site.site_title = "Decoração • Admin"
admin.site.index_title = "Gerencie inspirações, solicitações e atendimento"
