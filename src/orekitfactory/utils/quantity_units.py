import astropy.units as u


def validate_quantity(
    value: u.Quantity | float | str, float_unit: u.Unit
) -> u.Quantity:
    """Convert a value to a quantity, if necesary.

    Args:
        value (u.Quantity | float | str): The value to convert.
        float_unit (u.Unit): If a float, the unit to apply.

    Returns:
        u.Quantity: The parameter as a Quantity
    """
    if value is None:
        return None
    elif isinstance(value, u.Quantity):
        value.to
        return value
    elif isinstance(value, str):
        return u.Quantity(value)
    else:
        return value * float_unit
