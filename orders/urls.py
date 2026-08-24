from django.urls import path
from .views import create_order, order_status

urlpatterns = [
    path("orders/", create_order, name="create_order"),
    path("orders/<str:code>/", order_status, name="order_status"),
]
