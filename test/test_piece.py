import unittest
from pathlib import Path

from ParseOptions import ParseOptions, ChordTreatment, RestTreatment
from Piece import Piece


class PieceTest(unittest.TestCase):
    def test_should_parse_multiple_voices(self):
        filename = "testData/parsing/basic/multiple_voices_in_one_part.musicxml"
        piece = Piece.parse(file=Path(filename))

        self.assertEqual(piece.title, "multiple_voices_in_one_part")

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

        self.assertEqual(piece.title, "multiple_parts")

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

        self.assertEqual(piece.title, "multiple_parts_multiple_voices")

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

        self.assertEqual(piece.title, "one_accord_per_note")

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

        self.assertEqual(piece.title, "ties")

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

    def test_should_remove_rests_shorter_than_eights(self):
        filename = "testData/parsing/basic/remove_rests.musicxml"
        parse_options = ParseOptions(
            rest_treatment=RestTreatment.REMOVE_EIGHTS_AND_LOWER
        )
        piece = Piece.parse(file=Path(filename), options=parse_options)

        notes_without_short_rests = [
            "C in octave 4 Quarter Note",
            "Half Rest",
            "B in octave 3 Quarter Note",
            "Half Rest",
            "Half Rest",
            "C in octave 4 Quarter Note",
            "Quarter Rest",
            "D in octave 4 Quarter Note",
            "Quarter Rest",
            "Quarter Rest",
            "B in octave 3 Quarter Note",
            "C in octave 4 Eighth Note",
            "C in octave 4 16th Note",
            "B in octave 3 16th Note",
            "C in octave 4 32nd Note",
            "B in octave 3 32nd Note",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notes_without_short_rests,
        )

    def test_should_remove_rests_shorter_than_sixteenth(self):
        filename = "testData/parsing/basic/remove_rests.musicxml"
        parse_options = ParseOptions(
            rest_treatment=RestTreatment.REMOVE_SIXTEENTH_AND_LOWER
        )
        piece = Piece.parse(file=Path(filename), options=parse_options)

        notes_without_short_rests = [
            "C in octave 4 Quarter Note",
            "Half Rest",
            "B in octave 3 Quarter Note",
            "Half Rest",
            "Half Rest",
            "C in octave 4 Quarter Note",
            "Quarter Rest",
            "D in octave 4 Quarter Note",
            "Quarter Rest",
            "Quarter Rest",
            "B in octave 3 Quarter Note",
            "Eighth Rest",
            "C in octave 4 Eighth Note",
            "Eighth Rest",
            "Eighth Rest",
            "C in octave 4 16th Note",
            "B in octave 3 16th Note",
            "C in octave 4 32nd Note",
            "B in octave 3 32nd Note",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notes_without_short_rests,
        )

    def test_should_use_lowest_note_in_chord(self):
        filename = "testData/parsing/basic/chord_treatment.musicxml"
        parse_options = ParseOptions(chord_treatment=ChordTreatment.LOWEST)
        piece = Piece.parse(file=Path(filename), options=parse_options)

        notes_without_short_rests = [
            "C in octave 4 Quarter Note",
            "F in octave 4 Quarter Note",
            "E in octave 4 Quarter Note",
            "B in octave 3 Quarter Note",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notes_without_short_rests,
        )

    def test_should_remove_chords(self):
        filename = "testData/parsing/basic/chord_treatment.musicxml"
        parse_options = ParseOptions(chord_treatment=ChordTreatment.REMOVE)
        piece = Piece.parse(file=Path(filename), options=parse_options)

        notes_without_short_rests = [
            "Quarter Rest",
            "F in octave 4 Quarter Note",
            "E in octave 4 Quarter Note",
            "Quarter Rest",
        ]

        self.assertListEqual(
            piece.parts[0].voices[0].full_names(),
            notes_without_short_rests,
        )


if __name__ == "__main__":
    unittest.main()
