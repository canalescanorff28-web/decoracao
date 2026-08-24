from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("decoration", "title_snapshot", "unit_price_snapshot", "quantity")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("code", "customer_name", "customer_whatsapp", "status", "total_reference", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("code", "customer_name", "customer_whatsapp")
    readonly_fields = ("code", "total_reference", "created_at", "updated_at", "owner_notified", "customer_notified")
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "title_snapshot", "unit_price_snapshot", "quantity")
