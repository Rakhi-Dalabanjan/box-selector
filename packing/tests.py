import json
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Box, Order, OrderItem, Product
from .services import can_pack, recommend_box


# ---------- helpers (plain setup, they skip validation on purpose) ----------

def make_product(name="Widget", dims=(50, 50, 50), weight=100):
    return Product.objects.create(
        name=name, length=dims[0], width=dims[1], height=dims[2], weight=weight
    )


def make_box(name, dims, max_weight, cost):
    return Box.objects.create(
        name=name,
        inner_length=dims[0],
        inner_width=dims[1],
        inner_height=dims[2],
        max_weight=max_weight,
        cost=Decimal(cost),
    )


def make_order(*pairs):
    """make_order((product, qty), (product2, qty2), ...)"""
    order = Order.objects.create()
    for product, quantity in pairs:
        OrderItem.objects.create(order=order, product=product, quantity=quantity)
    return order


# ---------- 1. packing geometry (no database needed) ----------

class CanPackTests(SimpleTestCase):
    def test_two_items_fit_exactly(self):
        self.assertTrue(can_pack([(150, 200, 100)] * 2, (300, 200, 100)))

    def test_item_too_tall_in_every_rotation(self):
        self.assertFalse(can_pack([(60, 60, 60)], (100, 100, 50)))

    def test_rotation_is_allowed(self):
        # a long thin item only fits lying along the box's long side
        self.assertTrue(can_pack([(10, 10, 100)], (100, 10, 10)))

    def test_volume_passes_but_geometry_fails(self):
        # 288,000 mm3 of items in a 500,000 mm3 box, yet it cannot work:
        # two 60x60 footprints don't fit side by side in 100x100,
        # and stacking needs 80 mm of height in a 50 mm box.
        self.assertFalse(can_pack([(60, 60, 40)] * 2, (100, 100, 50)))

    def test_only_one_large_cube_fits_in_a_bigger_cube(self):
        # 3 x 216,000 = 648,000 is under 1,000,000, but 60 + 60 > 100 on every axis
        self.assertFalse(can_pack([(60, 60, 60)] * 3, (100, 100, 100)))

    def test_four_cubes_fill_a_box_exactly(self):
        self.assertTrue(can_pack([(50, 50, 50)] * 4, (100, 100, 50)))

    def test_fifth_cube_does_not_fit(self):
        self.assertFalse(can_pack([(50, 50, 50)] * 5, (100, 100, 50)))


# ---------- 2. model validation ----------

class ModelValidationTests(TestCase):
    def test_valid_product_passes(self):
        Product(name="ok", length=1, width=1, height=1, weight=1).full_clean()

    def test_zero_dimension_is_rejected(self):
        with self.assertRaises(ValidationError):
            Product(name="bad", length=0, width=1, height=1, weight=1).full_clean()

    def test_zero_weight_is_rejected(self):
        with self.assertRaises(ValidationError):
            Product(name="bad", length=1, width=1, height=1, weight=0).full_clean()

    def test_negative_box_cost_is_rejected(self):
        box = Box(
            name="bad", inner_length=1, inner_width=1, inner_height=1,
            max_weight=1, cost=Decimal("-1.00"),
        )
        with self.assertRaises(ValidationError):
            box.full_clean()

    def test_zero_quantity_is_rejected(self):
        order = Order.objects.create()
        item = OrderItem(order=order, product=make_product(), quantity=0)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_same_product_twice_in_one_order_is_rejected(self):
        product = make_product()
        order = make_order((product, 1))
        # atomic() keeps the failed INSERT from breaking the rest of the test
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrderItem.objects.create(order=order, product=product, quantity=2)


# ---------- 3. recommend_box (needs the database) ----------

