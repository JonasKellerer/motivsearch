from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Origin:
    measure_number: int
    note_number: int
