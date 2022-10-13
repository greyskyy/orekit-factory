from collections import namedtuple
import datetime
import functools
from typing import Sequence

from orekit.pyhelpers import absolutedate_to_datetime

from org.orekit.data import DataContext
from org.orekit.time import AbsoluteDate

from ..factory import to_absolute_date

IntervalData = namedtuple("IntervalData", ("start", "stop"))


@functools.total_ordering
class DateInterval:
    """Interval of time."""

    def __init__(
        self,
        start: AbsoluteDate
        | datetime.datetime
        | Sequence[AbsoluteDate | datetime.datetime],
        stop: AbsoluteDate | datetime.datetime = None,
        context: DataContext = None,
    ):
        """Class constructor.

        Args:
            start (AbsoluteDate|datetime|array-like): The starting time, or (if
            array-like) a size-2 array holding the start and stop.
            stop (AbsoluteDate|datetime): The stopping time.
            context (DataContext, optional): If a convertion to AbsoluteDate
            is required, use this context. If None, the default context will be
            used. Defaults to None.
        """
        if isinstance(start, Sequence):
            if len(start) == 2:
                t0 = to_absolute_date(start[0], context=context)
                t1 = to_absolute_date(start[1], context=context)
            else:
                raise ValueError("Array-like parameter must be length = 2")
        elif stop is None:
            raise ValueError(
                "Either an array-like object for first parameter, or 2 positional "
                "parameters required to create a DateInterval"
            )
        else:
            t0 = to_absolute_date(start, context=context)
            t1 = to_absolute_date(stop, context=context)

        if t0.compareTo(t1) > 0:
            self.__data = IntervalData(t1, t0)
        else:
            self.__data = IntervalData(t0, t1)

    @property
    def start(self) -> AbsoluteDate:
        """Starting time of the interval.

        Returns:
            AbsoluteDate: The interval's starting time.
        """
        return self.__data[0]

    @functools.cached_property
    def start_dt(self) -> datetime.datetime:
        """Starting time of the interval.

        Returns:
            datetime: The interval's starting time.
        """
        return absolutedate_to_datetime(self.__data[0])

    @property
    def stop(self) -> AbsoluteDate:
        """Stopping time of the interval.

        Returns:
            AbsoluteDate: The interval's stop time
        """
        return self.__data[1]

    @functools.cached_property
    def stop_dt(self) -> datetime.datetime:
        """Stopping time of the interval.

        Returns:
            datetime: The interval's stop time
        """
        return absolutedate_to_datetime(self.__data[1])

    @functools.cached_property
    def duration_secs(self) -> float:
        """The duration of this interval, in floating point seconds.

        Returns:
            float: The duration, in seconds.
        """
        return self.stop.durationFrom(self.start)

    @functools.cached_property
    def duration(self) -> datetime.timedelta:
        """The duration as a `timedelta`.

        Returns:
            timedelta: The interval duration as a `timedelta`
        """
        return datetime.timedelta(seconds=self.duration_secs)

    @functools.cached_property
    def dt(self) -> tuple[datetime.datetime]:
        """This interval as a tuple of datetime objects.

        Returns:
            tuple[dt.datetime]: the tuple of `(start, stop)` as datetime objects.
        """
        return IntervalData(self.start_dt, self.stop_dt)

    def to_tuple(self) -> tuple[AbsoluteDate]:
        """Representation of this interval as a tuple of (start,stop).

        Returns:
            tuple[AbsoluteDate]: The resulting tuple.
        """
        return IntervalData(self.start, self.stop)

    def to_list(self) -> list[AbsoluteDate]:
        """Representations of this interval a list of [start,stop].

        Returns:
            list[AbsoluteDate]: The resulting list
        """
        return [self.start, self.stop]

    def pad(self, time: float | datetime.timedelta):
        """Increase the interval symmetrically by moving the start earlier and the stop
        later by the provided amount.

        The interval duration will increase by `2 * time`.

        Args:
            time (float | timedelta): The amount to pad each side. Specified as a float
            number of seconds or the timedelta duration.

        Returns:
            DateInterval: The new interval, padded.

        Raises:
            ValueError: When the pad negative and would result in a negative interval
            duration.
        """
        padSeconds = 0
        if isinstance(time, datetime.timedelta):
            padSeconds = time.total_seconds()
        elif time:
            padSeconds = float(time)

        if (2 * padSeconds) < -self.duration_secs:
            raise ValueError("Negative pad must be less than half the duration")

        return DateInterval(
            self.start.shiftedBy(-padSeconds), self.stop.shiftedBy(padSeconds)
        )

    def contains(
        self, other, startInclusive: bool = True, stopInclusive: bool = False
    ) -> bool:
        """Determine if this interval contains the provided time or interval.

        Args:
            other (AbsoluteDate|DateInterval|datetime): The date or interval to check
            for containment. May be any type coercable into an AbsoluteDate or
            DateInterval
            startInclusive (bool, optional): Whether the start of this interval is
            closed. Defaults to True.
            stopInclusive (bool, optional): Whether stop of this interval is closed.
            Defaults to False.

        Raises:
            TypeError: _description_

        Returns:
            bool: _description_
        """
        return is_contained_in(
            other,
            self.start,
            self.stop,
            startInclusive=startInclusive,
            stopInclusive=stopInclusive,
        )

    def overlaps(
        self, other, startInclusive: bool = True, stopInclusive: bool = False
    ) -> bool:
        """Determine if this list contains the other list or date.

        Args:
            other (DateInterval): The interval to check for overlap
            startInclusive (bool, optional): Whether this interval's start point should
            be considered in overlap. Defaults to True.
            stopInclusive (bool, optional): Whether this interval's stop point should
            be considered in overlap. Defaults to False.

        Returns:
            bool: True when the intervals overlap; False otherwise
        """
        v0 = 0 if startInclusive else -1
        v1 = 0 if stopInclusive else 1

        if other is None:
            return False

        other = as_dateinterval(other)

        return (
            self.start.compareTo(other.stop) <= v0
            and self.stop.compareTo(other.start) >= v1
        )

    def union(self, other):
        """Combine this interval with another interval as the earliest start to latest
        stop of the two intervals.
        Note that this will return a valid union even if the intervals are
        non-overlapping.

        Args:
            other (DateInterval): The other interval.

        Returns:
            DateInterval: An interval describing the earliest start to the latest stop.
        """
        other = as_dateinterval(other)

        t0 = self.start if self.start.compareTo(other.start) <= 0 else other.start
        t1 = self.stop if self.stop.compareTo(other.stop) >= 0 else other.stop

        return DateInterval(t0, t1)

    def intersect(self, other, endpoint_inclusive: bool = True):
        """Insersect this interval with another interval.

        Args:
            other (DateInterval): The other interval.
            endpoint_inclusive (bool, optional): Indicate whether intersection at only
            an endpoint may result in a True result.

        Returns:
            DateInterval|None: Return the interval of overlap betwen the two intervals,
            or None.
        """
        other = as_dateinterval(other)

        t0 = self.start if self.start.compareTo(other.start) >= 0 else other.start
        t1 = self.stop if self.stop.compareTo(other.stop) <= 0 else other.stop

        cmp = 1 if endpoint_inclusive else 0

        if t0.compareTo(t1) < cmp:
            return DateInterval(t0, t1)
        else:
            return None

    def strictly_before(self, other) -> bool:
        """Determine if this interval is strictly before the other date or interval.

        Args:
            other (AbsoluteDate|DateInterval): The other date or interval.

        Returns:
            bool: True when this interval is strictly before the other date or interval;
            False otherwise
        """
        return is_strictly_before(other, self.start, self.stop)

    def strictly_after(self, other) -> bool:
        """Determine if this interval is strictly after the other date or interval.

        Args:
            other (DateInterval): The other date or interval.

        Returns:
            bool: True when this interval is strictly after the other date or interval;
            False otherwise
        """
        return is_strictly_after(other, self.start, self.stop)

    def __len__(self):
        return len(self.__data)

    def __getitem__(self, i):
        return self.__data[i]

    def __lt__(self, other) -> bool:
        if other is None:
            return False

        rv = self.start.compareTo(other.start)
        if rv == 0:
            return self.stop.compareTo(other.stop) < 0
        else:
            return rv < 0

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.start.equals(other.start) and self.stop.equals(other.stop)

    def __str__(self) -> str:
        return f"[{self.start.toString()}, {self.stop.toString()}]"


