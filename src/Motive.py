from dataclasses import dataclass
from typing import List

from MotivePosition import MotivePosition
from MotiveUnit import MotiveUnit


@dataclass
class Motive:
    positions: List[MotivePosition]
    frequency: int
    sequence: List[MotiveUnit]

    @classmethod
    def from_positions(
        cls, positions: List[MotivePosition], sequence: List[MotiveUnit]
    ):
        return cls(positions, len(positions), sequence)

    def __str__(self):
        return f"{self.sequence},{self.frequency},{self.positions}"

    def __repr__(self):
        return f"{self.sequence},{self.frequency},{self.positions}"
