"""Factory for date/time objects."""
from datetime import datetime

from org.orekit.data import DataContext
from org.orekit.time import AbsoluteDate, DateTimeComponents, TimeScale


def to_absolute_date(
    value: str | datetime | AbsoluteDate,
    context: DataContext | None = None,
    timescale: TimeScale | None = None,
) -> AbsoluteDate:
    """Convert the provided value to an AbsoluteDate instance.

    Args:
        value (str|datetime|AbsoluteDate|None): The value to convert.
        context (DataContext, optional): The data context from where the default UTC
        time scale will be retrieved, if necessary. If None, the default context will
        be used. Defaults to None.
        timescale (TimeScale, optional): The timescale in which a datetime or string
        instance should be created. If None, UTC will be used. Defaults to None.

    Raises:
        ValueError: When an invalid parameter type is provided for the `value` arg.

    Returns:
        AbsoluteDate: The date of the instance.
    """
    if context is None:
        context = DataContext.getDefault()

    if value is None or isinstance(value, AbsoluteDate):
        return value
    elif isinstance(value, datetime):
        return AbsoluteDate(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second + value.microsecond / 1000000.0,
            timescale or context.getTimeScales().getUTC(),
        )
    elif isinstance(value, str):
        return AbsoluteDate(
            DateTimeComponents.parseDateTime(value),
            timescale or context.getTimeScales().getUTC(),
        )
    else:
        raise ValueError(
            "Cannot create AbsoluteDate from value type: " + str(type(value))
        )


def try_absolutedate(
    value: str | datetime | AbsoluteDate,
    context: DataContext | None = None,
    timescale: TimeScale | None = None,
) -> AbsoluteDate:
    """Convert the provided value to an AbsoluteDate instance.

    Args:
        value (str|datetime|AbsoluteDate|None): The value to convert.
        context (DataContext, optional): The data context from where the default UTC
        time scale will be retrieved, if necessary. If None, the default context will
        be used. Defaults to None.
        timescale (TimeScale, optional): The timescale in which a datetime or string
        instance should be created. If None, UTC will be used. Defaults to None.

    Returns:
        AbsoluteDate|None: The date of the instance, or None if a conversion cannot be
        performed.
    """
    try:
        return to_absolute_date(value, context=context, timescale=timescale)
    except:  # noqa: E722
        return None
