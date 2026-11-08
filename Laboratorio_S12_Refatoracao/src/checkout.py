def checkout(order):
    subtotal = 0.0
    for item in order.items:
        subtotal += item.price * item.qty
    subtotal = round(subtotal, 2)

    if order.customer.plan == "GOLD":
        discount = round(subtotal * 0.10, 2)
    elif order.customer.plan == "SILVER":
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

    if shipping == 0.0:
        message = f"{order.customer.name}: frete grátis | total R$ {total:.2f}"
    else:
        message = f"{order.customer.name}: frete R$ {shipping:.2f} | total R$ {total:.2f}"

    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "tax": tax,
        "total": total,
        "message": message,
    }
