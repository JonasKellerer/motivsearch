from dataclasses import dataclass
from enum import Enum


class PositionInWork(str, Enum):
    ORIGINAL = 0
    INVERTED = 1
    MIRRORED = 2
    OUTSIDE = 3

    def __str__(self):
        return self.name


@dataclass
class MotivePosition:
    position: int
    length: int

    original_work: str
    original_position: int
    position_in_work: PositionInWork

    def __str__(self):
        return f"{self.position}:{self.length}:{self.original_position}:{self.position_in_work}"

    def __repr__(self):
        return f"{self.original_position}:{self.length}"

    def is_same_position(self, other: "MotivePosition") -> bool:
        if self.length != other.length:
            return False

        if self.original_work != other.original_work:
            return False

        if (
            self.position_in_work is PositionInWork.OUTSIDE
            or other.position_in_work is PositionInWork.OUTSIDE
        ):
            return False

        if self.position_in_work is PositionInWork.MIRRORED:
            if other.position_in_work is PositionInWork.MIRRORED:
                return self.original_position == other.original_position
            else:
                return (
                    self.original_position == other.original_position + other.length - 1
                )
        else:
            if other.position_in_work is PositionInWork.MIRRORED:
                return (
                    self.original_position + self.length - 1 == other.original_position
                )
            else:
                return self.original_position == other.original_position
