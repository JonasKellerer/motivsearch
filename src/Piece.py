import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from music21 import converter

from ParseOptions import ParseOptions
from Part import Part


@dataclass
class Piece:
    title: str
    parts: List[Part]

    @classmethod
    def parse(cls, file: Path, options: Optional[ParseOptions] = None) -> "Piece":
        logging.info(f"Reading file {file}")
        score = converter.parse(file)

        logging.info(f"Extracting parts from {file}")
        parts = [Part.parse(part, options) for part in score.parts]
        title = file.stem

        return cls(title, parts)
