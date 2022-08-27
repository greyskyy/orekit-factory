import functools

from datetime import datetime, timedelta
from typing import Iterable, Iterator

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


@functools.total_ordering
class DateInterval:
    """Interval of time."""

    def __init__(self, start: AbsoluteDate, stop: AbsoluteDate):
        """Class constructor.

        Args:
            start (AbsoluteDate): The starting time.
            stop (AbsoluteDate): The stopping time.
        """
        self.__start = start
        self.__stop = stop

        if self.__start.compareTo(self.__stop) > 0:
            self.__start = stop
            self.__stop = start

    @property
    def start(self) -> AbsoluteDate:
        """Starting time of the interval.

        Returns:
            AbsoluteDate: The interval's starting time.
        """
        return self.__start

    @property
    def stop(self) -> AbsoluteDate:
        """Stopping time of the interval.

        Returns:
            AbsoluteDate: The interval's stop time
        """
        return self.__stop

    @functools.cached_property
    def duration_secs(self) -> float:
        """The duration of this interval, in floating point seconds.

        Returns:
            float: The duration, in seconds.
        """
        return self.__stop.durationFrom(self.__start)

    @functools.cached_property
    def duration(self) -> timedelta:
        """The duration as a `timedelta`.

        Returns:
            timedelta: The interval duration as a `timedelta`
        """
        return timedelta(seconds=self.duration_secs)

    def to_tuple(self) -> tuple[AbsoluteDate]:
        """Representation of this interval as a tuple of (start,stop).

        Returns:
            tuple[AbsoluteDate]: The resulting tuple.
        """
        return (self.__start, self.__stop)

    def to_list(self) -> list[AbsoluteDate]:
        """Representations of this interval a list of [start,stop].

        Returns:
            list[AbsoluteDate]: The resulting list
        """
        return [self.__start, self.__stop]

    def pad(self, time: float | timedelta):
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
        if isinstance(time, timedelta):
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
            other (AbsoluteDate|DateInterval): The date or interval to check for
            containment
            startInclusive (bool, optional): Whether the start of this interval is
            closed. Defaults to True.
            stopInclusive (bool, optional): Whether stop of this interval is closed.
            Defaults to False.

        Raises:
            TypeError: _description_

        Returns:
            bool: _description_
        """
        return _contained_in(
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
        return _strictly_before(other, self.__start, self.__stop)

    def strictly_after(self, other) -> bool:
        """Determine if this interval is strictly after the other date or interval.

        Args:
            other (DateInterval): The other date or interval.

        Returns:
            bool: True when this interval is strictly after the other date or interval;
            False otherwise
        """
        return _strictly_after(other, self.__start, self.__stop)

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


@functools.singledispatch
def _contained_in(
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
    if other is None:
        return False
    raise ValueError(f"Unknown interval class type: {type(other)}")


@_contained_in.register
def _contained_in_date(
    date: AbsoluteDate,
    start: AbsoluteDate,
    stop: AbsoluteDate,
    startInclusive: bool = True,
    stopInclusive: bool = False,
) -> bool:
    v0 = 0 if startInclusive else -1
    v1 = 0 if stopInclusive else 1

    return start.compareTo(date) <= v0 and stop.compareTo(date) >= v1


@_contained_in.register
def _contained_in_ivl(
    ivl: DateInterval,
    start: AbsoluteDate,
    stop: AbsoluteDate,
    startInclusive: bool = True,
    stopInclusive: bool = False,
) -> bool:
    v0 = 0 if startInclusive else -1
    v1 = 0 if stopInclusive else 1

    return start.compareTo(ivl.start) <= v0 and stop.compareTo(ivl.stop) >= v1


@functools.singledispatch
def _strictly_before(other, start: AbsoluteDate, stop: AbsoluteDate) -> bool:
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
    raise ValueError(f"Unknown interval class type: {type(other)}")


@_strictly_before.register
def _strictly_before_date(
    date: AbsoluteDate, start: AbsoluteDate, stop: AbsoluteDate
) -> bool:
    return stop.compareTo(date) < 0


@_strictly_before.register
def _strictly_before_ivl(
    ivl: DateInterval, start: AbsoluteDate, stop: AbsoluteDate
) -> bool:
    return stop.compareTo(ivl.start) < 0


@functools.singledispatch
def _strictly_after(other, start: AbsoluteDate, stop: AbsoluteDate) -> bool:
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
    raise ValueError(f"Unknown interval class type: {type(other)}")


@_strictly_after.register
def _strictly_after_date(
    date: AbsoluteDate, start: AbsoluteDate, stop: AbsoluteDate
) -> bool:
    return start.compareTo(date) > 0


@_strictly_after.register
def _strictly_after_ivl(
    ivl: DateInterval, start: AbsoluteDate, stop: AbsoluteDate
) -> bool:
    return start.compareTo(ivl.stop) > 0


class DateIntervalList:
    """A list of non-overlapping DateInterval instances.
    This list is sorted in ascending interval order.
    """

    def __init__(
        self,
        interval: DateInterval = None,
        intervals: Iterable[DateInterval] = None,
        _dates: tuple[AbsoluteDate] = None,
        reduce_input=True,
    ):
        """_summary_

        Args:
            interval (DateInterval, optional): Create an interval list from a single
            interval. Defaults to None.
            intervals (tuple[DateInterval], optional): Create a list from a set of
            intervals. Defaults to None.
            reduce_input (bool, optional): When true, reduce the input list. Only set
            to False when the input list is explicitly built non-overlapping. Generally
            always True. Defaults to True.
        """
        if _dates:
            self.__dates = _dates
        elif interval:
            self.__dates = (interval.start, interval.stop)
        elif intervals:
            if reduce_input:
                self.__dates = DateIntervalList._reduce(intervals)
            else:
                self.__dates = DateIntervalList._flatten(intervals)
        else:
            self.__dates: tuple[AbsoluteDate] = ()

    @functools.cached_property
    def span(self) -> DateInterval:
        """The interval from the earliest start to the latest stop of all intervals in
        the list.

        Returns:
            DateInterval: The span interval
        """
        return DateInterval(self.__dates[0], self.__dates[-1])

    def to_date_list(self) -> tuple[AbsoluteDate]:
        """Convert this list into a flattened date tuple.

        Returns:
            tuple[AbsoluteDate]: The flattened start/stop dates
        """
        return self.__dates

    def contains(
        self, other, startInclusive: bool = True, stopInclusive: bool = False
    ) -> bool:
        """Determine if this interval contains the provided time or interval.

        Args:
            other (AbsoluteDate|DateInterval): The date or interval to check for
            containment
            startInclusive (bool, optional): Whether the start of this interval is
            closed. Defaults to True.
            stopInclusive (bool, optional): Whether stop of this interval is closed.
            Defaults to False.

        Raises:
            TypeError: _description_

        Returns:
            bool: _description_
        """
        for i in range(0, len(self.__dates) - 1, 2):
            start = self.__dates[i]
            stop = self.__dates[i + 1]

            if i == 0 and _strictly_before(other, start, stop):
                return False
            elif _contained_in(
                other,
                start,
                stop,
                startInclusive=startInclusive,
                stopInclusive=stopInclusive,
            ):
                return True
            elif _strictly_after(other, start, stop):
                return False
        return False

    def __iter__(self) -> Iterator[DateInterval]:
        tmp = [iter(self.__dates)] * 2
        for (start, stop) in zip(*tmp, strict=True):
            yield DateInterval(start, stop)

    def __getitem__(self, idx: int) -> DateInterval:
        return DateInterval(self.__dates[idx * 2], self.__dates[idx * 2 + 1])

    def __len__(self) -> int:
        return int(self.__dates.__len__() / 2)

    def __str__(self) -> str:
        s = ""
        for i in range(0, min(len(self), 5)):
            if i == 0:
                s = str(self[i])
            else:
                s = f"{s}, {self[i]}"
        return f"[{s}]"

    @staticmethod
    def _reduce(intervals: Iterable[DateInterval]) -> tuple[AbsoluteDate]:
        combined = list(intervals)
        combined.sort()

        i: int = 1
        while i < len(combined):
            j: int = i - 1

            if combined[i].overlaps(
                combined[j], startInclusive=True, stopInclusive=True
            ):
                combined[j] = combined[j].union(combined[i])
                combined.pop(i)
            else:
                i = i + 1

        dates = []
        for i in combined:
            dates.extend((i.start, i.stop))

        return tuple(dates)

    @staticmethod
    def _flatten(intervals: Iterable[DateInterval]) -> tuple[AbsoluteDate]:
        dates = []
        for i in intervals:
            dates.extend((i.start, i.stop))
        return dates


class DateIntervalListBuilder:
    """Build an interval given a known containing interval.

    This class enables building a DateIntervalList incrementally.
    """

    def __init__(self, start: AbsoluteDate = None, stop: AbsoluteDate = None):
        """Class constructor.

        Args:
            start (AbsoluteDate, optional): The earliest start time. Defaults to None.
            stop (AbsoluteDate, optional): The latest stop time. Defaults to None.
        """
        self.__start = start
        self.__stop = stop
        self.__dates = []

    def add_start(self, date: AbsoluteDate):
        if len(self.__dates) % 2 != 0:
            raise ValueError("Cannot add a second start to the builder.")

        self.__dates.append(date)

    def add_stop(self, date: AbsoluteDate):
        if not self.__dates and self.__start:
            self.__dates.append(self.__start)
        if len(self.__dates) % 2 == 0:
            raise ValueError("Cannot add a second stop to the builder.")

        self.__dates.append(date)

    def build_list(self) -> DateIntervalList:
        intervals = []
        if len(self.__dates) % 2:
            self.__dates.append(self.__stop)

        for start, stop in zip(*[iter(self.__dates)] * 2):
            intervals.append(DateInterval(start, stop))

        return DateIntervalList(intervals=intervals, reduce_input=True)


def _verifylist(list1) -> DateIntervalList:
    if list1 is None:
        raise ValueError("List cannot be None")

    if isinstance(list1, DateIntervalList):
        return list1
    elif isinstance(list1, DateInterval):
        return DateIntervalList(interval=list1)
    else:
        return DateIntervalList(intervals=list1)


class IntervalListOperations:
    """This class contains a collection of set operations to be performed on
    DateIntervalList instances."""

    @staticmethod
    def union(list1: DateIntervalList, list2: DateIntervalList) -> DateIntervalList:
        """Compute the union of the two lists. Overlapping intervals will be combined.

        Args:
            list1 (DateIntervalList): The first list.
            list2 (DateIntervalList): The second list.

        Returns:
            DateIntervalList: The list containing the union of the two lists.
        """
        list1 = _verifylist(list1)
        list2 = _verifylist(list2)

        combined = list(list1)
        combined.extend(list(list2))

        return DateIntervalList(intervals=combined, reduce_input=True)

    @staticmethod
    def intersection(
        list1: DateIntervalList,
        list2: DateIntervalList,
        allow_zero_length: bool = False,
    ) -> DateIntervalList:
        """Compute the intersection of the provided interval lists.
        The intersection computes the periods which are contained in one interval of
        each list.

        Args:
            list1 (DateIntervalList): The first list.
            list2 (DateIntervalList): The second list.
            allow_zero_length (bool, optional): Indicate whether to allow endpoint
            overlap to count as intersection. Setting this to True results in
            zero-duration result intervals.

        Returns:
            DateIntervalList: The list containing intervals contained within both lists.
        """
        list1 = _verifylist(list1)
        list2 = _verifylist(list2)

        i: int = 0
        j: int = 0
        results: list[DateInterval] = []
        while i < len(list1) and j < len(list2):
            l1 = list1[i] if i < len(list1) else None
            l2 = list2[j] if j < len(list2) else None

            # if only l1 is specified
            if l1 and l2:
                intersect = l1.intersect(l2, endpoint_inclusive=allow_zero_length)
                if intersect:
                    results.append(intersect)
                if l1.stop.compareTo(l2.stop) < 0:
                    i = i + 1
                else:
                    j = j + 1
        return DateIntervalList(intervals=results, reduce_input=False)

    @staticmethod
    def subtract(list1: DateIntervalList, list2: DateIntervalList) -> DateIntervalList:
        """Subtract the `list2` intervals from the `list1` intervals.

        Args:
            list1 (DateIntervalList): The minutend (list from which intervals will be
            subtracted).
            list2 (DateIntervalList): The subtrahend (list which will be subtracted
            from the other quantity.)

        Returns:
            DateIntervalList: The resulting intervals, or None.
        """
        list1 = _verifylist(list1)
        list2 = _verifylist(list2)

        # compute the intersection
        holes = IntervalListOperations.intersection(list1, list2)

        return IntervalListOperations.compliment(holes, list1.span)

    @staticmethod
    def compliment(
        lst: DateIntervalList, span: DateInterval = None
    ) -> DateIntervalList:
        lst = _verifylist(lst)
        if span is None:
            span = lst.span

        dates = list(
            filter(
                lambda d: _contained_in(
                    d, span.start, span.stop, startInclusive=True, stopInclusive=True
                ),
                lst.to_date_list(),
            )
        )

        dates.insert(0, span.start)
        dates.append(span.stop)

        if dates[0].equals(dates[1]):
            dates.pop(0)
            dates.pop(0)

        if dates and dates[-1].equals(dates[-2]):
            dates.pop()
            dates.pop()

        if len(dates) % 2 != 0:
            dates.pop()

        return DateIntervalList(_dates=dates)
