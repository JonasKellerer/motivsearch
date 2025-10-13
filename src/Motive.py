from dataclasses import dataclass
from typing import List

from GeneralInterval import BreakInterval, Interval
from MotivePosition import MotivePosition


@dataclass
class Motive:
    positions: List[MotivePosition]
    sequence: List[BreakInterval | Interval]

    def __str__(self):
        return f"{self.sequence},{self.frequency},{self.positions}"

    def __repr__(self):
        return f"{self.sequence},{self.frequency},{self.positions}"

    @property
    def frequency(self):
        return len(self.positions)
