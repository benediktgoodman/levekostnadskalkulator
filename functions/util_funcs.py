
def ensure_range(value, min_value, max_value, min_range):
    """
    Ensures that the range between the lower and upper values is at least the specified minimum range.

    Parameters
    ----------
    value : tuple[float, float]
        The range of values to be checked.
    min_value : float
        The minimum allowed value.
    max_value : float
        The maximum allowed value.
    min_range : float
        The minimum required range between the lower and upper values.

    Returns
    -------
    tuple[float, float]
        The adjusted range of values, ensuring the minimum range is met.

    """    
    lower, upper = value
    if upper - lower < min_range:
        if lower == min_value:
            upper = lower + min_range
        elif upper == max_value:
            lower = upper - min_range
        else:
            upper = min(max_value, lower + min_range)
    return (lower, upper)