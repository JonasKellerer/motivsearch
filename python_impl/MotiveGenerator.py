import argparse
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Dict

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
        Path(args.inputFolder),
        Path(args.outputFolder),
        [
            ParseOption.WITH_INVERTED if args.withInverted else None,
            ParseOption.WITH_MIRRORED if args.withMirrored else None,
            ParseOption.USE_DIATONIC if args.useDiatonic else None,
        ],
    )

    return motive_generator_options, parsers_options


class PositionInWork(str, Enum):
    ORIGINAL = 0
    INVERTED = 1
    MIRRORED = 2
    OUTSIDE = 3

    def __str__(self):
        return self.name


@dataclass(eq=True, frozen=True)
class MotiveUnit(ABC):
    _original_work: str
    _original_position: int
    _position_in_work: PositionInWork

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def inverted(self):
        pass

    @abstractmethod
    def mirrored(self):
        pass

    @property
    def original_work(self) -> str:
        return self._original_work

    @property
    def original_position(self) -> int:
        return self._original_position

    @property
    def position_in_work(self) -> PositionInWork:
        return self._position_in_work


@dataclass(eq=True, frozen=True)
class MotiveUnitBreak(MotiveUnit):

    _name: str

    def __init__(
        self,
        name: str,
        original_work: str,
        original_position: int,
        position_in_work: PositionInWork = PositionInWork.ORIGINAL,
    ):
        super().__init__(original_work, original_position, position_in_work)
        object.__setattr__(self, "_name", name)

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def inverted(self):
        return MotiveUnitBreak(
            self._name,
            self.original_work,
            self.original_position,
            PositionInWork.INVERTED,
        )

    def mirrored(self):
        return MotiveUnitBreak(
            self._name,
            self.original_work,
            self.original_position,
            PositionInWork.MIRRORED,
        )


@dataclass(eq=True, frozen=True)
class MotiveUnitInterval(MotiveUnit):

    _interval: int

    def __init__(
        self,
        interval: int,
        original_work: str,
        original_position: int,
        position_in_work: PositionInWork = PositionInWork.ORIGINAL,
    ):
        super().__init__(original_work, original_position, position_in_work)
        object.__setattr__(self, "_interval", interval)

    @property
    def name(self) -> str:
        return str(self._interval)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def inverted(self):
        return MotiveUnitInterval(
            -self._interval,
            self.original_work,
            self.original_position,
            PositionInWork.INVERTED,
        )

    def mirrored(self):
        return MotiveUnitInterval(
            self._interval,
            self.original_work,
            self.original_position,
            PositionInWork.MIRRORED,
        )


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


@dataclass
class MotivePosition:
    position: int
    length: int

    original_work: str
    original_position: int
    position_in_work: PositionInWork

    def __str__(self):
        return f"{self.position}:{self.length}:{self.original_position}:{self.position_in_work}"

    def __repr__(self):
        return f"{self.original_position}:{self.length}"

    def is_same_position(self, other: "MotivePosition") -> bool:
        if self.length != other.length:
            return False

        if self.original_work != other.original_work:
            return False

        if (
            self.position_in_work is PositionInWork.OUTSIDE
            or other.position_in_work is PositionInWork.OUTSIDE
        ):
            return False

        if self.position_in_work is PositionInWork.MIRRORED:
            if other.position_in_work is PositionInWork.MIRRORED:
                return self.original_position == other.original_position
            else:
                return (
                    self.original_position == other.original_position + other.length - 1
                )
        else:
            if other.position_in_work is PositionInWork.MIRRORED:
                return (
                    self.original_position + self.length - 1 == other.original_position
                )
            else:
                return self.original_position == other.original_position


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
    original_work: str

    @classmethod
    def parse_file(cls, file_path: Path, options: List[ParseOption]) -> "ParsedFile":
        def get_inverted(motive_units: List[MotiveUnit]) -> List[MotiveUnit]:
            if ParseOption.WITH_INVERTED in options:
                return UnitSequence(motive_units).inverted().sequence
            return []

        def get_mirrored(motive_units: List[MotiveUnit]) -> List[MotiveUnit]:
            if ParseOption.WITH_MIRRORED in options:
                return UnitSequence(motive_units).mirrored_and_inverted().sequence
            return []

        notes_and_rests = cls.get_notes(file_path)
        intervals_from_file = cls.get_motive_units(notes_and_rests, str(file_path))

        return cls(
            intervals_from_file,
            get_inverted(intervals_from_file),
            get_mirrored(intervals_from_file),
            notes_and_rests,
            str(file_path),
        )

    @staticmethod
    def get_notes(file_path: Path) -> StreamIterator[GeneralNote]:
        score = converter.parse(file_path)

        notes_and_rests = score.flatten().notesAndRests

        # remove accidentals, make this optional on useDiatonic
        for note_or_rest in notes_and_rests:
            if isinstance(note_or_rest, note.Note):
                note_or_rest.pitch.accidental = None

        return notes_and_rests

    @staticmethod
    def get_motive_units(
        notes_and_rests: StreamIterator[GeneralNote],
        work: str,
    ) -> List[MotiveUnit]:

        motive_units: List[MotiveUnit] = []
        for i in range(len(notes_and_rests) - 1):
            if isinstance(notes_and_rests[i], note.Note):
                if isinstance(notes_and_rests[i + 1], note.Note):
                    motive_units.append(
                        MotiveUnitInterval(
                            Interval(
                                notes_and_rests[i], notes_and_rests[i + 1]
                            ).generic.directed,
                            work,
                            i,
                        )
                    )
                else:
                    motive_units.append(MotiveUnitBreak("BreakTo", work, i))
            else:
                motive_units.append(MotiveUnitBreak("BreakFrom", work, i))
        return motive_units

    def get_all_motive_units(self, max_gap: int) -> List[MotiveUnit]:
        def get_breaks():
            return [
                MotiveUnitBreak("RestBetween", "noWork", -1, PositionInWork.OUTSIDE)
                for _ in range(max_gap)
            ]

        def add_with_breaks(motive_units: List[MotiveUnit]) -> List[MotiveUnit]:
            if len(motive_units) == 0:
                return []

            return get_breaks() + motive_units

        return (
            self.motive_units
            + add_with_breaks(self.motive_units_inverted)
            + add_with_breaks(self.motive_units_mirrored)
        )


