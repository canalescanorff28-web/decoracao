import json
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.cache import cache_control
from .models import Decoration, SiteSettings


def home(request):
    site = SiteSettings.current()
    decorations = Decoration.objects.filter(active=True).defer("image_blob")
    return render(request, "catalog/home.html", {"site": site, "decorations": decorations})


@cache_control(public=True, max_age=86400)
def decoration_image(request, pk):
    try:
        decoration = Decoration.objects.only("image_blob", "image_mime").get(pk=pk)
    except Decoration.DoesNotExist:
        return HttpResponseNotFound()
    if not decoration.image_blob:
        return HttpResponseNotFound()
    response = HttpResponse(bytes(decoration.image_blob), content_type=decoration.image_mime or "image/jpeg")
    response["Content-Disposition"] = "inline"
    return response


def manifest(request):
    site = SiteSettings.current()
    data = {
        "name": site.business_name,
        "short_name": "Aline & Érica Decor",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#fff8fb",
        "theme_color": "#4b163b",
        "icons": [
            {"src": static("catalog/icon-192.png"), "sizes": "192x192", "type": "image/png"},
            {"src": static("catalog/icon-512.png"), "sizes": "512x512", "type": "image/png"},
        ],
    }
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/manifest+json")


def service_worker(request):
    js = """
const CACHE='aline-erica-decor-v5';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  e.respondWith(fetch(e.request).then(r=>{const c=r.clone(); caches.open(CACHE).then(cache=>cache.put(e.request,c)); return r;}).catch(()=>caches.match(e.request)));
});
"""
    response = HttpResponse(js, content_type="application/javascript")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
