from dataclasses import dataclass
from typing import List

from music21.note import GeneralNote
from music21.stream.iterator import StreamIterator

from Motive import Motive
from MotivePosition import MotivePosition


@dataclass
class MotiveList:
    motives: List[Motive]
    notes: StreamIterator[GeneralNote]

    def get_inverse_positions(self) -> List[MotivePosition]:
        pass
