from enum import Enum


class SequenceType(str, Enum):
    ORIGINAL = 0
    INVERTED = 1
    MIRRORED = 2
    MIRRORED_INVERTED = 3

    def __str__(self):
        return self.name
