"""Unit tests for dates.py."""

import pytest

from datetime import datetime as dt, timedelta


def test_str_to_absolutedate():
    """Verify creation of absolute dates."""
    from orekitfactory.factory import to_absolute_date

    from org.orekit.data import DataContext

    context = DataContext.getDefault()
    utc = DataContext.getDefault().getTimeScales().getUTC()

    dt1 = dt.fromisoformat("2022-08-28T13:15:00")

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:15:00Z", context=context)
    date3 = to_absolute_date("2022-08-28T13:15:00Z", timescale=utc)
    date4 = to_absolute_date(dt1)
    date5 = to_absolute_date(dt1, context=context)
    date6 = to_absolute_date(dt1, timescale=utc)

    assert date1 is to_absolute_date(date1)
    assert date1.equals(date2)
    assert date1.equals(date3)
    assert date1.equals(date4)
    assert date1.equals(date5)
    assert date1.equals(date6)

    assert "2022-08-28T13:15:00.000Z" == date1.toString()

    with pytest.raises(ValueError):
        to_absolute_date(123456)


def test_interval():
    """Verify the DateInterval."""
    from orekitfactory.factory import to_absolute_date
    from orekitfactory.time import DateInterval

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:16:00Z")
    date3 = to_absolute_date("2022-08-28T13:17:00Z")
    date4 = to_absolute_date("2022-08-28T13:18:00Z")

    ivl1 = DateInterval(date1, date3)
    ivl2 = DateInterval(date2, date4)

    # verify properties
    assert date1.equals(ivl1.start)
    assert date3.equals(ivl1.stop)
    assert 120 == ivl1.duration_secs
    assert timedelta(minutes=2) == ivl1.duration

    # verify to list/tuples
    assert ivl1.to_tuple()[0].equals(date1)
    assert ivl1.to_tuple()[1].equals(date3)
    assert ivl1.to_list()[0].equals(date1)
    assert ivl1.to_list()[1].equals(date3)

    # verify padding
    ivl3 = ivl1.pad(60)
    ivl4 = ivl1.pad(timedelta(seconds=60))

    assert date1.shiftedBy(-60.0).equals(ivl3.start)
    assert date3.shiftedBy(60.0).equals(ivl3.stop)
    assert ivl3 == ivl4

    ivl5 = ivl1.pad(-60)
    assert 0.0 == ivl5.duration_secs

    with pytest.raises(ValueError):
        ivl1.pad(-120)

    # verify backwards construction
    ivl6 = DateInterval(date3, date1)
    assert ivl1 == ivl6

    # verify containment
    assert not ivl1.contains(None)
    assert ivl3.contains(ivl1)
    assert not ivl1.contains(ivl3)

    assert not ivl1.contains(ivl1)  # False because end isn't contained
    assert ivl1.contains(ivl1.start)
    assert not ivl1.contains(ivl1.start, startInclusive=False)

    assert not ivl1.contains(ivl1.stop)
    assert ivl1.contains(ivl1.stop, stopInclusive=True)

    with pytest.raises(ValueError):
        ivl1.contains("yellowbeard the pirate")

    # verify overlaps
    assert not ivl1.overlaps(None)
    assert ivl1.overlaps(ivl1)
    assert ivl1.overlaps(ivl2)
    assert not ivl1.overlaps(DateInterval(date3, date4))
    assert ivl1.overlaps(DateInterval(date3, date4), stopInclusive=True)
    assert not ivl1.overlaps(DateInterval(date4, date4.shiftedBy(60.0)))

    # verify union
    assert DateInterval(date1, date4) == ivl1.union(ivl2)
    assert DateInterval(date1, date4) == ivl2.union(ivl1)

    # verify intersect
    assert DateInterval(date2, date3) == ivl1.intersect(ivl2)
    assert ivl1.intersect(DateInterval(date4, date4.shiftedBy(60.0))) is None

    # verify strictly before
    assert not ivl1.strictly_before(None)
    assert not ivl1.strictly_before(ivl2)
    assert ivl1.strictly_before(DateInterval(date4, date4.shiftedBy(60.0)))
    assert ivl1.strictly_before(date4)
    with pytest.raises(ValueError):
        ivl1.strictly_before("yellowbeard the pirate")

    # verify strictly after
    assert not ivl2.strictly_after(None)
    assert not ivl2.strictly_after(ivl1)
    assert ivl2.strictly_after(date1)
    assert ivl2.strictly_after(DateInterval(date1, date1.shiftedBy(10.0)))

    with pytest.raises(ValueError):
        ivl2.strictly_after("yellowbeard the pirate")

    # verify comparisons
    assert not ivl1 < None
    assert ivl1 > None
    assert ivl1 is not None
    assert ivl1 < ivl2
    assert ivl2 > ivl1
    assert DateInterval(date1, date2) < ivl1
    assert DateInterval(date1, date3) == ivl1

    # verify to-string
    assert "[2022-08-28T13:15:00.000Z, 2022-08-28T13:17:00.000Z]" == str(ivl1)


