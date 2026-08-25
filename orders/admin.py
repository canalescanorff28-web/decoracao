from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Order, OrderItem
from .whatsapp import wa_link, customer_ack, customer_confirmed, customer_finished


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("decoration", "title_snapshot", "unit_price_snapshot", "quantity")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("code", "customer_name", "event_theme", "event_date", "status", "total_reference", "whatsapp_shortcut", "created_at")
    list_display_links = ("code", "customer_name")
    list_editable = ("status",)
    list_filter = ("status", "event_type", "event_date", "created_at")
    search_fields = ("code", "customer_name", "customer_whatsapp", "event_theme", "celebrant_name")
    date_hierarchy = "created_at"
    readonly_fields = (
        "code", "total_reference", "created_at", "updated_at",
        "owner_notified", "customer_notified", "whatsapp_tools",
        "event_location",
    )
    fieldsets = (
        ("Solicitação", {"fields": ("code", "status", "total_reference", "created_at", "updated_at")}),
        ("Cliente", {"fields": ("customer_name", "customer_whatsapp", "consent_whatsapp", "whatsapp_tools")}),
        ("Evento", {"fields": ("event_type", "event_theme", "celebrant_name", "celebrant_age", "event_date", "guest_count")}),
        ("Local do evento", {"fields": (
            "event_venue", "event_city", "event_state", "event_neighborhood",
            "event_street", "event_number", "event_complement", "event_reference",
            "event_postcode", "event_location"
        )}),
        ("Personalização", {"fields": ("keep_choices", "keep_details", "change_choices", "change_details", "notes")}),
        ("Compatibilidade técnica", {"fields": ("owner_notified", "customer_notified"), "classes": ("collapse",)}),
    )
    inlines = [OrderItemInline]
    list_per_page = 50
    save_on_top = True

    @admin.display(description="WhatsApp")
    def whatsapp_shortcut(self, obj):
        url = wa_link(obj.customer_whatsapp, customer_ack(obj))
        if not url:
            return "—"
        return format_html('<a href="{}" target="_blank" style="font-weight:700">Responder ↗</a>', url)

    @admin.display(description="Atendimento gratuito pelo WhatsApp")
    def whatsapp_tools(self, obj):
        if not obj or not obj.pk:
            return "Salve a solicitação primeiro."
        buttons = [
            ("Recebemos sua solicitação", customer_ack(obj)),
            ("Pedido confirmado", customer_confirmed(obj)),
            ("Finalização / agradecimento", customer_finished(obj)),
        ]
        html = []
        for label, message in buttons:
            url = wa_link(obj.customer_whatsapp, message)
            html.append(f'<a href="{url}" target="_blank" style="display:inline-block;margin:4px 8px 4px 0;padding:8px 12px;border-radius:8px;background:#4b163b;color:#fff;text-decoration:none">{label} ↗</a>')
        return mark_safe("".join(html))


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "title_snapshot", "unit_price_snapshot", "quantity")
    search_fields = ("order__code", "title_snapshot")
