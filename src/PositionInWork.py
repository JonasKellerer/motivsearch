from enum import Enum


class PositionInWork(str, Enum):
    ORIGINAL = 0
    INVERTED = 1
    MIRRORED = 2
    OUTSIDE = 3

    def __str__(self):
        return self.name
