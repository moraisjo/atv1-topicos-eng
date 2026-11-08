def _calculate_subtotal(order):
    subtotal = 0.0
    for item in order.items:
        subtotal += item.price * item.qty
    return round(subtotal, 2)


def _calculate_checkout_amounts(subtotal, plan):
    if plan == "GOLD":
        discount = round(subtotal * 0.10, 2)
    elif plan == "SILVER":
        discount = round(subtotal * 0.05, 2)
    else:
        discount = 0.0

    after_discount = round(subtotal - discount, 2)

    if after_discount >= 150.0:
        shipping = 0.0
    else:
        shipping = 12.0

    taxable = round(after_discount + shipping, 2)
    tax = round(taxable * 0.18, 2)
    total = round(taxable + tax, 2)
    return discount, shipping, tax, total


def _format_checkout_message(customer_name, shipping, total):
    if shipping == 0.0:
        return f"{customer_name}: frete grátis | total R$ {total:.2f}"
    return f"{customer_name}: frete R$ {shipping:.2f} | total R$ {total:.2f}"


def checkout(order):
    subtotal = _calculate_subtotal(order)
    discount, shipping, tax, total = _calculate_checkout_amounts(
        subtotal, order.customer.plan
    )
    message = _format_checkout_message(order.customer.name, shipping, total)

    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "tax": tax,
        "total": total,
        "message": message,
    }
