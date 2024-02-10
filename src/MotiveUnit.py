from abc import ABC, abstractmethod
from dataclasses import dataclass

from MotivePosition import PositionInWork


@dataclass(eq=True, frozen=True)
class MotiveUnit(ABC):
    _original_work: str
    _original_position: int
    _position_in_work: PositionInWork

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
    def original_work(self) -> str:
        return self._original_work

    @property
    def original_position(self) -> int:
        return self._original_position

    @property
    def position_in_work(self) -> PositionInWork:
        return self._position_in_work


@dataclass(eq=True, frozen=True)
class MotiveUnitBreak(MotiveUnit):

    _name: str

    def __init__(
        self,
        name: str,
        original_work: str,
        original_position: int,
        position_in_work: PositionInWork = PositionInWork.ORIGINAL,
    ):
        super().__init__(original_work, original_position, position_in_work)
        object.__setattr__(self, "_name", name)

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def inverted(self):
        return MotiveUnitBreak(
            self._name,
            self.original_work,
            self.original_position,
            PositionInWork.INVERTED,
        )

    def mirrored(self):
        return MotiveUnitBreak(
            self._name,
            self.original_work,
            self.original_position,
            PositionInWork.MIRRORED,
        )


@dataclass(eq=True, frozen=True)
class MotiveUnitInterval(MotiveUnit):

    _interval: int

    def __init__(
        self,
        interval: int,
        original_work: str,
        original_position: int,
        position_in_work: PositionInWork = PositionInWork.ORIGINAL,
    ):
        super().__init__(original_work, original_position, position_in_work)
        object.__setattr__(self, "_interval", interval)

    @property
    def name(self) -> str:
        return str(self._interval)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def inverted(self):
        return MotiveUnitInterval(
            -self._interval,
            self.original_work,
            self.original_position,
            PositionInWork.INVERTED,
        )

    def mirrored(self):
        return MotiveUnitInterval(
            self._interval,
            self.original_work,
            self.original_position,
            PositionInWork.MIRRORED,
        )
