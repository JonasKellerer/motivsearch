from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Origin:
    piece_title: str
    part_id: str
    voice_id: str
    measure_number: int
    note_number: int
