from dataclasses import dataclass
from typing import List

from MotivePosition import MotivePosition


@dataclass
class PositionSequence:
    sequence: List[MotivePosition]

    def __init__(self, sequence: List[MotivePosition]):
        unique_positions = []
        for position in sequence:
            is_in_unique_positions = any(
                position.is_same_position(unique_position)
                for unique_position in unique_positions
            )

            if not is_in_unique_positions:
                unique_positions.append(position)

        self.sequence = unique_positions

    def merge(self, other: "PositionSequence") -> None:
        both_sequences = self.sequence + other.sequence
        self.__init__(both_sequences)
