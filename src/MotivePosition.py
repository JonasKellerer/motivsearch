from pydantic import BaseModel


class MotivePosition(BaseModel):
    position: int
    length: int

    def __str__(self) -> str:
        return f"{self.position}:{self.length}"

    def __repr__(self) -> str:
        return f"{self.position}:{self.length}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MotivePosition):
            return self.is_same_position(other)
        return NotImplemented

    def is_same_position(self, other: "MotivePosition") -> bool:
        return self.position == other.position and self.length == other.length
