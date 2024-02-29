import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

from music21 import note, converter
from music21.interval import Interval
from music21.note import GeneralNote
from music21.stream.iterator import StreamIterator


@dataclass
class MotiveGeneratorOptions:
    min_frequency: int
    max_gap: int
    max_length: int
    min_num_sequences: int
    max_num_sequences: int


class ParseOption(Enum):
    WITH_INVERTED = 1
    WITH_MIRRORED = 2
    USE_DIATONIC = 3


@dataclass
class ParserOptions:
    input_folder: Path
    output_folder: Path
    options: list[ParseOption]


def prase_args() -> (MotiveGeneratorOptions, ParserOptions):
    parser = argparse.ArgumentParser(description="Motive Generator")
    parser.add_argument(
        "--inputFolder", type=str, help="Folder containing the xml files"
    )
    parser.add_argument("--outputFolder", type=str, help="Folder for output files")
    parser.add_argument(
        "--minFrequency",
        type=int,
        help="Minimal frequency, of how often a motive must occur",
    )
    parser.add_argument(
        "--maxGap", type=int, help="Maximum gap allowed between two notes"
    )
    parser.add_argument(
        "--minNumSequences", type=int, help="Minimum number of sequences"
    )
    parser.add_argument(
        "--maxNumSequences", type=int, help="Maximum number of sequences"
    )
    parser.add_argument("--maxLength", type=int, help="Maximum length of a motive")
    parser.add_argument(
        "--withInverted", action="store_true", help="Searches also for inverted motives"
    )
    parser.add_argument(
        "--withMirrored", action="store_true", help="Searches also for mirrored motives"
    )
    parser.add_argument(
        "--useDiatonic", action="store_true", help="Use diatonic intervals"
    )

    args = parser.parse_args()
    motive_generator_options = MotiveGeneratorOptions(
        args.minFrequency,
        args.maxGap,
        args.maxLength,
        args.minNumSequences,
        args.maxNumSequences,
    )
    parsers_options = ParserOptions(
        args.inputFolder,
        args.outputFolder,
        [
            ParseOption.WITH_INVERTED if args.withInverted else None,
            ParseOption.WITH_MIRRORED if args.withMirrored else None,
            ParseOption.USE_DIATONIC if args.useDiatonic else None,
        ],
    )

    return motive_generator_options, parsers_options


