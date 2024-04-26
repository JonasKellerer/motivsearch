from pathlib import Path
from typing import List, Optional, Tuple

from Motive import Motive
from MotivePosition import PositionInWork, MotivePosition
from MotiveSequence import PositionSequence
from MotiveUnit import MotiveUnitInterval, MotiveUnit
from ParsedFiles import ParsedFiles
from UnitSequence import UnitSequence
from src.MainParser import ParseOption


class MotiveGenerator:
    def __init__(
        self,
        min_frequency: int,
        max_gap: int,
        max_length: int,
        min_num_sequences: int,
        max_num_sequences: int,
    ):
        self.min_frequency = min_frequency
        self.max_gap = max_gap
        self.max_length = max_length
        self.min_num_sequences = min_num_sequences
        self.max_num_sequences = max_num_sequences

    def discover_motives(
        self, file_path: Path, options: List[ParseOption]
    ) -> Tuple[List[Motive], ParsedFiles]:
        parsed_files = ParsedFiles.parse_files(file_path, options)
        motives = self.generate_motives(parsed_files.get_all_motive_units(self.max_gap))

        motives = self.remove_motives_with_breaks(motives)

        if ParseOption.WITH_INVERTED in options or ParseOption.WITH_MIRRORED in options:
            motives = self.merge_inverted_and_mirrored(motives)

        if (
            ParseOption.WITH_INVERTED in options
            and ParseOption.WITH_MIRRORED in options
        ):
            motives = self.remove_motives_only_in_mirrored_and_inverted(motives)

        return motives, parsed_files

    def remove_motives_with_breaks(self, motives: List[Motive]) -> List[Motive]:
        return [
            motive
            for motive in motives
            if all(
                isinstance(motive_unit, MotiveUnitInterval)
                for motive_unit in motive.sequence
            )
        ]

    def merge_inverted_and_mirrored(self, motives: List[Motive]) -> List[Motive]:
        unique_motives: List[Motive] = []
        for motive in motives:
            sequence = motive.sequence
            if len(unique_motives) == 0:
                unique_motives.append(motive)
                continue

            merged = False
            for unique_motive in unique_motives:
                if UnitSequence(unique_motive.sequence).is_equal_mirrored_or_inverted(
                    UnitSequence(sequence)
                ):
                    original_positions = PositionSequence(unique_motive.positions)
                    original_positions.merge(PositionSequence(motive.positions))
                    unique_motive.positions = original_positions.sequence
                    merged = True
                    break
            if not merged:
                unique_motives.append(motive)

        return unique_motives

    def remove_motives_only_in_mirrored_and_inverted(
        self, motives: List[Motive]
    ) -> List[Motive]:
        return [
            motive
            for motive in motives
            if any(
                position.position_in_work == PositionInWork.ORIGINAL
                for position in motive.positions
            )
        ]

    def generate_motives(
        self,
        sequence: List[MotiveUnit],
    ) -> List[Motive]:
        basic_motives = self.get_basic_motives(sequence)
        motives_of_all_iterations = []

        current_motive = self.get_initial_motives(basic_motives.copy())

        while current_motive:
            new_motives = []
            for motive in current_motive:
                frequent_position = self.get_frequent_position(motive)
                candidate_extensions = self.generate_candidate_extension(
                    basic_motives, frequent_position
                )
                for candidate in candidate_extensions:
                    merged = self.merge_motives(motive, candidate)
                    if merged is not None:
                        new_motives.append(merged)
            current_motive = self.filter_motives(new_motives)

            motives_to_add_to_all_iterations = [
                motive
                for motive in current_motive
                if len(motive.sequence) >= self.min_num_sequences
            ]
            motives_of_all_iterations.extend(motives_to_add_to_all_iterations)

        return motives_of_all_iterations

    def get_initial_motives(self, motives: List[Motive]) -> List[Motive]:
        return [
            motive
            for motive in motives
            if all(
                sequence.position_in_work == PositionInWork.ORIGINAL
                for sequence in motive.sequence
            )
        ]

    def get_basic_motives(self, sequence: List[MotiveUnit]) -> List[Motive]:
        basic_motives: dict[str, Motive] = {}
        for index, unit in enumerate(sequence):
            if unit.name not in basic_motives:
                basic_motives[unit.name] = Motive([], 0, [unit])
            basic_motives[unit.name].positions.append(
                MotivePosition(
                    index,
                    1,
                    unit.original_work,
                    unit.original_position,
                    unit.position_in_work,
                )
            )
            basic_motives[unit.name].frequency += 1

        return [
            motive
            for motive in basic_motives.values()
            if motive.frequency >= self.min_frequency
        ]

    def get_frequent_position(self, motive: Motive) -> int:
        return (
            motive.positions[self.min_frequency - 1].position
            + motive.positions[self.min_frequency - 1].length
        )

    def generate_candidate_extension(
        self, base_motives: List[Motive], frequent_position: int
    ) -> List[Motive]:
        return [
            motive
            for motive in base_motives
            if any(pos.position >= frequent_position for pos in motive.positions)
        ]

    def merge_motives(self, motive: Motive, candidate: Motive) -> Optional[Motive]:
        new_positions = []
        for position in motive.positions:
            next_positions = []
            for candidate_position in candidate.positions:
                gap = candidate_position.position - (
                    position.position + position.length
                )

                starts_after_current_end = candidate_position.position >= (
                    position.position + position.length
                )

                total_length = (
                    candidate_position.position + candidate_position.length
                ) - position.position

                if (
                    gap <= self.max_gap
                    and starts_after_current_end
                    and total_length <= self.max_length
                ):
                    next_positions.append(candidate_position)

            if next_positions:
                new_positions.append(
                    MotivePosition(
                        position.position,
                        (next_positions[0].position - position.position)
                        + next_positions[0].length,
                        position.original_work,
                        position.original_position,
                        position.position_in_work,
                    )
                )

        if new_positions:
            return Motive(
                new_positions, len(new_positions), motive.sequence + candidate.sequence
            )
        return None

    def filter_motives(self, motives: List[Motive]) -> List[Motive]:

        return [
            motive
            for motive in motives
            if motive.frequency >= self.min_frequency
            and len(motive.sequence) <= self.max_num_sequences
        ]
