"""Unit tests for frame.py."""

import pytest


def test_get_frame():
    """Verify retrieving the orekit frame based on string inputs."""
    from orekitfactory.factory import get_frame

    from org.orekit.data import DataContext
    from org.orekit.utils import IERSConventions

    context = DataContext.getDefault()

    # verify None raises an error
    with pytest.raises(ValueError):
        get_frame(None)

    # verify eme2000 / J2000
    eme2000 = context.getFrames().getEME2000()
    assert eme2000.equals(get_frame("j2000"))
    assert eme2000.equals(get_frame("J2000"))
    assert eme2000.equals(get_frame("eme2000"))
    assert eme2000.equals(get_frame("EME2000"))

    # verify GCRF / ECI
    gcrf = context.getFrames().getGCRF()
    assert gcrf.equals(get_frame("gcrf", context=context))
    assert gcrf.equals(get_frame("GCRF", context=context))
    assert gcrf.equals(get_frame("eci", context=context))
    assert gcrf.equals(get_frame("ECI", context=context))

    # verify ITRF
    itrf = context.getFrames().getITRF(IERSConventions.IERS_2010, True)
    assert itrf.equals(
        get_frame("itrf", context=context, iersConventions="2010", simpleEop=True)
    )
    assert itrf.equals(
        get_frame("ITRF", context=context, iersConventions="2010", simpleEop=True)
    )
    assert itrf.equals(
        get_frame("ecef", context=context, iersConventions="2010", simpleEop=True)
    )
    assert itrf.equals(
        get_frame("Ecef", context=context, iersConventions="2010", simpleEop=True)
    )
    assert itrf.equals(
        get_frame("ECF", context=context, iersConventions="2010", simpleEop=True)
    )
    assert itrf.equals(
        get_frame("ecf", context=context, iersConventions="2010", simpleEop=True)
    )

    # verify another predefined frame
    teme = context.getFrames().getTEME()
    assert teme.equals(get_frame("teme", context=context))
    assert teme.equals(get_frame("TEME", context=context))

    # verify unknown frame raises error
    with pytest.raises(ValueError):
        get_frame("yellowbeard the pirate")


def test_get_predefined():
    """Verify aspects of get_predefined not otherwise covered."""
    from orekitfactory.factory.frames import get_predefined

    with pytest.raises(ValueError):
        get_predefined(None)
