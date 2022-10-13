import astropy.units as units

from org.orekit.data import DataContext
from org.orekit.frames import Frame
from org.orekit.orbits import KeplerianOrbit, Orbit, OrbitType, PositionAngle
from org.orekit.propagation.analytical.tle import TLE
from org.orekit.time import AbsoluteDate
from org.orekit.utils import Constants

from .dates import to_absolute_date
from ..utils import validate_quantity
from .frames import get_frame


def to_orbit_type(value: OrbitType | str) -> OrbitType:
    """Convert a string to an orekit OrbitType.

    This method is a no-op when an OrbitType is provided.

    Args:
        value (OrbitType | str): The input data to convert.

    Returns:
        OrbitType: The orbit type

    Raises:
        If `value` is not a str or OrbitType
        If `value` is a string but cannot be converted.
    """
    if value is None:
        return None
    elif isinstance(value, OrbitType):
        return value
    else:
        return OrbitType.valueOf(value.upper())


def check_tle(line1: str, line2: str) -> bool:
    """Check whether the TLE lines are correctly formatted.

    Args:
        line1 (str): The first line.
        line2 (str): The second line.

    Returns:
        bool: True when the format is ok, False othewise.
    """
    return TLE.isFormatOK(line1, line2)


def to_tle(line1: str, line2: str, context: DataContext = None) -> TLE:
    """
    Build a TLE from the input lines.

    Args:
        line1 (str): Line 1 of the TLE
        line2 (str): Line 2 of the TLE
        context (DataContext, optional): Data context to use when building, the default
        will be used if not provided. Defaults to None.

    Returns:
        TLE: The TLE object
    """
    if context is None:
        context = DataContext.getDefault()

    utc = context.getTimeScales().getUTC()

    return TLE(line1, line2, utc)


def to_orbit(
    a: units.Quantity[units.m] | float | str,
    e: float,
    i: units.Quantity[units.rad] | float | str,
    omega: units.Quantity[units.rad] | float | str,
    w: units.Quantity[units.rad] | float | str,
    epoch: str | AbsoluteDate,
    frame: Frame | str = None,
    v: units.Quantity[units.rad] | float | str | None = None,
    m: units.Quantity[units.rad] | float | str | None = None,
    context: DataContext = None,
    mu: units.Quantity[units.m**3 / units.s**2] | float | str = None,
    **kwargs
) -> Orbit:
    """
    Build an orbit from the provided values.

    Args:
        a (u.Quantity[u.m]|float|str): The semi-major axis of the orbit, as a distance
        quantity, string parsable by astropy.units.Quantity, or a number. If a number,
        must be in kilometers.
        e (Any): The orbital eccentricity.
        i (Any): The inclination of the orbit, as an angular quantity, string parsable
        by astropy.units.Quantity, or a number. If a number, must be in degrees.
        omega (Any): The right ascension of ascending node of the orbit, as an angular
        Quantity, string parsable by astropy.units.Quantity, or a number. If a number,
        must be in degrees.
        w (Any): The perigee argument of the orbit, as an angular Quantity, string
        parsable by astropy.units.Quantity, or a number. If a number, must be in
        degrees.
        epoch (str): epoch time as an ISO-8601 string
        frame (str, optional): Frame in which the orbit is defined. Valid values are
        GCRF or EME2000. If None, gcrf will be used. Defaults to None.
        v (Any, optional): Orbital true anomaly as a number in radians, or a string
        parsable by astropy.units.Quantity. Defaults to None.
        m (Any, optional): Orbital mean anomaly as a number in radians, or a string
        parsable by astropy.units.Quantity.. Defaults to None.
        context (DataContext, optional): Data context to use when building, the default
        will be used if not provided. Defaults to None.
        mu (float, optional): Central body attraction coefficient. If unspecified the
        earth's WGS-84 constant is used. Defaults to None.

    Raises:
        ValueError: when a required parameter is unspecified or specified but cannot be
        parsed

    Returns:
        Orbit: The orbit.
    """
    # TODO: handle EquinoctialOrbit and CircularOrbit construction
    if context is None:
        context = DataContext.getDefault()

    if mu is None:
        mu = validate_quantity(Constants.WGS84_EARTH_MU, units.m**3 / units.s**2)
    else:
        mu = validate_quantity(mu, units.m**3 / units.s**2)

    # ensure arguments are quantities
    a: units.Quantity = validate_quantity(a, units.km)
    i: units.Quantity = validate_quantity(i, units.deg)
    omega: units.Quantity = validate_quantity(omega, units.deg)
    w: units.Quantity = validate_quantity(w, units.deg)

    if v is not None:
        type = PositionAngle.TRUE
        anom = validate_quantity(v, units.deg)
    elif m is not None:
        type = PositionAngle.MEAN
        anom = validate_quantity(m, units.deg)
    else:
        raise ValueError("either true or mean anomaly must be specified")

    if frame is None:
        frame = context.getFrames().getGCRF()
    elif isinstance(frame, str):
        frame = get_frame(frame, context=context, **kwargs)
    elif not isinstance(frame, Frame):
        raise ValueError(
            "Argument for `frame` is not None, a Frame instance, or a str instance."
        )

    epoch: AbsoluteDate = to_absolute_date(epoch, context=context)
    return KeplerianOrbit(
        float(a.to_value(unit=units.m)),
        float(e),
        float(i.to_value(unit=units.rad)),
        float(w.to_value(unit=units.rad)),
        float(omega.to_value(unit=units.rad)),
        float(anom.to_value(unit=units.rad)),
        type,
        frame,
        epoch,
        float(mu.to_value(unit=units.m**3 / units.s**2)),
    )