def as_dateinterval(
    t0: None
    | DateInterval
    | AbsoluteDate
    | datetime.datetime
    | Sequence[AbsoluteDate | datetime.datetime],
    t1: None | AbsoluteDate | datetime.datetime = None,
) -> DateInterval:
    """Attempt to create an interval from the provided inputs.

    Args:
        t0 (None | DateInterval | AbsoluteDate | dt.datetime | Sequence[AbsoluteDate
        |  dt.datetime]): The interval start, or an array-like object holding the start
        and stop.
        t1 (None | AbsoluteDate | dt.datetime, optional): When `t0` is a scalar, the
        interval stop time. Defaults to None.

    Returns:
        DateInterval: The date interval.

    Raises:
        ValueError: when the parameters cannot be coerced into a date interval
    """
    if t0 is None:
        return None
    elif isinstance(t0, DateInterval):
        return t0
    else:
        return DateInterval(t0, t1)


def try_dateinterval(
    t0: None
    | DateInterval
    | AbsoluteDate
    | datetime.datetime
    | Sequence[AbsoluteDate | datetime.datetime],
    t1: None | AbsoluteDate | datetime.datetime = None,
) -> DateInterval:
    """Attempt to create an interval from the provided inputs.

    Args:
        t0 (None | DateInterval | AbsoluteDate | dt.datetime |
        Sequence[AbsoluteDate  |  dt.datetime]): The interval start, or an array-like
        object holding the start and stop.
        t1 (None | AbsoluteDate | dt.datetime, optional): When `t0` is a scalar,
        the interval stop time. Defaults to None.

    Returns:
        DateInterval|None: The date interval or None if it cannot be coverted.
    """
    try:
        return as_dateinterval(t0, t1)
    except:  # noqa: E722
        return None


