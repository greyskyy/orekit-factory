from org.orekit.utils import IERSConventions


def to_iers_conventions(s: str, default: str = None) -> IERSConventions:
    """Convert a string to an iers convetions.

    The IERS conventions, as defined by Orekit are IERS_2010, IERS_2003, and IERS_1996.
    This method converts the following strings, regardless of case:
        - iers_2010, iers-2010, iers2010, 2010 all convert to the IERS_2010 convention
        - iers_2003, iers-2003, iers2003, 2003 all convert to the IERS_2003 convention
        - iers_1996, iers-1996, iers1996, 1996 all convert to the IERS_1996 convention

    Args:
        s (str): The string to convert
        default (str, optional): The default to use if s is None. Defaults to None.

    Raises:
        ValueError: Triggered when the string cannot be converted

    Returns:
        IERSConventions: The convention
    """
    if s is None and default is None:
        return None

    safe = s or default
    lsafe = safe.lower()

    if (
        lsafe == "iers_2010"
        or lsafe == "iers-2010"
        or lsafe == "iers2010"
        or lsafe == "2010"
    ):
        return IERSConventions.IERS_2010
    elif (
        lsafe == "iers_2003"
        or lsafe == "iers-2003"
        or lsafe == "iers2003"
        or lsafe == "2003"
    ):
        return IERSConventions.IERS_2003
    elif (
        lsafe == "iers_1996"
        or lsafe == "iers-1996"
        or lsafe == "iers1996"
        or lsafe == "1996"
    ):
        return IERSConventions.IERS_1996
    else:
        raise ValueError(f"Invalid iers convention string {s}")
