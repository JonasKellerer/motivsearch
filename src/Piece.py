import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from music21 import converter

from Part import Part


@dataclass
class Piece:
    title: str
    parts: List[Part]

    @classmethod
    def parse(cls, file: Path) -> "Piece":
        logging.info(f"Reading file {file}")
        score = converter.parse(file)

        parts = [Part.parse(part) for part in score.parts]

        return cls(str(file), parts)
