from dataclasses import dataclass

from MotiveUnit import Origin
from PositionInWork import PositionInWork


@dataclass
class MotivePosition:
    position: int
    length: int

    origin: Origin
    position_in_work: PositionInWork

    def __str__(self):
        return f"{self.position}:{self.length}:{self.origin}:{self.position_in_work}"

    def __repr__(self):
        return f"{self.origin}:{self.length}"

    def is_same_position(self, other: "MotivePosition") -> bool:
        if self.length != other.length:
            return False

        if self.origin != other.origin:
            return False

        if (
            self.position_in_work is PositionInWork.OUTSIDE
            or other.position_in_work is PositionInWork.OUTSIDE
        ):
            return False

        if self.position_in_work is PositionInWork.MIRRORED:
            if other.position_in_work is PositionInWork.MIRRORED:
                return self.origin.note_number == other.origin.note_number
            else:
                return (
                    self.origin.note_number
                    == other.origin.note_number + other.length - 1
                )
        else:
            if other.position_in_work is PositionInWork.MIRRORED:
                return (
                    self.origin.note_number + self.length - 1
                    == other.origin.note_number
                )
            else:
                return self.origin.note_number == other.origin.note_number
