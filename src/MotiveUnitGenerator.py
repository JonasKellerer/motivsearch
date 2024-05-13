from dataclasses import dataclass
from typing import List

from music21 import note
from music21.interval import Interval

from Corpus import Corpus
from MotivePosition import PositionInWork
from MotiveUnit import (
    MotiveUnitBreak,
    MotiveUnit,
    MotiveUnitInterval,
    Origin,
    RestIntervalType,
)
from UnitSequence import UnitSequence
from Voice import Voice
from src.MainParser import ParseOption


@dataclass
class MotiveUnitGenerator:
    options: List[ParseOption]
    max_gap: int

    def from_corpus(self, corpus: Corpus):

        motive_units = []
        for piece in corpus.pieces:
            for part in piece.parts:
                for voice in part.voices:
                    units = self.including_inverted_and_mirrored(
                        voice, piece.title, part.id
                    )
                    motive_units += add_with_breaks(units, self.max_gap)

        return motive_units

    def including_inverted_and_mirrored(
        self, voice: Voice, piece_title: str, part_id: str
    ):
        original = self.original_from_voice(voice, piece_title, part_id)
        inverted = get_inverted(original, self.options)
        mirrored = get_mirrored(original, self.options)

        return (
            original
            + add_with_breaks(inverted, self.max_gap)
            + add_with_breaks(mirrored, self.max_gap)
        )

    def original_from_voice(
        self, voice: Voice, piece_title: str, part_id: str
    ) -> List[MotiveUnit]:

        motive_units: List[MotiveUnit] = []

        for i, note_or_rest in enumerate(voice.notes):
            if i == len(voice.notes) - 1:
                break

            origin = Origin(
                piece_title=piece_title,
                part_id=part_id,
                voice_id=voice.id,
                measure_number=note_or_rest.measureNumber,
                note_number=i,
            )

            if isinstance(note_or_rest, note.Note):
                if isinstance(voice.notes[i + 1], note.Note):
                    motive_units.append(
                        MotiveUnitInterval(
                            interval=Interval(
                                note_or_rest, voice.notes[i + 1]
                            ).generic.directed,
                            origin=origin,
                        )
                    )
                else:
                    motive_units.append(
                        MotiveUnitBreak(
                            type=RestIntervalType.NOTE_BEFORE, origin=origin
                        )
                    )
            else:
                if isinstance(voice.notes[i + 1], note.Note):
                    motive_units.append(
                        MotiveUnitBreak(type=RestIntervalType.NOTE_AFTER, origin=origin)
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
        for _ in range(max_gap + 1)
    ]


def add_with_breaks(motive_units: List[MotiveUnit], max_gap: int) -> List[MotiveUnit]:
    if len(motive_units) == 0:
        return []

    return get_breaks(max_gap) + motive_units
