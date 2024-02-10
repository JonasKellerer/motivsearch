from music21 import converter, note
from typing import List

from music21.interval import Interval


class XmlReader:

    @staticmethod
    def get_intervals(file_path: str) -> List[str]:
        score = converter.parse(file_path)

        notes_and_rests = score.flat.notesAndRests

        intervals: List[str] = []
        for i in range(len(notes_and_rests) - 1):
            if isinstance(notes_and_rests[i], note.Note) and isinstance(notes_and_rests[i + 1], note.Note):
                interval = Interval(notes_and_rests[i + 1], notes_and_rests[i])
                intervals.append(interval.name)
            else:
                intervals.append("R")

        return intervals