def is_contained_in(
    other,
    start: AbsoluteDate,
    stop: AbsoluteDate,
    startInclusive: bool = True,
    stopInclusive: bool = False,
) -> bool:
    """Determine whether the other object is contained in the interval defined by
    [start, stop]

    Args:
        other (AbsoluteDate|DateInterval): The other object to check for containment.
        start (AbsoluteDate): The interval start time.
        stop (AbsoluteDate): The interval stop time.
        startInclusive (bool, optional): Indicate the the interval should be closed at
        the start. Defaults to True.
        stopInclusive (bool, optional): Indicate the interval should be closed at the
        stop. Defaults to False.

    Raises:
        ValueError: When the `other` parameter is not a valid type handled by this
        method.

    Returns:
        bool: True when contained, False otherwise.
    """
    v0 = 0 if startInclusive else -1
    v1 = 0 if stopInclusive else 1

    if other is None:
        return False
    elif isinstance(other, (DateInterval, Sequence)):
        other_ivl = as_dateinterval(other)
        return (
            start.compareTo(other_ivl.start) <= v0
            and stop.compareTo(other_ivl.stop) >= v1
        )
    else:
        other_date = to_absolute_date(other)
        return start.compareTo(other_date) <= v0 and stop.compareTo(other_date) >= v1


def is_strictly_before(other, start: AbsoluteDate, stop: AbsoluteDate) -> bool:
    """Determine whether the other object is strictly before the interval defined by
    the start, stop interval.

    Args:
        other (None|AbsoluteDate|DateInterval): The object to check.
        start (AbsoluteDate): Start of the interval to check against.
        stop (AbsoluteDate): Stop of the interval to check against.

    Raises:
        ValueError: When `other` is an unknown type (known types are:
        None|AbsoluteDate|DateInterval)

    Returns:
        bool: When `other` is strictly before the interval.
    """
    if other is None:
        return False
    elif isinstance(other, (DateInterval, Sequence)):
        other_ivl = as_dateinterval(other)
        return stop.compareTo(other_ivl.start) < 0
    else:
        other_date = to_absolute_date(other)
        return stop.compareTo(other_date) < 0


def is_strictly_after(other, start: AbsoluteDate, stop: AbsoluteDate) -> bool:
    """Determine whether the other object is strictly after the interval defined by the
    start, stop interval.

    Args:
        other (None|AbsoluteDate|DateInterval): The object to check.
        start (AbsoluteDate): Start of the interval to check against.
        stop (AbsoluteDate): Stop of the interval to check against.

    Raises:
        ValueError: When `other` is an unknown type (known types are:
        None|AbsoluteDate|DateInterval)

    Returns:
        bool: When `other` is strictly after the interval.
    """
    if other is None:
        return False
    elif isinstance(other, (DateInterval, Sequence)):
        other_ivl = as_dateinterval(other)
        return start.compareTo(other_ivl.stop) > 0
    else:
        other_date = to_absolute_date(other)
        return start.compareTo(other_date) > 0
