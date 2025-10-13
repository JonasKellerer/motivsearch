from enum import Enum


class SequenceType(str, Enum):
    ORIGINAL = "ORIGINAl"
    INVERTED = "INVERTED"
    MIRRORED = "MIRRORED"
    MIRRORED_INVERTED = "MIRRORED_INVERTED"

    def __str__(self):
        return self.name
