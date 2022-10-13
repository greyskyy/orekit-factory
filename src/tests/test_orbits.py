"""Unit tests verifying orbits.py."""
import math
import astropy.units as u
import pytest

LINE_1 = "1 49260U 21088A   22166.94778099  .00000339  00000+0  85254-4 0  9992"
LINE_2 = "2 49260  98.2276 237.1831 0001142  78.2478 281.8849 14.57099002 38060"


def test_check_tle():
    from orekitfactory.factory import check_tle

    assert check_tle(LINE_1, LINE_2)
    assert not check_tle("yellowbeard the pirate", "edith the pirate ship")


def test_to_tle():
    from org.orekit.data import DataContext
    from orekitfactory.factory import to_tle

    context = DataContext.getDefault()
    utc = context.getTimeScales().getUTC()

    # check default context
    tle = to_tle(LINE_1, LINE_2)
    assert tle.getLine1() == LINE_1
    assert tle.getLine2() == LINE_2
    assert tle.getUtc().equals(utc)

    # check provided context
    tle = to_tle(LINE_1, LINE_2, context=context)
    assert tle.getLine1() == LINE_1
    assert tle.getLine2() == LINE_2
    assert tle.getUtc().equals(utc)


def test_to_orbit():
    from org.orekit.data import DataContext
    from org.orekit.utils import Constants
    from org.orekit.orbits import KeplerianOrbit
    from orekitfactory.factory import to_orbit

    context = DataContext.getDefault()

    # test with true anomaly
    orbit: KeplerianOrbit = to_orbit(
        a="7080 km",
        e=0.0008685,
        i=85,
        omega=u.Quantity("261.9642 deg"),
        w="257.7333 deg",
        epoch="2022-06-16T17:54:00Z",
        v=1.2,
    )
    assert orbit.getA() == 7080000
    assert orbit.getE() == 0.0008685
    assert orbit.getI() == math.radians(85)
    assert orbit.getRightAscensionOfAscendingNode() == math.radians(261.9642)
    assert orbit.getPerigeeArgument() == math.radians(257.7333)
    assert orbit.getTrueAnomaly() == math.radians(1.2)
    assert orbit.getMu() == Constants.WGS84_EARTH_MU
    assert orbit.getFrame().equals(context.getFrames().getGCRF())

    # test with mean anomaly
    orbit: KeplerianOrbit = to_orbit(
        a="7080 km",
        e=0.0008685,
        i=85,
        omega=u.Quantity("261.9642 deg"),
        w="257.7333 deg",
        epoch="2022-06-16T17:54:00Z",
        m=1.2,
        mu=Constants.EGM96_EARTH_MU,
        frame="j2000",
    )
    assert orbit.getA() == 7080000
    assert orbit.getE() == 0.0008685
    assert orbit.getI() == math.radians(85)
    assert orbit.getRightAscensionOfAscendingNode() == math.radians(261.9642)
    assert orbit.getPerigeeArgument() == math.radians(257.7333)
    assert orbit.getMeanAnomaly() == math.radians(1.2)
    assert orbit.getMu() == Constants.EGM96_EARTH_MU
    assert orbit.getFrame().equals(context.getFrames().getEME2000())

    # test with specified frame anomaly
    orbit: KeplerianOrbit = to_orbit(
        a="7080 km",
        e=0.0008685,
        i=85,
        omega=u.Quantity("261.9642 deg"),
        w="257.7333 deg",
        epoch="2022-06-16T17:54:00Z",
        m=1.2,
        mu=Constants.EGM96_EARTH_MU,
        frame=context.getFrames().getEME2000(),
    )
    assert orbit.getA() == 7080000
    assert orbit.getE() == 0.0008685
    assert orbit.getI() == math.radians(85)
    assert orbit.getRightAscensionOfAscendingNode() == math.radians(261.9642)
    assert orbit.getPerigeeArgument() == math.radians(257.7333)
    assert orbit.getMeanAnomaly() == math.radians(1.2)
    assert orbit.getMu() == Constants.EGM96_EARTH_MU
    assert orbit.getFrame().equals(context.getFrames().getEME2000())

    # test unspecified anomaly provides error
    with pytest.raises(ValueError):
        to_orbit(
            a="7080 km",
            e=0.0008685,
            i=85,
            omega=u.Quantity("261.9642 deg"),
            w="257.7333 deg",
            epoch="2022-06-16T17:54:00Z",
        )

    # test bad frame raises error
    with pytest.raises(ValueError):
        # test with specified frame anomaly
        to_orbit(
            a="7080 km",
            e=0.0008685,
            i=85,
            omega=u.Quantity("261.9642 deg"),
            w="257.7333 deg",
            epoch="2022-06-16T17:54:00Z",
            m=1.2,
            frame=[1, 2, 3, 4],
        )
