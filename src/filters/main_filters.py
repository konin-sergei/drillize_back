def format_sum_accuracy_0(value):
    try:
        return f"{int(round(float(value), 0)):,}".replace(",", " ")
    except (ValueError, TypeError):
        return value