@dataclass
class ParsedFiles:
    parsed_files: Dict[Path, ParsedFile]

    @classmethod
    def parse_files(
        cls, input_folder: Path, options: List[ParseOption]
    ) -> "ParsedFiles":
        is_xml = lambda file_path: file_path.suffix == ".xml"
        file_paths = [file for file in input_folder.iterdir() if is_xml(file)]

        parsed_files = {
            file_path: ParsedFile.parse_file(file_path, options)
            for file_path in file_paths
        }
        return cls(parsed_files)

    def get_all_motive_units(self, max_gap: int) -> List[MotiveUnit]:
        def get_breaks():
            return [
                MotiveUnitBreak("RestBetween", "noWork", -1, PositionInWork.OUTSIDE)
                for _ in range(max_gap)
            ]

        def add_with_breaks(motive_units: List[MotiveUnit]) -> List[MotiveUnit]:
            if len(motive_units) == 0:
                return []

            return get_breaks() + motive_units

        output = []
        for _, parsed_file in self.parsed_files.items():
            output = output + add_with_breaks(parsed_file.get_all_motive_units(max_gap))

        return output


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
            # and MotiveUnitBreak("RestFrom") not in motive.sequence
            # and MotiveUnitBreak("RestTo") not in motive.sequence
        ]


output_filename = "output.csv"
output_json_filename = "output.json"


def write_motives_as_json_to_file(motives: List[Motive], output_folder: Path):
    if not output_folder.exists():
        output_folder.mkdir()

    with open(output_folder / output_json_filename, "w") as file:
        instances_dict = [asdict(motive) for motive in motives]

        file.write(json.dumps(instances_dict, indent=4))


def write_motives_to_file(motives: List[Motive], output_folder: Path):

    if not output_folder.exists():
        output_folder.mkdir()

    with open(output_folder / output_filename, "w") as file:
        file.write(
            "work\tsequence\tfrequency\tpositions\tfrequency_original\tpositions_original\tfrequency_inverted\tpositions_inverted\tfrequency_mirrored\tposition_mirrored\n"
        )
        for motive in motives:
            original_positions = list(
                filter(
                    lambda pos: pos.position_in_work == PositionInWork.ORIGINAL,
                    motive.positions,
                )
            )

            # filter only positions which have PositionInWork.INVERTED
            inverted_positions = list(
                filter(
                    lambda pos: pos.position_in_work == PositionInWork.INVERTED,
                    motive.positions,
                )
            )
            # filter only positions which have PositionInWork.MIRRORED
            mirrored_positions = list(
                filter(
                    lambda pos: pos.position_in_work == PositionInWork.MIRRORED,
                    motive.positions,
                )
            )

            output: List[str] = []
            output.append(motive.sequence[0].original_work)
            output.append(str(motive.sequence))
            output.append(str(motive.frequency))
            output.append(str(motive.positions))
            output.append(str(len(original_positions)))
            output.append(str(original_positions))
            output.append(str(len(inverted_positions)))
            output.append(str(inverted_positions))
            output.append(str(len(mirrored_positions)))
            output.append(str(mirrored_positions))

            file.write("\t".join(output) + "\n")


def plot_motives(motives: List[Motive], parsed_files: ParsedFiles, output_folder: Path):
    def get_works() -> set[Path]:
        return set(parsed_files.parsed_files.keys())

    works = get_works()

    pass
