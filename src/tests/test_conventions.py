import pytest

"""Unit tests for the conventions.py mehtods."""


def test_convention():
    """Verify successful loading of the various conventions."""
    from orekitfactory.factory import to_iers_conventions
    from org.orekit.utils import IERSConventions

    for year in ("2010", "2003", "1996"):
        for s in (
            f"iers_{year}",
            f"IERS_{year}",
            f"iers-{year}",
            f"IERS-{year}",
            f"iers{year}",
            f"IERS{year}",
            year,
        ):
            assert IERSConventions.valueOf(f"IERS_{year}") == to_iers_conventions(
                s
            ), f"Failure! string '{s}' did not yield IERS_{year}"


def test_none():
    """Verify None returns None."""
    from orekitfactory.factory import to_iers_conventions

    assert to_iers_conventions(None) is None


def test_bad_value():
    """Verify the ValueError is raised."""
    from orekitfactory.factory import to_iers_conventions

    with pytest.raises(ValueError):
        to_iers_conventions("yellowbeard")
