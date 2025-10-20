import logging
from dataclasses import dataclass
from operator import index
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
        parts = [Part.parse(part, unique_id=str(index), options=options) for index, part in enumerate(score.parts)]
        title = file.stem

        return cls(title, parts)
