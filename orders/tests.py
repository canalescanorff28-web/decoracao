import json
from django.test import TestCase
from catalog.models import Decoration, SiteSettings
from .models import Order
from .whatsapp import format_order


class OrderApiTests(TestCase):
    def setUp(self):
        site = SiteSettings.current()
        site.owner_whatsapp = "5598984669115"
        site.save(update_fields=["owner_whatsapp"])
        self.deco = Decoration.objects.create(
            title="Inspiração Cerejinha",
            slug="inspiracao-cerejinha",
            category="INFANTIL",
            price="100.00",
            active=True,
        )

    def test_order_creation_with_custom_theme(self):
        response = self.client.post(
            "/api/orders/",
            data=json.dumps({
                "name": "Cliente",
                "whatsapp": "5598999999999",
                "event_theme": "Moranguinho",
                "keep_details": "Quero manter a disposição das mesas.",
                "change_details": "Trocar personagens e adaptar as cores.",
                "items": [self.deco.id],
                "consent_whatsapp": True,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertIn("wa.me/5598984669115", payload["owner_whatsapp_link"])
        order = Order.objects.get(code=payload["order_code"])
        self.assertEqual(order.event_theme, "Moranguinho")
        self.assertIn("Moranguinho", format_order(order))

    def test_theme_is_required(self):
        response = self.client.post(
            "/api/orders/",
            data=json.dumps({"name": "Cliente", "whatsapp": "5598999999999", "items": [self.deco.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
