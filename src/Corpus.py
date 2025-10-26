import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from music21.note import Note

from ParseOptions import ParseOptions
from Piece import Piece


@dataclass
class Corpus:
    pieces: List[Piece]

    @classmethod
    def parse(
        cls, input_folder: Path, options: Optional[ParseOptions] = None
    ) -> "Corpus":
        logging.info(f"Reading folder {input_folder}")
        is_xml = (
            lambda file_path: file_path.suffix == ".xml"
            or file_path.suffix == ".musicxml"
        )
        file_paths = [file for file in input_folder.iterdir() if is_xml(file)]

        pieces = [Piece.parse(file, options) for file in file_paths]
        return cls(pieces)

    def remove_accidentals(self):
        logging.info("Removing accidentals from all pieces")
        for piece in self.pieces:
            for part in piece.parts:
                for voice in part.voices:
                    for note in voice.notes:
                        if isinstance(note, Note):
                            note.pitch.accidental = None
