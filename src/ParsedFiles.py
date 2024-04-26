import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from music21 import converter, note, stream, chord
from music21.interval import Interval
from music21.note import GeneralNote, Note, Rest
from music21.stream import Part as Part21
from music21.stream.iterator import StreamIterator

from MotivePosition import PositionInWork
from MotiveUnit import MotiveUnitBreak, MotiveUnit, MotiveUnitInterval
from UnitSequence import UnitSequence
from src.MainParser import ParseOption


@dataclass
class Voice:
    id: str
    notes: List[Note | Rest]


@dataclass
class Part:
    id: str
    voices: List[Voice]

    @classmethod
    def parse(cls, part: Part21) -> "Part":
        part.stripTies(inPlace=True)

        voices = extract_voices(part, extrac_voice_ids(part))
        return cls(part.id, voices)


def extract_voices(part: Part21, voice_ids: List[str]):
    part_data = {voice_id: [] for voice_id in voice_ids}

    for i, measure in enumerate(part.getElementsByClass(stream.Measure)):
        if len(measure.voices) == 0:
            for note in measure.notesAndRests:
                part_data[voice_ids[0]].append(use_only_highest_note(note))
            for voice in voice_ids[1:]:
                part_data[voice].append(
                    Rest(quarterLength=measure.barDuration.quarterLength)
                )

        for voice in measure.voices:
            for note in voice.notesAndRests:
                part_data[voice.id].append(use_only_highest_note(note))

    return [Voice(voice_id, part_data[voice_id]) for voice_id in voice_ids]


def extrac_voice_ids(part: Part21) -> List[str]:
    voice_ids = []
    for measure in part.getElementsByClass(stream.Measure):
        for voice in measure.getElementsByClass(stream.Voice):
            voice_ids.append(voice.id)
    if len(voice_ids) == 0:
        voice_ids.append("0")

    logging.debug(f"Voice ids: {voice_ids}")
    return voice_ids


def use_only_highest_note(note: GeneralNote) -> GeneralNote:
    if isinstance(note, chord.Chord):
        return note.sortAscending()[-1]
    return note


@dataclass
class Piece:
    title: str
    parts: List[Part]

    @classmethod
    def parse(cls, file: Path) -> "Piece":
        logging.info(f"Reading file {file}")
        score = converter.parse(file)

        parts = [Part.parse(part) for part in score.parts]

        return cls(str(file), parts)


@dataclass
class Corpus:
    pieces: List[Piece]

    @classmethod
    def parse(cls, input_folder: Path) -> "Corpus":
        logging.info(f"Reading folder {input_folder}")
        is_xml = (
            lambda file_path: file_path.suffix == ".xml"
            or file_path.suffix == ".musicxml"
        )
        file_paths = [file for file in input_folder.iterdir() if is_xml(file)]

        pieces = [Piece.parse(file) for file in file_paths]
        return cls(pieces)


def remove_accidentals(corpus: Corpus):
    for piece in corpus.pieces:
        for part in piece.parts:
            for voice in part.voices:
                for note in voice.notes:
                    if isinstance(note, Note):
                        note.pitch.accidental = None


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
