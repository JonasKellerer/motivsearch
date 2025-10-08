from dataclasses import dataclass
from enum import Enum

class AccidentalTreatment(Enum):
    NONE = 0
    REMOVE_ACCIDENTALS = 1

    @classmethod
    def from_string(cls, s: str) -> "AccidentalTreatment":
        lower_map = {member.name.lower(): member for member in cls}
        return lower_map.get(s.lower().replace('-', '_'))

class RestTreatment(Enum):
    NONE = 0
    REMOVE_EIGHTS_AND_LOWER = 1
    REMOVE_SIXTEENTH_AND_LOWER = 2

    def quarter_length_to_remove(self) -> None | float:
        if self is RestTreatment.REMOVE_SIXTEENTH_AND_LOWER:
            return 0.25
        elif self is RestTreatment.REMOVE_EIGHTS_AND_LOWER:
            return 0.5
        else:
            return None

    @classmethod
    def from_string(cls, s: str) -> "RestTreatment":
        lower_map = {member.name.lower(): member for member in cls}
        return lower_map.get(s.lower().replace('-', '_'))

class ChordTreatment(Enum):
    HIGHEST = 0
    LOWEST = 1
    REMOVE = 2

    @classmethod
    def from_string(cls, s: str) -> "ChordTreatment":
        lower_map = {member.name.lower(): member for member in cls}
        return lower_map.get(s.lower().replace('-', '_'))

@dataclass
class ParseOptions:
    rest_treatment: RestTreatment = RestTreatment.NONE
    chord_treatment: ChordTreatment = ChordTreatment.HIGHEST
    accidental_treatment: AccidentalTreatment = AccidentalTreatment.NONE
