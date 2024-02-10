from dataclasses import dataclass
from typing import List

from MotiveUnit import MotiveUnit


@dataclass
class UnitSequence:
    sequence: List[MotiveUnit]

    def inverted(self):
        return UnitSequence([unit.inverted() for unit in self.sequence])

    def mirrored(self):
        mirrored = [unit.mirrored() for unit in self.sequence]
        return UnitSequence(mirrored[::-1])

    def mirrored_and_inverted(self):
        return self.inverted().mirrored()

    def has_equal_intervals(self, other: "UnitSequence") -> bool:
        if len(self.sequence) != len(other.sequence):
            return False

        for i in range(len(self.sequence)):
            if self.sequence[i].name != other.sequence[i].name:
                return False
        return True

    def is_equal_mirrored_or_inverted(self, other: "UnitSequence") -> bool:
        inverted_other = other.inverted()
        mirrored_other = other.mirrored()
        mirrored_and_inverted_other = other.mirrored_and_inverted()

        return (
            self.has_equal_intervals(inverted_other)
            or self.has_equal_intervals(mirrored_other)
            or self.has_equal_intervals(mirrored_and_inverted_other)
        )
