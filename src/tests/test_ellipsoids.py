"""Unit tests for ellipsoids.py."""
import pytest


def test_get_reference_ellipsoid():
    from orekitfactory.factory import get_reference_ellipsoid
    from org.orekit.models.earth import ReferenceEllipsoid
    from org.orekit.data import DataContext
    from org.orekit.utils import IERSConventions

    context = DataContext.getDefault()

    itrf = context.getFrames().getITRF(IERSConventions.IERS_2010, False)
    simpleItrf = context.getFrames().getITRF(IERSConventions.IERS_2010, True)

    # verify none
    with pytest.raises(ValueError):
        assert get_reference_ellipsoid(model=None) is None

    # verify default
    wgs84 = get_reference_ellipsoid()
    assert itrf == wgs84.getFrame()

    # verify simple EOP frame
    assert simpleItrf == get_reference_ellipsoid(simpleEop=True).getFrame()

    # verify iers-2010
    for model in ("iers2010", "iers-2010", "2010"):
        iers = get_reference_ellipsoid(model=model)
        expected = ReferenceEllipsoid.getIers2010(itrf)

        assert iers.getA() == expected.getA()
        assert iers.getFrame() == expected.getFrame()
        assert iers.getB() == expected.getB()

    # verify iers-2003
    for model in ("iers2003", "iers-2003", "2003"):
        iers = get_reference_ellipsoid(model=model)
        expected = ReferenceEllipsoid.getIers2003(itrf)

        assert iers.getA() == expected.getA()
        assert iers.getFrame() == expected.getFrame()
        assert iers.getB() == expected.getB()

    # verify iers-1996
    for model in ("iers1996", "iers-1996", "1996", "96", "iers-96", "iers96"):
        iers = get_reference_ellipsoid(model=model)
        expected = ReferenceEllipsoid.getIers96(itrf)

        assert iers.getA() == expected.getA()
        assert iers.getFrame() == expected.getFrame()
        assert iers.getB() == expected.getB()

    # verify unknown model
    with pytest.raises(ValueError):
        get_reference_ellipsoid(model="yellowbeard the pirate")
