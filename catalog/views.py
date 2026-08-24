from django.http import HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from .models import Decoration, SiteSettings
import json

def home(request):
    settings_obj = SiteSettings.current()
    decorations = Decoration.objects.filter(active=True)
    return render(request, "catalog/home.html", {
        "site": settings_obj,
        "decorations": decorations,
    })

def manifest(request):
    data = {
        "name": "Catálogo Decorações",
        "short_name": "Decor",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#fff8fb",
        "theme_color": "#4d1b48",
        "icons": [
            {"src": static("catalog/icon-192.svg"), "sizes": "192x192", "type": "image/svg+xml"},
            {"src": static("catalog/icon-512.svg"), "sizes": "512x512", "type": "image/svg+xml"},
        ],
    }
    return HttpResponse(json.dumps(data), content_type="application/manifest+json")

def service_worker(request):
    js = """
const CACHE='catalogo-decor-v1';
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/']))));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
});
"""
    return HttpResponse(js, content_type="application/javascript")
