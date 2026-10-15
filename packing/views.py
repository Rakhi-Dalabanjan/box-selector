import json

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import Order, OrderItem, Product
from .services import recommend_box

MAX_QUANTITY = 1000  # guards against huge quantities being expanded into units


def _error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def _is_int(value):
    # bool is a subclass of int in Python, so True would otherwise pass
    return isinstance(value, int) and not isinstance(value, bool)


def _serialize_order(order):
    return {
        "id": order.pk,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
            }
            for item in order.items.all()
        ],
    }


def _get_order(order_id):
    try:
        return Order.objects.prefetch_related("items__product").get(pk=order_id)
    except Order.DoesNotExist:
        return None


def _parse_items(payload):
    """Return (list of (product_id, quantity), None) or (None, error message)."""
    if not isinstance(payload, dict):
        return None, 'Body must be a JSON object like {"items": [...]}.'
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return None, '"items" must be a non-empty list.'

    parsed, seen = [], set()
    for entry in items:
        if not isinstance(entry, dict):
            return None, "Each item must be an object."
        product_id, quantity = entry.get("product_id"), entry.get("quantity")
        if not _is_int(product_id) or not _is_int(quantity):
            return None, "product_id and quantity must be integers."
        if not 1 <= quantity <= MAX_QUANTITY:
            return None, f"quantity must be between 1 and {MAX_QUANTITY}."
        if product_id in seen:
            return None, f"Product {product_id} is listed twice; combine it into one item."
        seen.add(product_id)
        parsed.append((product_id, quantity))
    return parsed, None


@csrf_exempt
@require_http_methods(["GET", "POST"])
def orders(request):
    if request.method == "GET":
        queryset = Order.objects.prefetch_related("items__product").order_by("-id")
        return JsonResponse({"orders": [_serialize_order(o) for o in queryset]})

    # POST: create
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error("Body is not valid JSON.")

    parsed, problem = _parse_items(payload)
    if problem:
        return _error(problem)

    products = Product.objects.in_bulk([pid for pid, _ in parsed])
    missing = [pid for pid, _ in parsed if pid not in products]
    if missing:
        return _error(f"Unknown product id(s): {missing}")

    try:
        with transaction.atomic():  # all-or-nothing: no half-built orders
            order = Order.objects.create()
            for pid, quantity in parsed:
                item = OrderItem(order=order, product=products[pid], quantity=quantity)
                item.full_clean()  # runs the model validators
                item.save()
    except ValidationError as exc:
        return _error(exc.message_dict)

    return JsonResponse(_serialize_order(_get_order(order.pk)), status=201)


@require_GET
def order_detail(request, order_id):
    order = _get_order(order_id)
    if order is None:
        return _error("Order not found.", 404)
    return JsonResponse(_serialize_order(order))


@require_GET
def order_recommendation(request, order_id):
    order = _get_order(order_id)
    if order is None:
        return _error("Order not found.", 404)
    try:
        box = recommend_box(order)
    except ValueError as exc:  # e.g. an order with no items (possible via admin)
        return _error(str(exc))

    if box is None:
        return JsonResponse(
            {"order_id": order.pk, "box": None, "message": "No box fits this order."}
        )
    return JsonResponse(
        {
            "order_id": order.pk,
            "box": {
                "id": box.pk,
                "name": box.name,
                "inner_dimensions_mm": [box.inner_length, box.inner_width, box.inner_height],
                "max_weight_g": box.max_weight,
                "cost": str(box.cost),  # string keeps the Decimal exact
            },
        }
    )

@require_GET
def products(request):
    data = [
        {
            "id": p.pk,
            "name": p.name,
            "dimensions_mm": [p.length, p.width, p.height],
            "weight_g": p.weight,
        }
        for p in Product.objects.order_by("name")
    ]
    return JsonResponse({"products": data})

    