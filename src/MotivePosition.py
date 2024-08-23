from dataclasses import dataclass


@dataclass
class MotivePosition:
    position: int
    length: int

    def __str__(self):
        return f"{self.position}:{self.length}"

    def __repr__(self):
        return f"{self.position}:{self.length}"

    def __eq__(self, other: "MotivePosition") -> bool:
        return self.is_same_position(other)

    def is_same_position(self, other: "MotivePosition") -> bool:
        return self.position == other.position and self.length == other.length
