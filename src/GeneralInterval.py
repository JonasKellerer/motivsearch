from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


class RestIntervalType(str, Enum):
    NOTE_BEFORE = 0
    NOTE_AFTER = 1
    REST_BEFORE = 2
    DIVIDER = 3

    def __str__(self):
        return self.name


@dataclass(eq=True, frozen=True)
class GeneralInterval(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def inverted(self) -> "GeneralInterval":
        pass

    @abstractmethod
    def mirrored(self) -> "GeneralInterval":
        pass


@dataclass(eq=True, frozen=True)
class BreakInterval(GeneralInterval):

    _type: RestIntervalType

    def __init__(
        self,
        type: RestIntervalType,
    ):
        object.__setattr__(self, "_type", type)

    @property
    def name(self) -> str:
        return str(self._type)

    def __str__(self):
        return str(self._type)

    def __repr__(self):
        return str(self._type)

    def inverted(self):
        return BreakInterval(type=self._type)

    def mirrored(self):
        return BreakInterval(
            type=self._type,
        )


@dataclass(eq=True, frozen=True)
class Interval(GeneralInterval):
    _interval: int

    def __init__(
        self,
        interval: int,
    ):
        object.__setattr__(self, "_interval", interval)

    @property
    def name(self) -> str:
        return str(self._interval)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def inverted(self):
        inverted_interval = 1 if self._interval == 1 else -self._interval

        return Interval(
            interval=inverted_interval,
        )

    def mirrored(self):
        return Interval(
            interval=self._interval,
        )


@dataclass
class IntervalList:
    intervals: List[GeneralInterval]

    def inverted(self) -> "IntervalList":
        return IntervalList([interval.inverted() for interval in self.intervals])

    def mirrored(self) -> "IntervalList":
        return IntervalList(self.intervals[::-1])

    def mirrored_inverted(self) -> "IntervalList":
        return IntervalList(self.intervals[::-1]).inverted()

    def __str__(self):
        return str([interval.name for interval in self.intervals])