@dataclass(eq=True, frozen=True)
class MotiveUnit(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def inverted(self):
        pass


@dataclass(eq=True, frozen=True)
class MotiveUnitBreak(MotiveUnit):

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def inverted(self):
        return self


@dataclass(eq=True, frozen=True)
class MotiveUnitInterval(MotiveUnit):

    _interval: int

    @property
    def name(self) -> str:
        return str(self._interval)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def inverted(self):
        return MotiveUnitInterval(-self._interval)


@dataclass
class MotivePosition:
    position: int
    length: int

    def __str__(self):
        return f"{self.position}:{self.length}"

    def __repr__(self):
        return f"{self.position}:{self.length}"


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


@dataclass
class MotiveList:
    motives: List[Motive]
    notes: StreamIterator[GeneralNote]

    def get_inverse_positions(self) -> List[MotivePosition]:
        pass


@dataclass
class ParsedFile:
    motive_units: List[MotiveUnit]
    motive_units_inverted: List[MotiveUnit]
    motive_units_mirrored: List[MotiveUnit]
    notes_and_rests: StreamIterator[GeneralNote]

    def get_all_motive_units(self, max_gap: int) -> List[MotiveUnit]:
        def get_breaks():
            return [MotiveUnitBreak("RestBetween") for _ in range(max_gap)]

        def add_with_breaks(motive_units: List[MotiveUnit]) -> List[MotiveUnit]:
            if len(motive_units) == 0:
                return []

            return get_breaks() + motive_units

        return (
            self.motive_units
            + add_with_breaks(self.motive_units_inverted)
            + add_with_breaks(self.motive_units_mirrored)
        )


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
        self, file_path: str, options: List[ParseOption]
    ) -> Tuple[List[Motive], ParsedFile]:
        parsed_file = self.parse_file(file_path, options)

        motives = self.generate_motives(parsed_file.get_all_motive_units(self.max_gap))

        if ParseOption.WITH_INVERTED in options:
            motives = self.remove_inverse_duplicates(motives)

        return motives, parsed_file

    def remove_inverse_duplicates(self, motives: List[Motive]) -> List[Motive]:
        unique_motives = []
        result = []
        for motive in motives:
            inverted_sequence = [
                motive_unit.inverted() for motive_unit in motive.sequence
            ]

            if (
                motive.sequence not in unique_motives
                and inverted_sequence not in unique_motives
            ):
                unique_motives.append(motive.sequence)
                result.append(motive)

        return result

    def get_motive_units(
        self,
        notes_and_rests: StreamIterator[GeneralNote],
    ) -> List[MotiveUnit]:

        motive_units: List[MotiveUnit] = []
        for i in range(len(notes_and_rests) - 1):
            if isinstance(notes_and_rests[i], note.Note):
                if isinstance(notes_and_rests[i + 1], note.Note):
                    motive_units.append(
                        MotiveUnitInterval(
                            Interval(
                                notes_and_rests[i], notes_and_rests[i + 1]
                            ).generic.directed
                        )
                    )
                else:
                    motive_units.append(MotiveUnitBreak("BreakTo"))
            else:
                motive_units.append(MotiveUnitBreak("BreakFrom"))
        return motive_units

    def get_notes(self, file_path: str) -> StreamIterator[GeneralNote]:
        score = converter.parse(file_path)

        notes_and_rests = score.flatten().notesAndRests

        # remove accidentals, make this optional on useDiatonic
        for note_or_rest in notes_and_rests:
            if isinstance(note_or_rest, note.Note):
                note_or_rest.pitch.accidental = None

        return notes_and_rests

    def parse_file(self, file_path: str, options: List[ParseOption]) -> ParsedFile:
        def get_inverted(motive_units: List[MotiveUnit]) -> List[MotiveUnit]:
            if ParseOption.WITH_INVERTED in options:
                return [motive_unit.inverted() for motive_unit in motive_units]
            return []

        def get_mirrored(intervals: List[MotiveUnit]) -> List[MotiveUnit]:
            if ParseOption.WITH_MIRRORED in options:
                inverted = get_inverted(intervals).copy()
                return inverted[::-1]
            return []

        notes_and_rests = self.get_notes(file_path)
        intervals_from_file = self.get_motive_units(notes_and_rests)

        return ParsedFile(
            intervals_from_file,
            get_inverted(intervals_from_file),
            get_mirrored(intervals_from_file),
            notes_and_rests,
        )

    def generate_motives(
        self,
        sequence: List[MotiveUnit],
    ) -> List[Motive]:
        basic_motives = self.get_basic_motives(sequence)
        motives_of_all_iterations = []

        current_motive = basic_motives.copy()

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

    def get_basic_motives(self, sequence: List[MotiveUnit]) -> List[Motive]:
        basic_motives: dict[MotiveUnit, Motive] = {}
        for index, unit in enumerate(sequence):
            if unit not in basic_motives:
                basic_motives[unit] = Motive([], 0, [unit])
            basic_motives[unit].positions.append(MotivePosition(index, 1))
            basic_motives[unit].frequency += 1

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
            and MotiveUnitBreak("RestFrom") not in motive.sequence
            and MotiveUnitBreak("RestTo") not in motive.sequence
        ]


output_filename = "output.csv"


def write_motives_to_file(motives: List[Motive], parser_options: ParserOptions):

    if not parser_options.output_folder.exists():
        parser_options.output_folder.mkdir()

    with open(parser_options.output_folder / output_filename, "w") as file:
        file.write(
            "sequence,frequency,positions,frequency_inverted,positions_inverted,frequency_mirrored,position_mirrored\n"
        )
        for motive in motives:
            file.write(f"{motive.sequence},{motive.frequency},{motive.positions}\n")
