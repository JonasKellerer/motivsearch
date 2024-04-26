from dataclasses import dataclass
from typing import List

from music21.note import Note, Rest


@dataclass
class Voice:
    id: str
    notes: List[Note | Rest]

    def full_names(self) -> List[str]:
        return [note.fullName for note in self.notes]