def test_interval_list():
    """Tests verifying the DateIntervalList."""
    from orekitfactory.factory import to_absolute_date
    from orekitfactory.time import DateInterval, DateIntervalList

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:16:00Z")
    date3 = to_absolute_date("2022-08-28T13:17:00Z")
    date4 = to_absolute_date("2022-08-28T13:18:00Z")
    date5 = to_absolute_date("2022-08-28T13:19:00Z")

    ivl1 = DateInterval(date1, date3)
    ivl2 = DateInterval(date2, date4)
    ivl3 = DateInterval(date1, date2)

    list1 = DateIntervalList(interval=ivl1)

    # check construction
    assert 0 == len(DateIntervalList())
    assert ivl1 == list1.span
    assert 1 == len(list1)
    assert ivl1 == list1[0]

    list2 = DateIntervalList(intervals=[ivl1, ivl2])
    assert 1 == len(list2)
    assert DateInterval(date1, date4) == list2.span

    list3 = DateIntervalList(intervals=[ivl1, ivl2], reduce_input=False)
    assert 2 == len(list3)

    # test containment
    assert list1.contains(ivl3)
    assert not list1.contains(date4)
    assert not DateIntervalList(interval=ivl3).contains(DateInterval(date4, date5))
    assert not DateIntervalList(interval=DateInterval(date4, date5)).contains(ivl3)
    assert not list1.contains(ivl2)

    for ivl in list1:
        assert ivl == ivl1

    # test list of multiple sizes
    list4 = DateIntervalList(intervals=[ivl1, ivl3, DateInterval(date4, date5)])
    assert 2 == len(list4)

    assert (
        "[[2022-08-28T13:15:00.000Z, 2022-08-28T13:17:00.000Z], [2022-08-28T13:18:00.000Z, 2022-08-28T13:19:00.000Z]]"  # noqa: E501
        == str(list4)
    )


def test_list_union():
    """Tests verifying the DateIntervalList union operation."""
    from orekitfactory.factory import to_absolute_date
    from orekitfactory.time import (
        DateInterval,
        DateIntervalList,
        list_union,
    )

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:16:00Z")
    date3 = to_absolute_date("2022-08-28T13:17:00Z")
    date4 = to_absolute_date("2022-08-28T13:18:00Z")
    date5 = to_absolute_date("2022-08-28T13:19:00Z")
    date6 = to_absolute_date("2022-08-28T13:20:00Z")

    ivl1 = DateInterval(date1, date3)

    list1 = DateIntervalList(intervals=(ivl1, DateInterval(date2, date3)))
    list2 = DateIntervalList(
        intervals=(DateInterval(date3, date4), DateInterval(date5, date6))
    )

    with pytest.raises(ValueError):
        list_union("yellowbeard", list1)

    union1 = list_union(ivl1, list2)
    assert DateInterval(date1, date6) == union1.span
    assert 2 == len(union1)
    assert DateInterval(date1, date4) == union1[0]
    assert DateInterval(date5, date6) == union1[1]


