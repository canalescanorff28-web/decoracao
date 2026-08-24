from django.contrib import admin
from .models import Decoration, SiteSettings


@admin.register(Decoration)
class DecorationAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "active", "featured", "display_order")
    list_filter = ("category", "active", "featured")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("price", "active", "display_order")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "decorator_one_name",
        "decorator_two_name",
        "owner_whatsapp",
        "enabled",
    )
    fieldsets = (
        ("Identidade", {
            "fields": (
                "business_name",
                "decorator_one_name",
                "decorator_two_name",
                "owners",
                "hero_title",
            )
        }),
        ("Atendimento", {
            "fields": ("owner_whatsapp", "instagram_one", "instagram_two")
        }),
        ("Publicação", {"fields": ("enabled",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
