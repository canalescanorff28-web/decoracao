from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from catalog.models import Decoration, SiteSettings
from .models import Order
from .whatsapp import format_order


class OrderApiTests(TestCase):
    def setUp(self):
        site = SiteSettings.current()
        site.decorator_one_whatsapp = "5598984669115"
        site.decorator_two_whatsapp = "5598984673264"
        site.save(update_fields=[
            "decorator_one_whatsapp",
            "decorator_two_whatsapp",
        ])

        self.deco = Decoration.objects.create(
            title="Inspiração Cerejinha",
            slug="inspiracao-cerejinha-teste",
            category="INFANTIL",
            description="Teste",
            price=Decimal("300.00"),
            active=True,
        )

    def payload(self, **overrides):
        data = {
            "name": "Teste Cliente",
            "whatsapp": "98999999999",
            "event_type": "ANIVERSARIO",
            "event_theme": "Super Mario",
            "celebrant_name": "Gabriel",
            "celebrant_age": "6",
            "event_date": (date.today() + timedelta(days=30)).isoformat(),
            "event_location": "Salão",
            "keep_details": "estrutura e mesas",
            "change_details": "cores e personagens",
            "notes": "evento para 100 pessoas",
            "consent_whatsapp": True,
            "website": "",
            "items": [self.deco.id],
        }
        data.update(overrides)
        return data

    def test_order_creation_and_message_regression(self):
        response = self.client.post(
            "/api/orders/",
            data=self.payload(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertIn("wa.me/5598984669115", payload["owner_whatsapp_link"])

        message = payload["whatsapp_message"]
        self.assertIn("🌸", message)
        self.assertIn("Super Mario", message)
        self.assertIn("estrutura e mesas", message)
        self.assertIn("cores e personagens", message)
        self.assertIn("evento para 100 pessoas", message)
        self.assertIn("Érika Carina", message)
        self.assertIn("\n", message)
        self.assertNotIn("\\n", message)
        self.assertNotIn("�", message)
        self.assertNotIn("\\*", message)

        order = Order.objects.get(code=payload["order_code"])
        self.assertEqual(order.event_theme, "Super Mario")
        self.assertEqual(len(order.code), 14)

    def test_requires_whatsapp_consent(self):
        response = self.client.post(
            "/api/orders/",
            data=self.payload(consent_whatsapp=False),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_past_event_date(self):
        response = self.client.post(
            "/api/orders/",
            data=self.payload(
                event_date=(date.today() - timedelta(days=1)).isoformat()
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_rejects_honeypot_spam(self):
        response = self.client.post(
            "/api/orders/",
            data=self.payload(website="https://spam.example"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_public_status_does_not_expose_personal_data(self):
        create = self.client.post(
            "/api/orders/",
            data=self.payload(),
            content_type="application/json",
        ).json()

        status = self.client.get(
            f"/api/orders/{create['order_code']}/"
        )
        self.assertEqual(status.status_code, 200)
        data = status.json()
        self.assertNotIn("customer_name", data)
        self.assertNotIn("customer_whatsapp", data)
        self.assertNotIn("event_theme", data)

    def test_format_order_uses_real_newlines(self):
        self.client.post(
            "/api/orders/",
            data=self.payload(),
            content_type="application/json",
        )
        order = Order.objects.latest("created_at")
        message = format_order(order)
        self.assertIn("\n", message)
        self.assertNotIn("\\n", message)
        self.assertNotIn("*", message)
