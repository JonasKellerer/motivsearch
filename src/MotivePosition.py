from dataclasses import dataclass

from Origin import Origin


@dataclass
class MotivePosition:
    position: int
    length: int

    origin: Origin

    def __str__(self):
        return f"{self.position}:{self.length}:{self.origin}"

    def __repr__(self):
        return f"{self.origin.note_number}:{self.length}"

    def __eq__(self, other: "MotivePosition") -> bool:
        return self.is_same_position(other)

    def is_same_position(self, other: "MotivePosition") -> bool:
        if self.length != other.length:
            return False

        if self.origin != other.origin:
            return False

        if self.position != other.position:
            return False

        return True
