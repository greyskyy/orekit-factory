"""Unit tests for propagator.py."""

import astropy.units as u
import pytest

LINE_1 = "1 49260U 21088A   22166.94778099  .00000339  00000+0  85254-4 0  9992"
LINE_2 = "2 49260  98.2276 237.1831 0001142  78.2478 281.8849 14.57099002 38060"


def test_invalid():
    """Verify general input error cases."""
    from orekitfactory.factory import to_propagator

    assert to_propagator(None) is None

    # testinvalid orbits throw exceptions
    with pytest.raises(ValueError):
        to_propagator("yellowbeard is a pirate, not an orbit")


def test_tle():
    """Verify construction of an SGP4 propgagor instance."""
    from orekitfactory.factory import to_propagator

    from org.orekit.attitudes import InertialProvider
    from org.orekit.data import DataContext
    from org.orekit.propagation.analytical.tle import TLE

    context = DataContext.getDefault()
    utc = context.getTimeScales().getUTC()

    tle = TLE(LINE_1, LINE_2, utc)

    prop = to_propagator(tle)
    assert 100 == prop.propagate(tle.getDate()).getMass()

    prop = to_propagator(
        tle,
        mass="250 g",
        attitudeProvider=InertialProvider.of(context.getFrames().getGCRF()),
        context=context,
    )
    assert 0.25 == prop.propagate(tle.getDate()).getMass()


def test_numerical():
    """Verify construction of numerical propagators."""
    from orekitfactory.factory import to_propagator
    from orekitfactory.factory import to_orbit

    orbit = to_orbit(
        a="7080 km",
        e=0.0008685,
        i=85,
        omega=u.Quantity("261.9642 deg"),
        w="257.7333 deg",
        epoch="2022-06-16T17:54:00Z",
        v=1.2,
    )

    # disable sun and planets, since that data isn't available in test
    prop = to_propagator(
        orbit,
        considerSolarPressure=False,
        considerAtmosphere=False,
        considerGravity=False,
        bodies=None,
    )
    assert 100 == prop.propagate(orbit.getDate()).getMass()
