"""Time utilities and classes."""
import datetime as dt
import functools

from typing import Iterable, Iterator, Sequence
from orekit.pyhelpers import absolutedate_to_datetime

from org.orekit.time import AbsoluteDate


from ._dateinterval import (
    DateInterval,
    as_dateinterval,
    is_strictly_before,
    is_strictly_after,
    is_contained_in,
)


class DateIntervalList:
    """A list of non-overlapping DateInterval instances.
    This list is sorted in ascending interval order.
    """

    def __init__(
        self,
        interval: DateInterval
        | tuple[AbsoluteDate | dt.datetime]
        | list[AbsoluteDate | dt.datetime] = None,
        intervals: Iterable[DateInterval] = None,
        _dates: tuple[AbsoluteDate] = None,
        reduce_input=True,
    ):
        """_summary_

        Args:
            interval (DateInterval|tuple|list, optional): Create an interval
            list from a single
            interval. A tuple or list must have 2 values representing the start
            and stop respectively. If
            specified as datetime objects they will be convertered to
            AbsoluteDate using the default data context.
            Defaults to None.
            intervals (tuple[DateInterval], optional): Create a list from a set of
            intervals. Defaults to None.
            reduce_input (bool, optional): When true, reduce the input list. Only
            set to False when the input list is explicitly built non-overlapping.
            Generally always True. Defaults to True.
        """
        if _dates:
            self.__dates = _dates
        elif interval:
            interval = as_dateinterval(interval)
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

    def to_dt_list(self) -> tuple[dt.datetime]:
        """Convert this list into a flattened datetime tuple.

        Returns:
            tuple[datetime]: The flattened start/stop dates
        """
        return (absolutedate_to_datetime(d) for d in self.__dates)

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

            if i == 0 and is_strictly_before(other, start, stop):
                return False
            elif is_contained_in(
                other,
                start,
                stop,
                startInclusive=startInclusive,
                stopInclusive=stopInclusive,
            ):
                return True
            elif is_strictly_after(other, start, stop):
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

    def __add__(self, other):
        other_list = as_dateintervallist(other)
        return list_union(self, other_list)

    def __sub__(self, other):
        other_list = as_dateintervallist(other)
        return list_subtract(self, other_list)

    def __and__(self, other):
        other_list = as_dateintervallist(other)
        return list_intersection(self, other_list)

    def __invert__(self):
        return list_compliment(self)

    def __xor__(self, other):
        return list_compliment(self, span=as_dateinterval(other))

    @staticmethod
    def _reduce(intervals: Iterable[DateInterval]) -> tuple[AbsoluteDate]:
        combined = [as_dateinterval(i) for i in intervals]
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
            i = as_dateinterval(i)
            dates.extend((i.start, i.stop))
        return dates


class DateIntervalListBuilder:
    """Build an interval given a known containing interval.

    This class enables building a DateIntervalList incrementally.
    """

    def __init__(self, start: AbsoluteDate = None, stop: AbsoluteDate = None):
        """Class constructor.

        Args:
            start (AbsoluteDate, optional): The earliest start time. Defaults to
            None.
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


def as_dateintervallist(
    value: None
    | DateIntervalList
    | DateInterval
    | Sequence[AbsoluteDate | dt.datetime | Sequence[AbsoluteDate | dt.datetime]],
) -> DateIntervalList:
    """Coerce the provided value into a DateIntervalList.

    This function accepts the following types:
        - DateIntervalList
        - DateInterval
        - None - Produces an empty list
        - Nx1 list or tuple of either AbsoluteDate or datetime objects.
        Provided as [start1, stop1, start2, stop2, ...].
        - Nx2 list or tuple of either AbsoluteDate or datetime objects.
        Provided as [[start1, stop1], [start2, stop2], ...]

    Args:
        value (None | DateIntervalList | DateInterval | Sequence[AbsoluteDate |
        dt.datetime | Sequence[AbsoluteDate|dt.datetime]] | ): Value to coerce

    Returns:
        DateIntervalList: The DateIntervalList

    Raises:
        When the value cannot be coerced
    """
    if value is None:
        return DateIntervalList()
    elif isinstance(value, DateIntervalList):
        return value
    elif isinstance(value, DateInterval):
        return DateIntervalList(interval=value)
    elif isinstance(value, Sequence):
        if len(value) == 0:
            return DateIntervalList()
        elif isinstance(value[0], (AbsoluteDate, dt.datetime, str)):
            if len(value) % 2:
                raise ValueError(
                    "List of scalars is not even. Must be even "
                    "(providing start and stop pairs)."
                )
            else:
                intervals = [
                    as_dateinterval(t0, t1) for t0, t1 in zip(value[::2], value[1::2])
                ]
                return DateIntervalList(intervals=intervals)
        elif isinstance(value[0], (DateInterval, Sequence)):
            intervals = [as_dateinterval(v) for v in value]
            return DateIntervalList(intervals=intervals)

    raise RuntimeError("Failed to coerce the value into a DateIntervalList.")


def list_union(list1: DateIntervalList, list2: DateIntervalList) -> DateIntervalList:
    """Compute the union of the two lists. Overlapping intervals will be combined.

    Args:
        list1 (DateIntervalList): The first list.
        list2 (DateIntervalList): The second list.

    Returns:
        DateIntervalList: The list containing the union of the two lists.
    """
    list1 = as_dateintervallist(list1)
    list2 = as_dateintervallist(list2)

    combined = list(list1)
    combined.extend(list(list2))

    return DateIntervalList(intervals=combined, reduce_input=True)


def list_intersection(
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
    list1 = as_dateintervallist(list1)
    list2 = as_dateintervallist(list2)

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


def list_subtract(list1: DateIntervalList, list2: DateIntervalList) -> DateIntervalList:
    """Subtract the `list2` intervals from the `list1` intervals.

    Args:
        list1 (DateIntervalList): The minutend (list from which intervals will be
        subtracted).
        list2 (DateIntervalList): The subtrahend (list which will be subtracted
        from the other quantity.)

    Returns:
        DateIntervalList: The resulting intervals, or None.
    """
    list1 = as_dateintervallist(list1)
    list2 = as_dateintervallist(list2)

    # compute the intersection
    holes = list_intersection(list1, list2)

    return list_compliment(holes, list1.span)


def list_compliment(
    lst: DateIntervalList, span: DateInterval = None
) -> DateIntervalList:
    lst = as_dateintervallist(lst)
    if span is None:
        span = lst.span
    else:
        span = as_dateinterval(span)

    dates = list(
        filter(
            lambda d: is_contained_in(
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
