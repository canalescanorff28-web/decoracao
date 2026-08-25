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
            "event_venue": "Salão de festas",
            "event_city": "Santa Inês",
            "event_state": "MA",
            "event_neighborhood": "Centro",
            "event_street": "Rua Teste",
            "event_number": "44",
            "event_complement": "",
            "event_reference": "Próximo ao mercado",
            "event_postcode": "65300000",
            "event_latitude": "-3.6666667",
            "event_longitude": "-45.3833333",
            "guest_count": "100",
            "keep_choices": ["Estrutura da montagem", "Mesas e mobiliário"],
            "change_choices": ["Trocar tema / personagens", "Mudar cores"],
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
        self.assertTrue(payload["owner_whatsapp_link"].startswith("/api/orders/"))
        self.assertEqual(payload["delivery_mode"], "direct-web-mobile-whatsapp-handoff")
        self.assertIn("whatsapp_routes", payload)

        message = payload["whatsapp_message"]
        self.assertIn("🌸", message)
        self.assertIn("Super Mario", message)
        self.assertIn("estrutura e mesas", message)
        self.assertIn("cores e personagens", message)
        self.assertIn("evento para 100 pessoas", message)
        self.assertIn("Érika Carina", message)
        self.assertIn("Convidados: 100", message)
        self.assertIn("Santa Inês", message)
        self.assertIn("Estrutura da montagem", message)
        self.assertIn("Trocar tema / personagens", message)
        self.assertIn("\n", message)
        encoded = payload["whatsapp_message_encoded"]
        self.assertNotIn("🌸", encoded)
        self.assertIn("%F0%9F%8C%B8", encoded)
        self.assertIn("%0A", encoded)
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


    def test_server_side_whatsapp_handoff_preserves_emojis(self):
        created = self.client.post(
            "/api/orders/",
            data=self.payload(),
            content_type="application/json",
        ).json()

        route = created["whatsapp_routes"]["aline"]
        response = self.client.get(route)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        self.assertIn("https://web.whatsapp.com/send?", html)
        # 🌸 em UTF-8 percent-encoded.
        self.assertIn("%F0%9F%8C%B8", html)
        # ✨ em UTF-8 percent-encoded.
        self.assertIn("%E2%9C%A8", html)
        # Quebra de linha real deve chegar codificada.
        self.assertIn("%0A", html)
        # U+FFFD (replacement char) não pode existir.
        self.assertNotIn("%EF%BF%BD", html)
        # Não usa mais um Location gigante.
        self.assertNotIn("Location", response.headers)

    def test_erika_handoff_uses_erika_number(self):
        created = self.client.post(
            "/api/orders/",
            data=self.payload(),
            content_type="application/json",
        ).json()

        response = self.client.get(created["whatsapp_routes"]["erika"])
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn("phone=5598984673264", html)

    def test_generic_whatsapp_contact_uses_server_redirect(self):
        response = self.client.get("/api/whatsapp/aline/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn("web.whatsapp.com/send", html)
        self.assertIn("%F0%9F", html)
        self.assertIn("whatsapp://send?", html)

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
