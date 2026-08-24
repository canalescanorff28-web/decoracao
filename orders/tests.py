import json
from django.test import TestCase
from django.urls import reverse
from catalog.models import Decoration

class OrderApiTests(TestCase):
    def setUp(self):
        self.deco = Decoration.objects.create(
            title="Teste", slug="teste", category="EVENTOS", price="100.00", active=True
        )

    def test_order_creation(self):
        r = self.client.post(
            "/api/orders/",
            data=json.dumps({
                "name":"Cliente",
                "whatsapp":"5598999999999",
                "items":[self.deco.id],
                "consent_whatsapp":False
            }),
            content_type="application/json"
        )
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.json()["ok"])
