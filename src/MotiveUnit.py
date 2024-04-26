from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from Origin import Origin
from PositionInWork import PositionInWork


class RestIntervalType(str, Enum):
    NOTE_BEFORE = 0
    NOTE_AFTER = 1
    REST_BEFORE = 2
    DIVIDER = 3

    def __str__(self):
        return self.name


@dataclass(eq=True, frozen=True)
class MotiveUnit(ABC):
    _position_in_work: PositionInWork
    _origin: Origin

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def inverted(self):
        pass

    @abstractmethod
    def mirrored(self):
        pass

    @property
    def origin(self) -> Origin:
        return self._origin

    @property
    def position_in_work(self) -> PositionInWork:
        return self._position_in_work


@dataclass(eq=True, frozen=True)
class MotiveUnitBreak(MotiveUnit):

    _type: RestIntervalType

    def __init__(
        self,
        type: RestIntervalType,
        origin: Origin,
        position_in_work: PositionInWork = PositionInWork.ORIGINAL,
    ):
        super().__init__(_origin=origin, _position_in_work=position_in_work)
        object.__setattr__(self, "_type", type)

    @property
    def name(self) -> str:
        return str(self._type)

    def __str__(self):
        return str(self._type)

    def __repr__(self):
        return str(self._type)

    def inverted(self):
        return MotiveUnitBreak(
            type=self._type,
            origin=self.origin,
            position_in_work=PositionInWork.INVERTED,
        )

    def mirrored(self):
        return MotiveUnitBreak(
            type=self._type,
            origin=self.origin,
            position_in_work=PositionInWork.MIRRORED,
        )


@dataclass(eq=True, frozen=True)
class MotiveUnitInterval(MotiveUnit):

    _interval: int

    def __init__(
        self,
        interval: int,
        origin: Origin,
        position_in_work: PositionInWork = PositionInWork.ORIGINAL,
    ):
        super().__init__(_origin=origin, _position_in_work=position_in_work)
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

        return MotiveUnitInterval(
            interval=inverted_interval,
            origin=self.origin,
            position_in_work=PositionInWork.INVERTED,
        )

    def mirrored(self):
        return MotiveUnitInterval(
            interval=self._interval,
            origin=self.origin,
            position_in_work=PositionInWork.MIRRORED,
        )
