import unittest
from pathlib import Path

from MainParser import ParseOption
from Motive import Motive
from MotiveGenerator import MotiveGenerator
from MotivePosition import MotivePosition
from Origin import Origin
from SequenceType import SequenceType


class MotiveGeneratorTest_DiscoverMotives(unittest.TestCase):
    options = [
        ParseOption.WITH_INVERTED,
        ParseOption.WITH_MIRRORED,
        ParseOption.USE_DIATONIC,
    ]

    def test_single_file(self):
        file_path = Path("testData/single_file/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 8)

        self.assertEqual(motives[0].frequency(), 6)
        self.assertEqual(motives[0].frequency(SequenceType.ORIGINAL), 5)
        self.assertEqual(motives[0].frequency(SequenceType.INVERTED), 1)
        self.assertEqual(motives[0].frequency(SequenceType.MIRRORED), 0)
        self.assertEqual(motives[0].frequency(SequenceType.MIRRORED_INVERTED), 0)
        self.assertEqual(
            motives[0].intervals.name(SequenceType.ORIGINAL), "['2', '2', '2']"
        )
        self.assertEqual(motives[1].frequency(), 2)
        self.assertEqual(
            motives[1].intervals.name(SequenceType.ORIGINAL), "['2', '2', '-3']"
        )
        self.assertEqual(motives[2].frequency(), 1)
        self.assertEqual(
            motives[2].intervals.name(SequenceType.ORIGINAL), "['2', '-3', '-4']"
        )
        self.assertEqual(motives[3].frequency(), 1)
        self.assertEqual(
            motives[3].intervals.name(SequenceType.ORIGINAL), "['2', '-3', '1']"
        )
        self.assertEqual(motives[4].frequency(), 1)
        self.assertEqual(
            motives[4].intervals.name(SequenceType.ORIGINAL), "['-3', '-4', '2']"
        )
        self.assertEqual(motives[5].frequency(), 1)
        self.assertEqual(
            motives[5].intervals.name(SequenceType.ORIGINAL), "['-3', '1', '-2']"
        )
        self.assertEqual(motives[6].frequency(), 1)
        self.assertEqual(
            motives[6].intervals.name(SequenceType.ORIGINAL), "['-4', '2', '2']"
        )
        self.assertEqual(motives[7].frequency(), 1)
        self.assertEqual(
            motives[7].intervals.name(SequenceType.ORIGINAL), "['1', '-2', '-2']"
        )

    def test_chromatic_variation(self):
        file_path = Path("testData/chromatic_variation/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 15)

    def test_mirrored(self):
        file_path = Path("testData/mirrored")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 1)

        self.assertEqual(motives[0].frequency(), 2)
        self.assertEqual(
            motives[0].intervals.name(SequenceType.ORIGINAL), "['1', '2', '4']"
        )

    def test_mirror_and_inverted_variation(self):
        file_path = Path("testData/mirror_and_inverted/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 13)

        expected_motives = [
            {"frequency": 2, "sequence": "['5', '-3', '-3']"},
            {"frequency": 1, "sequence": "['-3', '-3', '3']"},
            {"frequency": 1, "sequence": "['-3', '3', '-2']"},
            {"frequency": 4, "sequence": "['-3', '2', '2']"},
            {"frequency": 1, "sequence": "['3', '3', '4']"},
            {"frequency": 1, "sequence": "['3', '4', '1']"},
            {"frequency": 1, "sequence": "['-2', '-2', '-2']"},
            {"frequency": 1, "sequence": "['-2', '-2', '7']"},
            {"frequency": 1, "sequence": "['-2', '7', '-8']"},
            {"frequency": 1, "sequence": "['2', '2', '-5']"},
            {"frequency": 1, "sequence": "['2', '-5', '3']"},
            {"frequency": 1, "sequence": "['4', '1', '2']"},
            {"frequency": 1, "sequence": "['1', '2', '2']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_rhythm_variation(self):
        file_path = Path("testData/rythm_variation/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 11)

        self.assertEqual(motives[0].frequency(), 2)
        self.assertEqual(motives[3].frequency(), 2)
        self.assertEqual(motives[5].frequency(), 2)

    def test_basic(self):
        file_path = Path("testData/basic/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        self.assertEqual(motives[0].frequency(), 1)
        self.assertEqual(motives[1].frequency(), 1)

    def test_chromatic(self):
        file_path = Path("testData/chromatic/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 1)

        self.assertEqual(motives[0].frequency(), 2)

    def test_breaks(self):
        file_path = Path("testData/breaks/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 0)

    def test_multiple_parts(self):
        file_path = Path("testData/multiple_parts/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 4)

        expected_motives = [
            {"frequency": 1, "sequence": "['1', '2', '4']"},
            {"frequency": 1, "sequence": "['-3', '-2', '1']"},
            {"frequency": 1, "sequence": "['3', '-3', '3']"},
            {"frequency": 1, "sequence": "['-3', '3', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_multiple_voices_in_one_part(self):
        file_path = Path("testData/multiple_voices_in_one_part")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 4)

        expected_motives = [
            {"frequency": 1, "sequence": "['1', '1', '2']"},
            {"frequency": 1, "sequence": "['1', '2', '4']"},
            {"frequency": 1, "sequence": "['-3', '-2', '1']"},
            {"frequency": 1, "sequence": "['1', '1', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_multiple_parts_multiple_voices(self):
        file_path = Path("testData/multiple_parts_multiple_voices")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 6)

        expected_motives = [
            {"frequency": 1, "sequence": "['1', '1', '2']"},
            {"frequency": 1, "sequence": "['1', '2', '4']"},
            {"frequency": 1, "sequence": "['-3', '-2', '1']"},
            {"frequency": 1, "sequence": "['1', '1', '1']"},
            {"frequency": 1, "sequence": "['3', '-3', '3']"},
            {"frequency": 1, "sequence": "['-3', '3', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_one_accord_per_note(self):
        file_path = Path("testData/one_accord_per_note")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        expected_motives = [
            {"frequency": 1, "sequence": "['1', '2', '4']"},
            {"frequency": 1, "sequence": "['-3', '-2', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_ties(self):
        file_path = Path("testData/ties")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 1)

        expected_motives = [
            {"frequency": 1, "sequence": "['1', '2', '4']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_multiple_pieces_same_motives(self):
        file_path = Path("testData/multiple_pieces/same_motives")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        expected_motives = [
            {"frequency": 2, "sequence": "['1', '2', '4']"},
            {"frequency": 2, "sequence": "['-3', '-2', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_multiple_pieces_different_motives(self):
        file_path = Path("testData/multiple_pieces/different_motives")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 4)

        expected_motives = [
            {"frequency": 1, "sequence": "['4', '-3', '4']"},
            {"frequency": 1, "sequence": "['7', '-10', '1']"},
            {"frequency": 1, "sequence": "['1', '2', '4']"},
            {"frequency": 1, "sequence": "['-3', '-2', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_multiple_pieces_same_motive_in_inverted(self):
        file_path = Path("testData/multiple_pieces/same_motive_in_inverted")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        # welches stück auch immer zu erst eingelesen wird, das wird als original genommen?
        expected_motives = [
            {"frequency": 2, "sequence": "['1', '2', '4']"},
            {"frequency": 2, "sequence": "['3', '2', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_multiple_pieces_same_motive_in_mirrored(self):
        file_path = Path("testData/multiple_pieces/same_motive_in_mirrored")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        expected_motives = [
            {"frequency": 2, "sequence": "['1', '2', '4']"},
            {"frequency": 2, "sequence": "['1', '-2', '-3']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(
                motives[i].intervals.name(SequenceType.ORIGINAL),
                expected_motive["sequence"],
            )

    def test_multiple_pieces_same_motive_in_mirrored_and_inverted(self):
        file_path = Path(
            "testData/multiple_pieces/same_motive_in_mirrored_and_inverted"
        )

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        expected_motives = [
            {"frequency": 4, "sequence": "['1', '2', '4']"},
            {"frequency": 4, "sequence": "['-3', '-2', '1']"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency(), expected_motive["frequency"])
            self.assertEqual(motives[i].intervals.name(SequenceType.ORIGINAL), expected_motive["sequence"])
