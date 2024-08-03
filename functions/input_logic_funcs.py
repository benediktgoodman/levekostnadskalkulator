def ensure_range(value, min_value, max_value, min_range):
    lower, upper = value
    if upper - lower < min_range:
        if lower == min_value:
            upper = lower + min_range
        elif upper == max_value:
            lower = upper - min_range
        else:
            upper = min(max_value, lower + min_range)
    return (lower, upper)