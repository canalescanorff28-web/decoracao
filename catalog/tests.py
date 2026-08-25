from django.core.management import call_command
from django.test import TestCase

from .models import Decoration, SiteSettings


class SeedCatalogTests(TestCase):
    def test_seed_runs_twice_without_crashing_or_overwriting(self):
        site = SiteSettings.current()
        site.decorator_one_whatsapp = ""
        site.decorator_two_whatsapp = ""
        site.save(update_fields=[
            "decorator_one_whatsapp",
            "decorator_two_whatsapp",
        ])

        call_command("seed_catalog")
        first_count = Decoration.objects.count()
        self.assertGreater(first_count, 0)

        site.refresh_from_db()
        self.assertEqual(site.decorator_one_whatsapp, "5598984669115")
        self.assertEqual(site.decorator_two_whatsapp, "5598984673264")

        first = Decoration.objects.order_by("id").first()
        first.title = "Título alterado pelo admin"
        first.save()

        call_command("seed_catalog")

        self.assertEqual(Decoration.objects.count(), first_count)
        first.refresh_from_db()
        self.assertEqual(first.title, "Título alterado pelo admin")


class PublicSiteTests(TestCase):
    def test_home_contains_both_whatsapp_choices(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn('data-wa-number="5598984669115"', html)
        self.assertIn('data-wa-number="5598984673264"', html)
        self.assertIn('data-wa-person="aline"', html)
        self.assertIn('data-wa-person="erika"', html)
        self.assertIn('id="useGpsLocation"', html)
        self.assertIn('name="event_city"', html)
        self.assertIn('name="keep_choices"', html)
        self.assertIn('name="change_choices"', html)

    def test_service_worker_does_not_cache_admin_or_api(self):
        response = self.client.get("/service-worker.js")
        text = response.content.decode("utf-8")
        self.assertIn("url.pathname.startsWith('/admin/')", text)
        self.assertIn("url.pathname.startsWith('/api/')", text)

    def test_robots_and_sitemap_exist(self):
        self.assertEqual(self.client.get("/robots.txt").status_code, 200)
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)
