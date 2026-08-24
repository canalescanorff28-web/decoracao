from django.contrib import admin
from .models import Decoration, SiteSettings

@admin.register(Decoration)
class DecorationAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "active", "featured", "display_order")
    list_filter = ("category", "active", "featured")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("business_name", "owners", "owner_whatsapp", "enabled")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
