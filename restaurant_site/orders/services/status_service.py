ALLOWED_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['preparing', 'cancelled'],
    'preparing': ['ready'],
    'ready': ['delivering'],
    'delivering': ['completed'],
}


def can_transition(old, new):
    return new in ALLOWED_TRANSITIONS.get(old, [])


def change_status(order, new_status):
    if not can_transition(order.status, new_status):
        raise ValueError(f"Invalid transition {order.status} → {new_status}")

    order.status = new_status
    order.save()

    return order