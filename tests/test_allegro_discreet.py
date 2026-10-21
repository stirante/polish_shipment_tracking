"""Discreet mode keeps delivery details and drops products and prices."""

import json
import runpy
import unittest
from pathlib import Path


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "polish_shipment_tracking"
HELPERS = runpy.run_path(str(COMPONENT / "helpers.py"))

ORDERS = {
    "orderGroups": [{
        "groupId": "g1",
        "myorders": [{
            "id": "order-1",
            "orderDate": "2026-10-20T10:00:00Z",
            "seller": {"login": "shop"},
            "status": {"primary": {"status": "SENT"}},
            "totalCost": {"amount": "199.99", "currency": "PLN"},
            "payment": {"amount": {"amount": "199.99"}, "cardMask": "****1234"},
            "offers": [{
                "title": "Secret gift",
                "quantity": 1,
                "friendlyUrl": "https://allegro.pl/oferta/secret",
                "imageUrl": "https://a.allegroimg.com/original/secret.jpg",
                "unitPrice": {"amount": "199.99", "currency": "PLN"},
                "productId": "b8dd4d40-secret-product",
            }],
            "delivery": {
                "name": "Allegro Paczkomaty InPost",
                "deliveredBy": "InPost",
                "cost": {"amount": "9.99", "currency": "PLN"},
                "discount": {"originalCost": {"amount": "10.49"}, "type": "FREEBOX"},
                "waybillsData": {"waybills": [{
                    "waybillId": "620012345678",
                    "carrier": {"id": "INPOST", "name": "InPost"},
                    "pickupCode": {"code": "123456", "qrCode": "QR"},
                }]},
            },
        }],
    }],
}


class AllegroDiscreetTests(unittest.TestCase):
    def setUp(self):
        order = HELPERS["normalize_allegro_orders"](ORDERS)[0]
        self.stripped = HELPERS["strip_allegro_order"](order)

    def test_products_and_prices_are_gone(self):
        dumped = json.dumps(self.stripped)
        for secret in ("Secret gift", "secret.jpg", "secret-product", "****1234", "199.99", "10.49", "9.99"):
            self.assertNotIn(secret, dumped)
        self.assertNotIn("offers", self.stripped)
        self.assertNotIn("totalCost", self.stripped)

    def test_delivery_details_stay(self):
        self.assertEqual(self.stripped["status"], "SENT")
        self.assertEqual(self.stripped["seller"], "shop")
        self.assertEqual(self.stripped["deliveredBy"], "InPost")
        self.assertEqual(self.stripped["pickupCode"], "123456")
        self.assertEqual(self.stripped["waybills"][0]["number"], "620012345678")
        self.assertEqual(
            HELPERS["get_parcel_tracking_numbers"](self.stripped, "allegro"), {"620012345678"}
        )
        # The card reads the pickup QR code from the raw order.
        raw = self.stripped["_raw_response"]
        self.assertEqual(raw["delivery"]["waybillsData"]["waybills"][0]["pickupCode"]["qrCode"], "QR")


if __name__ == "__main__":
    unittest.main()
