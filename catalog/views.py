import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.cache import cache_control, never_cache

from .models import Decoration, SiteSettings


def _absolute_static(path):
    return f"{settings.PUBLIC_SITE_URL}{static(path)}"


def home(request):
    site = SiteSettings.current()

    if not site.enabled and not request.user.is_staff:
        response = render(
            request,
            "catalog/maintenance.html",
            {"site": site},
            status=503,
        )
        response["Retry-After"] = "3600"
        response["Cache-Control"] = "no-store"
        return response

    decorations = Decoration.objects.filter(active=True).defer("image_blob")
    description = (
        f"{site.decorator_one_name} & {site.decorator_two_name}: "
        "inspirações e decorações personalizadas para aniversários, "
        "celebrações e eventos."
    )

    same_as = [
        url
        for url in [site.instagram_one_url, site.instagram_two_url]
        if url
    ]

    contacts = []
    if site.decorator_one_whatsapp:
        contacts.append({
            "@type": "ContactPoint",
            "telephone": f"+{site.decorator_one_whatsapp}",
            "contactType": f"Atendimento - {site.decorator_one_name}",
            "areaServed": "BR",
            "availableLanguage": "pt-BR",
        })
    if site.decorator_two_whatsapp:
        contacts.append({
            "@type": "ContactPoint",
            "telephone": f"+{site.decorator_two_whatsapp}",
            "contactType": f"Atendimento - {site.decorator_two_name}",
            "areaServed": "BR",
            "availableLanguage": "pt-BR",
        })

    structured_data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": site.business_name,
        "url": settings.PUBLIC_SITE_URL,
        "description": description,
        "image": _absolute_static("catalog/android-chrome-512x512.png"),
        "sameAs": same_as,
        "contactPoint": contacts,
    }

    return render(
        request,
        "catalog/home.html",
        {
            "site": site,
            "decorations": decorations,
            "canonical_url": settings.PUBLIC_SITE_URL,
            "page_description": description,
            "og_image_url": _absolute_static("catalog/android-chrome-512x512.png"),
            "structured_data": json.dumps(
                structured_data,
                ensure_ascii=False,
            ).replace("</", "<\\/"),
        },
    )


@cache_control(public=True, max_age=31536000, immutable=True)
def decoration_image(request, pk):
    try:
        decoration = Decoration.objects.only(
            "image_blob",
            "image_mime",
        ).get(pk=pk)
    except Decoration.DoesNotExist:
        return HttpResponseNotFound()

    if not decoration.image_blob:
        return HttpResponseNotFound()

    response = HttpResponse(
        bytes(decoration.image_blob),
        content_type=decoration.image_mime or "image/webp",
    )
    response["Content-Disposition"] = "inline"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@never_cache
def manifest(request):
    site = SiteSettings.current()
    data = {
        "id": "/",
        "name": site.business_name,
        "short_name": "Aline & Érika",
        "description": "Inspirações e decorações personalizadas para momentos especiais.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "lang": "pt-BR",
        "background_color": "#fffaf6",
        "theme_color": "#45132f",
        "icons": [
            {
                "src": static("catalog/android-chrome-192x192.png"),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": static("catalog/android-chrome-512x512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    }
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        content_type="application/manifest+json",
    )


@never_cache
def robots_txt(request):
    body = "\n".join([
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        f"Sitemap: {settings.PUBLIC_SITE_URL}/sitemap.xml",
        "",
    ])
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


@never_cache
def sitemap_xml(request):
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        f'    <loc>{settings.PUBLIC_SITE_URL}/</loc>\n'
        '    <changefreq>weekly</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '</urlset>\n'
    )
    return HttpResponse(body, content_type="application/xml; charset=utf-8")


@never_cache
def service_worker(request):
    js = r"""
const CACHE = 'aline-erika-decor-v8';
const PUBLIC_STATIC = ['/static/', '/inspiracoes/'];

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    Promise.all([
      caches.keys().then(keys =>
        Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))
      ),
      self.clients.claim()
    ])
  );
});

function isSafePublicAsset(url) {
  return PUBLIC_STATIC.some(prefix => url.pathname.startsWith(prefix))
    || url.pathname === '/manifest.webmanifest';
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/api/')) {
    return;
  }

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match('/'))
    );
    return;
  }

  if (!isSafePublicAsset(url)) return;

  event.respondWith(
    caches.match(request).then(cached => {
      const network = fetch(request).then(response => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then(cache => cache.put(request, copy));
        }
        return response;
      });

      return cached || network;
    })
  );
});
"""
    response = HttpResponse(js, content_type="application/javascript")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
