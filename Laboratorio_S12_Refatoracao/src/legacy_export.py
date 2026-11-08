def export_customer_history(customer, orders):
    lines = []
    header = "CUSTOMER;" + customer.name.upper() + ";" + customer.plan
    lines.append(header)

    total_orders = 0
    total_value = 0.0
    for order in orders:
        total_orders += 1
        order_total = 0.0
        for item in order.items:
            order_total += item.price * item.qty
        total_value += order_total
        lines.append(
            "ORDER;"
            + str(total_orders)
            + ";"
            + customer.name.upper()
            + ";"
            + str(round(order_total, 2))
        )

    lines.append("SUMMARY;" + str(total_orders) + ";" + str(round(total_value, 2)))
    return "\n".join(lines)
