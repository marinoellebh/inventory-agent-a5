from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .models import Item

CENT = Decimal("0.01")


def item_data(item):
    return {"name": item.name, "quantity": item.quantity, "price": str(item.price)}


def check_stock(name):
    """Look up how many of an item we have."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    return item_data(item)


def list_items():
    """Return every item in the inventory."""
    items = Item.objects.all()
    return {"items": [item_data(i) for i in items]}


def add_item(name, quantity):
    """Create a new item, or add to an existing one's stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is not None:
        item.quantity += quantity
        item.save()
        return {**item_data(item), "created": False}
    item = Item.objects.create(name=name, quantity=quantity)
    return {**item_data(item), "created": True}


def remove_stock(name, quantity):
    """Take a quantity out of stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    if quantity > item.quantity:
        return {
            "error": f"Cannot remove {quantity}. Only {item.quantity} in stock.",
            "name": item.name,
            "quantity": item.quantity,
        }
    item.quantity -= quantity
    item.save()
    return item_data(item)


def delete_item(name):
    """Remove an item from the inventory entirely."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    item.delete()
    return {"deleted": name}


def set_item_price(name, price):
    """Set a nonnegative unit price without changing stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    try:
        amount = Decimal(str(price))
        if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        return {"error": "Price must be a nonnegative amount with at most two decimal places."}
    if amount >= Decimal("100000000"):
        return {"error": "Price is too large."}
    item.price = amount
    item.save(update_fields=["price"])
    return item_data(item)


def calculate_total(name, quantity, vat_percent=0):
    """Calculate a quote from the stored unit price; never change stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return {"error": "Quantity must be a positive whole number."}
    try:
        rate = Decimal(str(vat_percent))
        if not rate.is_finite() or rate < 0 or rate > 100:
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        return {"error": "VAT percent must be between 0 and 100."}
    subtotal = item.price * quantity
    vat = (subtotal * rate / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    return {
        **item_data(item), "requested_quantity": quantity,
        "subtotal": str(subtotal.quantize(CENT)), "vat_percent": str(rate),
        "vat_amount": str(vat), "total": str((subtotal + vat).quantize(CENT)),
        "in_stock": quantity <= item.quantity,
    }


TOOL_DECLARATIONS = [
    {
        "type": "function",
        "name": "calculate_total",
        "description": "Calculate the cost of a requested quantity using the item's stored unit price, optionally adding VAT. Use for all total-cost and VAT questions; this does not sell or remove stock. vat_percent=10 means 10% VAT.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The item's name, e.g. 'Chocolate bar'."},
                "quantity": {"type": "integer", "description": "Number of units to price."},
                "vat_percent": {"type": "number", "description": "VAT percentage, e.g. 10 for 10%. Omit if none requested."},
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "set_item_price",
        "description": "Set or update the stored unit price of an existing item. Use only when the user asks to change its price.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The existing item's name."},
                "price": {"type": "number", "description": "Nonnegative unit price with no more than two decimal places."},
            },
            "required": ["name", "price"],
        },
    },
    {
        "type": "function",
        "name": "check_stock",
        "description": "Look up the current quantity and unit price of a single item in the inventory. Use this for questions about stock or unit price.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "list_items",
        "description": "Return every item in the inventory with its quantity and unit price. Use this when the user asks what is in stock generally, or asks for a list, rather than about one specific item.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "add_item",
        "description": "Add stock to the inventory. If the item does not exist it is created; if it already exists the quantity is added to the existing total. Use this for restocking and for new deliveries.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to add. Must be positive.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "remove_stock",
        "description": "Reduce the quantity of an existing item. Use this when items are sold, shipped or used. This does NOT delete the item; it only lowers the number.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to remove. Must be positive.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "delete_item",
        "description": "Permanently remove an item and its record from the inventory entirely. This is destructive. Only use it when the user clearly wants the item gone, not when they want to reduce its quantity.",
        "parameters": {
            "type": "object",
            "properties": {

                "name": {
                    "type": "string",
                    "description": "The name of the item to delete.",
                },
            },
            "required": ["name"],
        },
    },
]

TOOL_FUNCTIONS = {
    "calculate_total": calculate_total,
    "set_item_price": set_item_price,
    "check_stock": check_stock,
    "list_items": list_items,
    "add_item": add_item,
    "remove_stock": remove_stock,
    "delete_item": delete_item,
}
