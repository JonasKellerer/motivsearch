from enum import IntEnum
from typing import List

from pydantic import  BaseModel

class RestIntervalType(IntEnum):
    NOTE_BEFORE = 0
    NOTE_AFTER = 1
    REST_BEFORE = 2
    DIVIDER = 3

    def __str__(self) -> str:
        return self.name



class BreakInterval(BaseModel):
    type: RestIntervalType

    @property
    def name(self) -> str:
        return str(self.type)

    def __str__(self) -> str:
        return str(self.type)

    def __repr__(self) -> str:
        return str(self.type)

    def inverted(self) -> "BreakInterval":
        return BreakInterval(type=self.type)

    def mirrored(self) -> "BreakInterval":
        return BreakInterval(type=self.type)

class Interval(BaseModel):
    interval: int

    @property
    def name(self) -> str:
        return str(self.interval)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def inverted(self) -> "Interval":
        inverted_interval = 1 if self.interval == 1 else -self.interval
        return Interval(interval=inverted_interval)

    def mirrored(self) -> "Interval":
        return Interval(interval=self.interval)


class IntervalList(BaseModel):
    intervals: List[Interval | BreakInterval]

    def inverted(self) -> "IntervalList":
        return IntervalList(intervals=[interval.inverted() for interval in self.intervals])

    def mirrored(self) -> "IntervalList":
        return IntervalList(intervals=self.intervals[::-1]).inverted()

    def mirrored_inverted(self) -> "IntervalList":
        return IntervalList(intervals=self.intervals[::-1])

    def __str__(self) -> str:
        return str([interval.name for interval in self.intervals])