class RecommendBoxTests(TestCase):
    def setUp(self):
        self.small = make_box("Small", (100, 100, 100), 1000, "5.00")
        self.large = make_box("Large", (300, 300, 300), 5000, "10.00")

    def test_cheapest_fitting_box_is_chosen(self):
        order = make_order((make_product(), 1))
        self.assertEqual(recommend_box(order), self.small)

    def test_too_big_for_cheap_box_goes_to_bigger_one(self):
        order = make_order((make_product(dims=(150, 150, 150)), 1))
        self.assertEqual(recommend_box(order), self.large)

    def test_weight_limit_is_respected(self):
        # geometry fits the small box, but 2 x 600 g = 1200 g > 1000 g
        order = make_order((make_product(weight=600), 2))
        self.assertEqual(recommend_box(order), self.large)

    def test_returns_none_when_nothing_fits(self):
        order = make_order((make_product(dims=(400, 10, 10)), 1))
        self.assertIsNone(recommend_box(order))

    def test_returns_none_when_too_heavy_for_every_box(self):
        order = make_order((make_product(weight=6000), 1))
        self.assertIsNone(recommend_box(order))

    def test_equal_cost_prefers_smaller_box(self):
        Box.objects.all().delete()
        make_box("Roomy", (200, 200, 200), 1000, "5.00")
        snug = make_box("Snug", (100, 100, 100), 1000, "5.00")
        order = make_order((make_product(), 1))
        self.assertEqual(recommend_box(order), snug)

    def test_empty_order_raises(self):
        with self.assertRaises(ValueError):
            recommend_box(Order.objects.create())


# ---------- 4. the JSON API ----------

class ApiTests(TestCase):
    def setUp(self):
        self.product = make_product()
        self.small = make_box("Small", (100, 100, 100), 1000, "5.00")
        self.large = make_box("Large", (300, 300, 300), 5000, "10.00")

    def post_order(self, payload):
        return self.client.post(
            reverse("orders"), data=json.dumps(payload), content_type="application/json"
        )

    def test_create_order(self):
        response = self.post_order(
            {"items": [{"product_id": self.product.pk, "quantity": 2}]}
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["items"][0]["product_id"], self.product.pk)
        self.assertEqual(body["items"][0]["quantity"], 2)
        self.assertEqual(Order.objects.count(), 1)

    def test_bad_payloads_return_400_and_create_nothing(self):
        pid = self.product.pk
        bad_payloads = {
            "zero quantity": {"items": [{"product_id": pid, "quantity": 0}]},
            "negative quantity": {"items": [{"product_id": pid, "quantity": -1}]},
            "quantity too large": {"items": [{"product_id": pid, "quantity": 1001}]},
            "boolean quantity": {"items": [{"product_id": pid, "quantity": True}]},
            "string quantity": {"items": [{"product_id": pid, "quantity": "2"}]},
            "unknown product": {"items": [{"product_id": 999999, "quantity": 1}]},
            "empty items list": {"items": []},
            "missing items key": {},
            "duplicate product": {
                "items": [
                    {"product_id": pid, "quantity": 1},
                    {"product_id": pid, "quantity": 1},
                ]
            },
            "item is not an object": {"items": ["x"]},
            "body is a list": [],
        }
        for label, payload in bad_payloads.items():
            with self.subTest(label):
                response = self.post_order(payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json())
        self.assertEqual(Order.objects.count(), 0)

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            reverse("orders"), data="{not json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_list_orders(self):
        make_order((self.product, 1))
        make_order((self.product, 3))
        response = self.client.get(reverse("orders"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["orders"]), 2)

    def test_retrieve_order(self):
        order = make_order((self.product, 4))
        response = self.client.get(reverse("order-detail", args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], order.pk)
        self.assertEqual(response.json()["items"][0]["quantity"], 4)

    def test_retrieve_missing_order_is_404(self):
        response = self.client.get(reverse("order-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_recommendation_returns_cheapest_box(self):
        order = make_order((self.product, 1))
        response = self.client.get(reverse("order-recommendation", args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        box = response.json()["box"]
        self.assertEqual(box["id"], self.small.pk)
        self.assertEqual(box["cost"], "5.00")

    def test_recommendation_when_nothing_fits(self):
        order = make_order((make_product(dims=(400, 10, 10)), 1))
        response = self.client.get(reverse("order-recommendation", args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["box"])

    def test_recommendation_for_missing_order_is_404(self):
        response = self.client.get(reverse("order-recommendation", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_recommendation_for_empty_order_is_400(self):
        order = Order.objects.create()  # possible via the admin
        response = self.client.get(reverse("order-recommendation", args=[order.pk]))
        self.assertEqual(response.status_code, 400)

    def test_wrong_method_is_405(self):
        response = self.client.delete(reverse("orders"))
        self.assertEqual(response.status_code, 405)