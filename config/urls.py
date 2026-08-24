from django.contrib import admin
from django.urls import path, include
from catalog.views import home, manifest, service_worker
from orders.views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("manifest.webmanifest", manifest, name="manifest"),
    path("service-worker.js", service_worker, name="service_worker"),
    path("api/health/", health, name="health"),
    path("api/", include("orders.urls")),
]
