from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Union

import music21
from music21 import converter, note
from music21.interval import Interval
from music21.note import GeneralNote
from music21.stream.iterator import StreamIterator


class ParseOption(Enum):
    WITH_INVERTED = 1
    WITH_MIRRORED = 2
    USE_DIATONIC = 3


class XmlReader:

    @staticmethod
    def get_intervals(
        notes_and_rests: StreamIterator[GeneralNote],
    ) -> List[Union[Interval, str]]:

        intervals: List[Union[Interval, str]] = []
        for i in range(len(notes_and_rests) - 1):
            if isinstance(notes_and_rests[i], note.Note):
                if isinstance(notes_and_rests[i + 1], note.Note):
                    intervals.append(
                        music21.interval.Interval(
                            notes_and_rests[i], notes_and_rests[i + 1]
                        )
                    )
                else:
                    intervals.append("BreakTo")
            else:
                intervals.append("BreakFrom")
        return intervals

    @staticmethod
    def get_notes(file_path: str) -> StreamIterator[GeneralNote]:
        score = converter.parse(file_path)

        notes_and_rests = score.flatten().notesAndRests

        # remove accidentals, make this optional on useDiatonic
        for note_or_rest in notes_and_rests:
            if isinstance(note_or_rest, note.Note):
                note_or_rest.pitch.accidental = None

        return notes_and_rests

    @staticmethod
    def get_motive_unit(interval: Union[Interval, str]) -> str:
        if isinstance(interval, str):
            return interval
        return str(interval.generic.directed)

    @staticmethod
    def parse_file(
        file_path: str, options: List[ParseOption], max_gap
    ) -> Tuple[List[Optional[Interval]], StreamIterator[GeneralNote]]:
        def get_inverted(intervals: List[Interval | str]) -> List[Interval | str]:
            inverted = []
            for interval in intervals:
                if isinstance(interval, str):
                    inverted.append(interval)
                else:
                    inverted.append(Interval(-interval.semitones))

            return inverted

        def get_mirrored(intervals: List[Interval | str]) -> List[Interval | str]:
            inverted = get_inverted(intervals).copy()
            return inverted[::-1]

        def get_breaks(max_gap: int) -> List[str]:
            return ["BreakBetween" for _ in range(max_gap + 1)]

        notes_and_rests = XmlReader.get_notes(file_path)

        intervals_from_file = XmlReader.get_intervals(notes_and_rests)

        output = intervals_from_file.copy()

        if ParseOption.WITH_INVERTED in options:
            output.extend(get_breaks(max_gap))
            output.extend(get_inverted(intervals_from_file))

        if ParseOption.WITH_MIRRORED in options:
            output.extend(get_breaks(max_gap))
            output.extend(get_mirrored(intervals_from_file))

        return output, notes_and_rests
