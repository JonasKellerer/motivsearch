import logging
from dataclasses import dataclass
from typing import List, Dict

from music21 import note
from music21.interval import Interval as m21Interval

from Corpus import Corpus
from Motive import Motive
from MotivePosition import MotivePosition
from Origin import Origin
from Voice import Voice
from GeneralInterval import Interval, RestIntervalType, BreakInterval


@dataclass
class MotiveUnitGenerator:
    @staticmethod
    def from_corpus(corpus: Corpus) -> Dict[str, Dict[str, Dict[str, list[Motive]]]]:
        logging.info("Generating motive units from corpus")
        motive_units: Dict[str, Dict[str, Dict[str, list[Motive]]]] = {}
        for piece in corpus.pieces:
            motive_units[piece.title] = {}
            for part in piece.parts:
                motive_units[piece.title][part.id] = {}
                for voice in part.voices:
                    motive_units[piece.title][part.id][voice.id] = (
                        MotiveUnitGenerator.original_from_voice(voice)
                    )

        return motive_units

    @staticmethod
    def original_from_voice(voice: Voice) -> List[Motive]:

        single_motives: List[Motive] = []

        for i, note_or_rest in enumerate(voice.notes):
            if i == len(voice.notes) - 1:
                break

            origin = Origin(
                measure_number=note_or_rest.measureNumber,
                note_number=i,
            )
            position = MotivePosition(
                position=i,
                length=1,
                origin=origin,
            )

            if isinstance(note_or_rest, note.Note):
                if isinstance(voice.notes[i + 1], note.Note):
                    m21_interval = m21Interval(
                        note_or_rest, voice.notes[i + 1]
                    ).generic.directed
                    sequence = [Interval(m21_interval)]

                    single_motives.append(
                        Motive(
                            sequence=sequence,
                            positions=[position],
                        )
                    )
                else:
                    sequence = [BreakInterval(type=RestIntervalType.NOTE_BEFORE)]
                    single_motives.append(
                        Motive(
                            sequence=sequence,
                            positions=[position],
                        )
                    )
            else:
                if isinstance(voice.notes[i + 1], note.Note):
                    sequence = [BreakInterval(type=RestIntervalType.NOTE_AFTER)]
                    single_motives.append(
                        Motive(
                            sequence=sequence,
                            positions=[position],
                        )
                    )
                else:
                    sequence = [BreakInterval(type=RestIntervalType.REST_BEFORE)]
                    single_motives.append(
                        Motive(sequence=sequence, positions=[position])
                    )

        return single_motives
