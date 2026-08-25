from django.contrib import admin
from django.urls import include, path

from catalog.views import (
    decoration_image,
    home,
    manifest,
    robots_txt,
    service_worker,
    sitemap_xml,
)
from orders.views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("inspiracoes/<int:pk>/imagem/", decoration_image, name="decoration_image"),
    path("manifest.webmanifest", manifest, name="manifest"),
    path("service-worker.js", service_worker, name="service_worker"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
    path("api/health/", health, name="health"),
    path("api/", include("orders.urls")),
]
