# Константы
TAX_RATE = 0.21
DEFAULT_CURRENCY = "USD"

# Купоны
SAVE10_RATE = 0.10

SAVE20_FULL_RATE = 0.20
SAVE20_MIN_RATE = 0.05
SAVE20_THRESHOLD = 200

VIP_FULL_DISCOUNT = 50
VIP_MIN_DISCOUNT = 10
VIP_THRESHOLD = 100


def parse_request(request: dict):
    """Извлекает данные из запроса."""
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency", DEFAULT_CURRENCY)
    return user_id, items, coupon, currency


def validate_request(user_id, items):
    """Валидация обязательных полей и структуры."""
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")


def calculate_subtotal(items):
    """Подсчёт суммы без скидки."""
    return sum(item["price"] * item["qty"] for item in items)


def calculate_discount(coupon, subtotal):
    """Расчёт скидки по купону."""
    if coupon is None or coupon == "":
        return 0
    if coupon == "SAVE10":
        return int(subtotal * SAVE10_RATE)
    if coupon == "SAVE20":
        if subtotal >= SAVE20_THRESHOLD:
            return int(subtotal * SAVE20_FULL_RATE)
        return int(subtotal * SAVE20_MIN_RATE)
    if coupon == "VIP":
        discount = VIP_FULL_DISCOUNT
        if subtotal < VIP_THRESHOLD:
            discount = VIP_MIN_DISCOUNT
        return discount
    raise ValueError("unknown coupon")


def process_checkout(request: dict) -> dict:
    """Основная функция — теперь короткая и читается сверху вниз."""
    user_id, items, coupon, currency = parse_request(request)
    validate_request(user_id, items)

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(coupon, subtotal)

    total_after_discount = max(subtotal - discount, 0)
    tax = int(total_after_discount * TAX_RATE)
    total = total_after_discount + tax

    order_id = f"{user_id}-{len(items)}-X"

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
