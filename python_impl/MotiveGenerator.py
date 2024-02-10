from dataclasses import dataclass
from typing import List


@dataclass(eq=True, frozen=True)
class MotiveUnit:
    name: str


@dataclass
class MotivePosition:
    position: int
    length: int


@dataclass
class Motive:
    positions: List[MotivePosition]
    frequency: int
    sequence: List[MotiveUnit]

    @classmethod
    def from_positions(cls, positions: List[MotivePosition], sequence: List[MotiveUnit]):
        return cls(positions, len(positions), sequence)


class MotiveGenerator:
    def generate_motives(self, sequence: List[MotiveUnit], min_frequency: int, max_gap: int, min_length: int,
                         max_length: int) -> List[Motive]:
        basic_motives = self.get_basic_motives(sequence, min_frequency)
        motives_of_all_iterations = []

        while basic_motives:
            new_motives = []
            for motive in basic_motives:
                frequent_position = self.get_frequent_position(motive, min_frequency)
                candidate_extensions = self.generate_candidate_extension(basic_motives, frequent_position)
                for candidate in candidate_extensions:
                    merged = self.merge_motives(motive, candidate, max_gap, max_length)
                    if merged and len(merged.sequence) >= min_length:
                        new_motives.append(merged)
            basic_motives = self.filter_motives(new_motives, min_frequency, max_length)
            motives_of_all_iterations.extend(basic_motives)

        return motives_of_all_iterations

    def get_basic_motives(self, sequence: List[MotiveUnit], min_frequency: int) -> List[Motive]:
        basic_motives: dict[MotiveUnit, Motive] = {}
        for index, unit in enumerate(sequence):
            if unit not in basic_motives:
                basic_motives[unit] = Motive([], 0, [unit])
            basic_motives[unit].positions.append(MotivePosition(index, 1))
            basic_motives[unit].frequency += 1

        return [motive for motive in basic_motives.values() if motive.frequency >= min_frequency]

    def get_motive_units(self, sequence: str) -> List[MotiveUnit]:
        return [MotiveUnit(value.strip()) for value in sequence.split(",")]

    def get_frequent_position(self, motive: Motive, min_frequency: int) -> int:
        return motive.positions[min_frequency - 1].position + motive.positions[min_frequency - 1].length

    def generate_candidate_extension(self, base_motives: List[Motive], frequent_position: int) -> List[Motive]:
        return [motive for motive in base_motives if
                any(pos.position >= frequent_position - 1 for pos in motive.positions)]

    def merge_motives(self, motive: Motive, candidate: Motive, max_gap: int, max_length: int) -> Motive:
        new_positions = []
        for position in motive.positions:
            next_positions = [candidate_position for candidate_position in candidate.positions if
                              candidate_position.position - (
                                      position.position + position.length) <= max_gap and candidate_position.position >= (
                                      position.position + position.length) and candidate_position.position + candidate_position.length - position.position <= max_length]
            if next_positions:
                new_positions.append(MotivePosition(position.position, position.length + next_positions[0].length))

        if new_positions:
            return Motive(new_positions, len(new_positions), motive.sequence + candidate.sequence)
        return None

    def filter_motives(self, motives: List[Motive], min_frequency: int, max_length: int) -> List[Motive]:
        return [motive for motive in motives if
                motive.frequency >= min_frequency and len(motive.sequence) <= max_length]
