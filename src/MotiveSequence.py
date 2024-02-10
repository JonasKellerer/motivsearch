from dataclasses import dataclass
from typing import List

from MotivePosition import MotivePosition


@dataclass
class PositionSequence:
    sequence: List[MotivePosition]

    def merge(self, other: "PositionSequence") -> None:
        for position in other.sequence:
            if not any(
                position.is_same_position(current_position)
                for current_position in self.sequence
            ):
                self.sequence.append(position)