def test_list_intersection():
    """Tests verifying DateIntervalList intersection operation."""
    from orekitfactory.factory import to_absolute_date
    from orekitfactory.time import (
        DateInterval,
        DateIntervalList,
        list_intersection,
    )

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:16:00Z")
    date3 = to_absolute_date("2022-08-28T13:17:00Z")
    date4 = to_absolute_date("2022-08-28T13:18:00Z")
    date5 = to_absolute_date("2022-08-28T13:19:00Z")
    date6 = to_absolute_date("2022-08-28T13:20:00Z")

    list1 = DateIntervalList(
        intervals=(DateInterval(date1, date3), DateInterval(date2, date3))
    )
    list2 = DateIntervalList(
        intervals=(DateInterval(date3, date4), DateInterval(date5, date6))
    )

    int1 = list_intersection(
        list1,
        (DateInterval(date3, date4), DateInterval(date5, date6)),
        allow_zero_length=True,
    )
    assert 1 == len(int1)
    assert DateInterval(date3, date3) == int1[0]

    int2 = list_intersection(list2, list1, allow_zero_length=False)
    assert 0 == len(int2)


def test_list_compliment():
    """Tests verifying DateIntervalList list compliment."""
    from orekitfactory.factory import to_absolute_date
    from orekitfactory.time import DateInterval, DateIntervalList, list_compliment

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:16:00Z")
    date3 = to_absolute_date("2022-08-28T13:17:00Z")
    date4 = to_absolute_date("2022-08-28T13:18:00Z")
    date5 = to_absolute_date("2022-08-28T13:19:00Z")
    date6 = to_absolute_date("2022-08-28T13:20:00Z")

    list = DateIntervalList(
        intervals=(DateInterval(date2, date3), DateInterval(date4, date5))
    )

    comp1 = list_compliment(list)
    assert 1 == len(comp1)
    assert DateInterval(date3, date4) == comp1[0]

    comp2 = list_compliment(list, span=DateInterval(date1, date6))
    assert 3 == len(comp2)
    assert DateInterval(date1, date2) == comp2[0]
    assert DateInterval(date3, date4) == comp2[1]
    assert DateInterval(date5, date6) == comp2[2]


def test_list_subtract():
    """Tests verifying DateIntervalList subtraction."""
    from orekitfactory.factory import to_absolute_date
    from orekitfactory.time import (
        DateInterval,
        DateIntervalList,
        list_subtract,
    )

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:16:00Z")
    date3 = to_absolute_date("2022-08-28T13:17:00Z")
    date4 = to_absolute_date("2022-08-28T13:18:00Z")
    date5 = to_absolute_date("2022-08-28T13:19:00Z")
    date6 = to_absolute_date("2022-08-28T13:20:00Z")

    list = DateIntervalList(
        intervals=(DateInterval(date2, date3), DateInterval(date4, date5))
    )
    result = list_subtract(DateIntervalList(interval=DateInterval(date1, date6)), list)

    assert 3 == len(result)
    assert DateInterval(date1, date2) == result[0]
    assert DateInterval(date3, date4) == result[1]
    assert DateInterval(date5, date6) == result[2]


def test_list_builder():
    """Tests verifying the list builder."""
    from orekitfactory.factory import to_absolute_date
    from orekitfactory.time import (
        DateInterval,
        DateIntervalListBuilder,
    )

    date1 = to_absolute_date("2022-08-28T13:15:00Z")
    date2 = to_absolute_date("2022-08-28T13:16:00Z")
    date3 = to_absolute_date("2022-08-28T13:17:00Z")
    date4 = to_absolute_date("2022-08-28T13:18:00Z")
    date6 = to_absolute_date("2022-08-28T13:20:00Z")

    # verify no bound, base case
    builder = DateIntervalListBuilder()
    with pytest.raises(ValueError):
        builder.add_stop(date1)

    builder.add_start(date2)

    with pytest.raises(ValueError):
        builder.add_start(date3)

    builder.add_stop(date3)

    with pytest.raises(ValueError):
        builder.add_stop(date4)

    list = builder.build_list()
    assert 1 == len(list)
    assert DateInterval(date2, date3) == list[0]

    # verify with bounds
    builder = DateIntervalListBuilder(start=date1, stop=date6)
    builder.add_stop(date2)
    builder.add_start(date3)
    builder.add_stop(date4)
    builder.add_start(date6)
    list = builder.build_list()

    assert 3 == len(list)
