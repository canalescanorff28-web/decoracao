from django.urls import path
from .views import (
    contact_whatsapp,
    create_order,
    order_status,
    order_whatsapp_redirect,
)

urlpatterns = [
    path("orders/", create_order, name="create_order"),
    path(
        "orders/<str:code>/whatsapp/<str:decorator>/",
        order_whatsapp_redirect,
        name="order_whatsapp_redirect",
    ),
    path("orders/<str:code>/", order_status, name="order_status"),
    path(
        "whatsapp/<str:decorator>/",
        contact_whatsapp,
        name="contact_whatsapp",
    ),
]
