import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional

from Corpus import Corpus
from Motive import Motive
from MotivePosition import PositionInWork, MotivePosition
from MotiveUnit import MotiveUnitInterval, MotiveUnit
from MotiveUnitGenerator import MotiveUnitGenerator
from PositionSequence import PositionSequence
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
    ) -> List[Motive]:
        logging.info(f"Discovering motives in {file_path}")
        corpus = Corpus.parse(file_path)
        corpus.remove_accidentals()

        motive_unit_generator = MotiveUnitGenerator(
            options=options, max_gap=self.max_gap
        )
        motive_units = motive_unit_generator.from_corpus(corpus)

        motives = self.generate_motives(motive_units)

        motives = self.remove_motives_with_breaks(motives)

        if ParseOption.WITH_INVERTED in options or ParseOption.WITH_MIRRORED in options:
            motives = self.merge_inverted_and_mirrored(motives)

        # if (
        #     ParseOption.WITH_INVERTED in options
        #     and ParseOption.WITH_MIRRORED in options
        # ):
        #     motives = self.remove_motives_only_in_mirrored_and_inverted(motives)

        return motives

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
                    original, to_merge = self.switch_original_and_to_merge(
                        unique_motive, motive
                    )

                    original_position_sequence = PositionSequence(original.positions)

                    original_position_sequence.merge(
                        PositionSequence(to_merge.positions)
                    )
                    unique_motive.positions = original_position_sequence.sequence
                    unique_motive.frequency = len(original_position_sequence.sequence)
                    unique_motive.sequence = original.sequence

                    merged = True
                    break
            if not merged:
                unique_motives.append(motive)

        return unique_motives

    def switch_original_and_to_merge(
        self, original: Motive, to_merge: Motive
    ) -> tuple[Motive, Motive]:
        if (
            to_merge.positions[0].position_in_work == PositionInWork.ORIGINAL
            and original.positions[0].position_in_work != PositionInWork.ORIGINAL
        ):
            return to_merge, original

        return original, to_merge

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
        logging.info("Generating motives")
        basic_motives = self.get_basic_motives(sequence)
        motives_of_all_iterations = []

        current_motive = self.get_initial_motives(basic_motives.copy())

        while current_motive:
            logging.info(f"Current motives: {len(current_motive)}")
            new_motives = []
            for motive in current_motive:
                logging.info(f"Current motive: {motive.sequence}")
                frequent_position = self.get_frequent_position(motive)
                candidate_extensions = self.generate_candidate_extension(
                    basic_motives, frequent_position
                )
                logging.info(f"Found {len(candidate_extensions)} candidate extensions")
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
            logging.info(
                f"Found {len(motives_to_add_to_all_iterations)} motives with at least {self.min_num_sequences} sequences"
            )
            motives_of_all_iterations.extend(motives_to_add_to_all_iterations)

        return motives_of_all_iterations

    def get_initial_motives(self, motives: List[Motive]) -> List[Motive]:
        logging.info("Getting initial motives. Removing motives with breaks.")
        return [
            motive
            for motive in motives
            if all(isinstance(unit, MotiveUnitInterval) for unit in motive.sequence)
        ]

    def get_basic_motives(self, sequence: List[MotiveUnit]) -> List[Motive]:
        logging.info("Getting basic motives")
        basic_motives: dict[str, Motive] = {}
        for index, unit in enumerate(sequence):
            if unit.name not in basic_motives:
                basic_motives[unit.name] = Motive([], 0, [unit])
            basic_motives[unit.name].positions.append(
                MotivePosition(
                    position=index,
                    length=1,
                    origin=unit.origin,
                    position_in_work=unit.position_in_work,
                )
            )
            basic_motives[unit.name].frequency += 1
        logging.info(f"Found {len(basic_motives)} basic motives")

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
        logging.info(
            f"Generating candidate extensions for position {frequent_position}"
        )
        return [
            motive
            for motive in base_motives
            if (
                any(pos.position >= frequent_position for pos in motive.positions)
                and all(
                    isinstance(unit, MotiveUnitInterval) for unit in motive.sequence
                )
            )
        ]

    def merge_motives(self, motive: Motive, candidate: Motive) -> Optional[Motive]:
        logging.info(f"Merging motives {motive.sequence} and {candidate.sequence}")
        logging.info(f"Number of positions in motive: {len(motive.positions)}")
        logging.info(f"Number of positions in candidate: {len(candidate.positions)}")

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda p: self.process_positions(p, candidate.positions),
                motive.positions,
            )

        new_positions = [result for result in results if result is not None]

        if new_positions:
            position_sequence = PositionSequence(new_positions)

            return Motive(
                positions=position_sequence.sequence,
                frequency=len(position_sequence.sequence),
                sequence=motive.sequence + candidate.sequence,
            )
        return None

    def process_positions(
        self,
        position: MotivePosition,
        candidate_positions: list[MotivePosition],
    ):
        next_positions = []
        for candidate_position in candidate_positions:
            if position.position_in_work != candidate_position.position_in_work:
                continue

            gap = candidate_position.position - (position.position + position.length)
            if gap > self.max_gap:
                continue

            starts_after_current_end = candidate_position.position >= (
                position.position + position.length
            )
            if not starts_after_current_end:
                continue

            total_length = (
                candidate_position.position + candidate_position.length
            ) - position.position
            if total_length > self.max_length:
                continue

            next_positions.append(candidate_position)

        if next_positions:
            return MotivePosition(
                position=position.position,
                length=(next_positions[0].position - position.position)
                + next_positions[0].length,
                origin=position.origin,
                position_in_work=position.position_in_work,
            )
        return None

    def filter_motives(self, motives: List[Motive]) -> List[Motive]:
        logging.info(f"Filtering motives: {len(motives)}")

        return [
            motive
            for motive in motives
            if motive.frequency >= self.min_frequency
            and len(motive.sequence) <= self.max_num_sequences
        ]
