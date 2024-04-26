import logging
import unittest
from pathlib import Path

from music21.note import Note

from ParsedFiles import Piece


class PieceTest(unittest.TestCase):
    def test_should_parse_multiple_voices(self):
        filename = "testData/parsing/basic/multiple_voices_in_one_part.musicxml"
        piece = Piece.parse(file=Path(filename))

        self.assertEqual(piece.title, filename)

        notesOfFirstVoice = [
            "C in octave 4 Quarter Note",
            "C in octave 4 Eighth Note",
            "C in octave 4 Eighth Note",
            "D in octave 4 Quarter Note",
            "G in octave 4 Quarter Note",
            "Quarter Rest",
            "F in octave 4 Quarter Note",
            "D in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
        ]

        notesOfSecondVoice = [
            "D in octave 3 Eighth Note",
            "D in octave 3 Eighth Note",
            "D in octave 3 Eighth Note",
            "D in octave 3 Eighth Note",
            "Half Rest",
            "Whole Rest",
            "Whole Rest",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notesOfFirstVoice,
        )
        self.assertListEqual(
            piece.parts[0].voices[1].full_names(),
            notesOfSecondVoice,
        )

    def test_should_parse_multiple_parts(self):
        filename = "testData/parsing/basic/multiple_parts.musicxml"
        piece = Piece.parse(file=Path(filename))

        self.assertEqual(piece.title, filename)

        notesOfFirstPart = [
            "C in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
            "D in octave 4 Quarter Note",
            "G in octave 4 Quarter Note",
            "Quarter Rest",
            "F in octave 4 Quarter Note",
            "D in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
        ]

        notesOfSecondPart = [
            "B in octave 4 Quarter Note",
            "D in octave 5 Quarter Note",
            "B in octave 4 Quarter Note",
            "D in octave 5 Quarter Note",
            "D in octave 5 Quarter Note",
            "Quarter Rest",
            "A in octave 4 Quarter Note",
            "C in octave 5 Quarter Note",
            "C in octave 5 Quarter Note",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notesOfFirstPart,
        )
        self.assertListEqual(
            piece.parts[1].voices[0].full_names(),
            notesOfSecondPart,
        )

    def test_should_parse_multiple_parts_with_multiple_voices(self):
        filename = "testData/parsing/basic/multiple_parts_multiple_voices.musicxml"
        piece = Piece.parse(file=Path(filename))

        self.assertEqual(piece.title, filename)

        notesOfFirstVoice = [
            "C in octave 4 Quarter Note",
            "C in octave 4 Eighth Note",
            "C in octave 4 Eighth Note",
            "D in octave 4 Quarter Note",
            "G in octave 4 Quarter Note",
            "Quarter Rest",
            "F in octave 4 Quarter Note",
            "D in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
        ]

        notesOfSecondVoice = [
            "D in octave 3 Eighth Note",
            "D in octave 3 Eighth Note",
            "D in octave 3 Eighth Note",
            "D in octave 3 Eighth Note",
            "Half Rest",
            "Whole Rest",
            "Whole Rest",
        ]

        notesOfSecondPart = [
            "B in octave 4 Quarter Note",
            "D in octave 5 Quarter Note",
            "B in octave 4 Quarter Note",
            "D in octave 5 Quarter Note",
            "D in octave 5 Quarter Note",
            "Quarter Rest",
            "A in octave 4 Quarter Note",
            "C in octave 5 Quarter Note",
            "C in octave 5 Quarter Note",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notesOfFirstVoice,
        )
        self.assertListEqual(
            piece.parts[0].voices[1].full_names(),
            notesOfSecondVoice,
        )
        self.assertListEqual(
            piece.parts[1].voices[0].full_names(),
            notesOfSecondPart,
        )

    def test_should_only_use_highest_note_in_chord(self):
        filename = "testData/parsing/basic/one_accord_per_note.musicxml"
        piece = Piece.parse(file=Path(filename))

        self.assertEqual(piece.title, filename)

        notesOfFirstVoice = [
            "C in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
            "D in octave 4 Quarter Note",
            "G in octave 4 Quarter Note",
            "Quarter Rest",
            "F in octave 4 Quarter Note",
            "D in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
            "C in octave 4 Quarter Note",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notesOfFirstVoice,
        )

    def test_should_strip_ties(self):
        filename = "testData/parsing/basic/ties.musicxml"
        piece = Piece.parse(file=Path(filename))

        self.assertEqual(piece.title, filename)

        notesOfFirstVoice = [
            "C in octave 4 Half Note",
            "D in octave 4 Quarter Note",
            "G in octave 4 Quarter Note",
            "Quarter Rest",
            "F in octave 4 Quarter Note",
            "D in octave 4 Quarter Note",
            "C in octave 4 Half Note",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notesOfFirstVoice,
        )


if __name__ == "__main__":
    unittest.main()
