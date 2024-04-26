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
from MotiveUnit import (
    MotiveUnitBreak,
    MotiveUnit,
    MotiveUnitInterval,
    Origin,
    RestIntervalType,
)
from UnitSequence import UnitSequence
from src.MainParser import ParseOption


@dataclass
class Voice:
    id: str
    notes: List[Note | Rest]

    def full_names(self) -> List[str]:
        return [note.fullName for note in self.notes]


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

    def remove_accidentals(self):
        for piece in self.pieces:
            for part in piece.parts:
                for voice in part.voices:
                    for note in voice.notes:
                        if isinstance(note, Note):
                            note.pitch.accidental = None


@dataclass
class MotiveUnitGenerator:
    options: List[ParseOption]
    max_gap: int

    def from_corpus(self, corpus: Corpus):

        motive_units = []
        for piece in corpus.pieces:
            for part in piece.parts:
                for voice in part.voices:
                    units = self.includingInvertedAndMirrored(
                        voice, piece.title, part.id
                    )
                    motive_units = add_with_breaks(units, self.max_gap)

        return motive_units

    def includingInvertedAndMirrored(
        self, voice: Voice, piece_title: str, part_id: str
    ):
        original = MotiveUnitGenerator.originalFromVoice(voice, piece_title, part_id)
        inverted = get_inverted(original, self.options)
        mirrored = get_mirrored(original, self.options)

        return (
            original
            + add_with_breaks(inverted, self.max_gap)
            + add_with_breaks(mirrored, self.max_gap)
        )

    def originalFromVoice(
        self, voice: Voice, piece_title: str, part_id: str
    ) -> List[MotiveUnit]:

        motive_units: List[MotiveUnit] = []

        for i, note_or_rest in enumerate(voice.notes):
            origin = Origin(
                piece_title,
                part_id,
                voice.id,
                note_or_rest.measureNumber,
                i,
            )

            if isinstance(note_or_rest, note.Note):
                if isinstance(voice.notes[i + 1], note.Note):
                    motive_units.append(
                        MotiveUnitInterval(
                            Interval(note_or_rest, voice.notes[i + 1]).generic.directed,
                            origin,
                        )
                    )
                else:
                    motive_units.append(
                        MotiveUnitBreak(RestIntervalType.NOTE_BEFORE, origin)
                    )
            else:
                if isinstance(voice.notes[i + 1], note.Note):
                    motive_units.append(
                        MotiveUnitBreak(RestIntervalType.NOTE_AFTER, origin)
                    )
                else:
                    motive_units.append(
                        MotiveUnitBreak(RestIntervalType.REST_BEFORE, origin)
                    )

        return motive_units


def get_inverted(
    motive_units: List[MotiveUnit], options: List[ParseOption]
) -> List[MotiveUnit]:
    if ParseOption.WITH_INVERTED in options:
        return UnitSequence(motive_units).inverted().sequence
    return []


def get_mirrored(
    motive_units: List[MotiveUnit], options: List[ParseOption]
) -> List[MotiveUnit]:
    if ParseOption.WITH_MIRRORED in options:
        return UnitSequence(motive_units).mirrored_and_inverted().sequence
    return []


def get_breaks(max_gap: int) -> List[MotiveUnit]:
    origin_outside = Origin("noWork", "noWork", "noWork", -1, -1)

    return [
        MotiveUnitBreak(
            RestIntervalType.DIVIDER, origin_outside, PositionInWork.OUTSIDE
        )
        for _ in range(max_gap)
    ]


def add_with_breaks(motive_units: List[MotiveUnit], max_gap: int) -> List[MotiveUnit]:
    if len(motive_units) == 0:
        return []

    return get_breaks(max_gap) + motive_units
