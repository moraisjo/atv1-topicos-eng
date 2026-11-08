import unittest

from src.checkout import checkout
from src.models import Customer, Item, Order


def order_for(name, plan, *items):
    return Order(
        customer=Customer(name=name, plan=plan),
        items=tuple(Item(item_name, price, qty) for item_name, price, qty in items),
    )


class CheckoutTests(unittest.TestCase):
    def test_regular_customer_pays_shipping(self):
        result = checkout(order_for("Ana", "REGULAR", ("Book", 100.0, 1)))
        self.assertEqual(result["subtotal"], 100.0)
        self.assertEqual(result["discount"], 0.0)
        self.assertEqual(result["shipping"], 12.0)
        self.assertEqual(result["tax"], 20.16)
        self.assertEqual(result["total"], 132.16)

    def test_silver_customer_gets_five_percent_discount(self):
        result = checkout(order_for("Bruno", "SILVER", ("Headset", 100.0, 1)))
        self.assertEqual(result["discount"], 5.0)
        self.assertEqual(result["shipping"], 12.0)
        self.assertEqual(result["total"], 126.26)

    def test_gold_customer_gets_ten_percent_discount(self):
        result = checkout(order_for("Carla", "GOLD", ("Keyboard", 100.0, 1)))
        self.assertEqual(result["discount"], 10.0)
        self.assertEqual(result["total"], 120.36)

    def test_gold_customer_can_receive_free_shipping(self):
        result = checkout(order_for("Diego", "GOLD", ("Monitor", 200.0, 1)))
        self.assertEqual(result["discount"], 20.0)
        self.assertEqual(result["shipping"], 0.0)
        self.assertEqual(result["tax"], 32.4)
        self.assertEqual(result["total"], 212.4)

    def test_free_shipping_boundary_is_inclusive(self):
        result = checkout(order_for("Eva", "REGULAR", ("Chair", 150.0, 1)))
        self.assertEqual(result["shipping"], 0.0)
        self.assertEqual(result["total"], 177.0)

    def test_multiple_items_are_accumulated(self):
        result = checkout(
            order_for(
                "Fábio",
                "SILVER",
                ("Mouse", 50.0, 2),
                ("Cable", 25.0, 2),
            )
        )
        self.assertEqual(result["subtotal"], 150.0)
        self.assertEqual(result["discount"], 7.5)
        self.assertEqual(result["shipping"], 12.0)
        self.assertEqual(result["total"], 182.31)

    def test_message_reflects_shipping_condition(self):
        paid = checkout(order_for("Gabi", "REGULAR", ("Book", 100.0, 1)))
        free = checkout(order_for("Hugo", "REGULAR", ("Desk", 160.0, 1)))
        self.assertEqual(paid["message"], "Gabi: frete R$ 12.00 | total R$ 132.16")
        self.assertEqual(free["message"], "Hugo: frete grátis | total R$ 188.80")


if __name__ == "__main__":
    unittest.main()
