import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional

from Corpus import Corpus
from GeneralInterval import Interval
from Motive import Motive
from MotiveList import MotiveList
from MotivePosition import MotivePosition
from MotiveUnitGenerator import MotiveUnitGenerator
from PositionSequence import PositionSequence
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
    ) -> MotiveList:
        logging.info(f"Discovering motives in {file_path}")
        corpus = Corpus.parse(file_path)

        if ParseOption.USE_DIATONIC in options:
            corpus.remove_accidentals()

        motive_unit_generator = MotiveUnitGenerator()
        all_motive_units = motive_unit_generator.from_corpus(corpus)

        all_motives = MotiveList([])
        for piece in all_motive_units:
            logging.info(f"Processing piece {piece}")
            for part in all_motive_units[piece]:
                logging.info(f"Processing part {part}")
                for voice in all_motive_units[piece][part]:
                    logging.info(f"Processing voice {voice}")
                    motive_units = all_motive_units[piece][part][voice]
                    motives = self.generate_motives(motive_units)
                    motives = self.remove_motives_with_breaks(motives)

                    all_motives.add(motives, piece, part, voice)

        return all_motives

    def remove_motives_with_breaks(self, motives: List[Motive]) -> List[Motive]:
        logging.info("Removing motives with breaks")
        return [
            motive
            for motive in motives
            if all(isinstance(motive_unit, Interval) for motive_unit in motive.sequence)
        ]

    def generate_motives(
        self,
        sequence: List[Motive],
    ) -> List[Motive]:
        logging.info("Generating motives")
        basic_motives = self.get_basic_motives(sequence)
        motives_of_all_iterations = []

        current_motive = basic_motives.copy()

        while current_motive:
            logging.info(f"Current motives: {len(current_motive)}")
            new_motives: List[Motive] = []
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
            current_motive = new_motives

            motives_to_add_to_all_iterations = [
                motive
                for motive in current_motive
                if len(motive.sequence) >= self.min_num_sequences
            ]
            logging.info(
                f"Found {len(motives_to_add_to_all_iterations)} motives with at least {self.min_num_sequences} sequences"
            )
            motives_of_all_iterations.extend(motives_to_add_to_all_iterations)

            if any(
                len(motive.sequence) >= self.max_num_sequences
                for motive in current_motive
            ):
                break

        return motives_of_all_iterations

    def get_basic_motives(self, sequence: List[Motive]) -> List[Motive]:
        logging.info("Getting basic motives")
        basic_motives: dict[str, Motive] = {}
        for index, motive in enumerate(sequence):
            name = motive.sequence[0].name
            if name not in basic_motives:
                basic_motives[name] = Motive(sequence=motive.sequence, positions=[])
            basic_motives[name].positions.append(
                MotivePosition(position=index, length=1)
            )
        logging.info(f"Found {len(basic_motives)} basic motives")

        return [motive for motive in basic_motives.values()]

    def get_frequent_position(self, motive: Motive) -> int:
        return motive.positions[0].position + motive.positions[0].length

    def generate_candidate_extension(
        self, base_motives: List[Motive], frequent_position: int
    ) -> List[Motive]:
        logging.info(
            f"Generating candidate extensions for position {frequent_position}"
        )
        return [
            motive
            for motive in base_motives
            if any(pos.position >= frequent_position for pos in motive.positions)
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
            )

        return None
