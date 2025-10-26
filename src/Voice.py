from dataclasses import dataclass
from typing import List

from music21.note import Note, Rest

from ParseOptions import RestTreatment


@dataclass
class Voice:
    id: str
    notes: List[Note | Rest]

    def full_names(self) -> List[str]:
        return [note.fullName for note in self.notes]

    def remove_rests(self, remove_options: RestTreatment = RestTreatment.NONE) -> None:
        quarter_length_limit = remove_options.quarter_length_to_remove()

        if quarter_length_limit is None:
            return
        self.notes = [
            element
            for element in self.notes
            if not isinstance(element, Rest)
            or element.duration.quarterLength > quarter_length_limit
        ]
