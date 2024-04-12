from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from music21 import converter, note, stream, chord
from music21.interval import Interval
from music21.note import GeneralNote
from music21.stream.iterator import StreamIterator

from MotivePosition import PositionInWork
from MotiveUnit import MotiveUnitBreak, MotiveUnit, MotiveUnitInterval
from UnitSequence import UnitSequence
from src.MainParser import ParseOption


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

        new_score = ParsedFile.use_only_highest_notes_in_chord(score)

        ParsedFile.strip_ties(new_score)

        notes_and_rests = new_score.flatten().notesAndRests

        ParsedFile.remove_accidentals(notes_and_rests)

        return notes_and_rests

    @staticmethod
    def strip_ties(new_score):
        for part in new_score.parts:
            part.stripTies(inPlace=True)

    @staticmethod
    def remove_accidentals(notes_and_rests):
        for note_or_rest in notes_and_rests:
            if isinstance(note_or_rest, note.Note):
                note_or_rest.pitch.accidental = None

    @staticmethod
    def use_only_highest_notes_in_chord(score):
        new_score = stream.Score()
        for part in score.parts:
            new_part = stream.Part()

            for element in part.flatten():
                if isinstance(element, chord.Chord):
                    highest_note = element.sortAscending()[-1]
                    new_part.append(highest_note)
                else:
                    new_part.append(element)

            new_score.append(new_part)
        return new_score

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
        is_xml = (
            lambda file_path: file_path.suffix == ".xml"
            or file_path.suffix == ".musicxml"
        )
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
